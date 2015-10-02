# Copyright (c) 2015, PLUMgrid Inc, http://plumgrid.com

# This file contains functions used by the hooks to deploy PLUMgrid Gateway.

from charmhelpers.contrib.openstack.neutron import neutron_plugin_attribute
from copy import deepcopy
from charmhelpers.core.hookenv import (
    log,
    config,
    unit_get
)
from charmhelpers.contrib.network.ip import (
    get_iface_from_addr,
    get_bridges,
    get_bridge_nics,
)
from charmhelpers.core.host import (
    write_file,
    service_start,
    service_stop,
)
from charmhelpers.fetch import (
    apt_cache
)
from charmhelpers.contrib.storage.linux.ceph import modprobe
from charmhelpers.core.host import set_nic_mtu
from charmhelpers.contrib.openstack import templating
from collections import OrderedDict
from charmhelpers.contrib.openstack.utils import (
    os_release,
)
from socket import gethostname as get_unit_hostname
import pg_gw_context
import subprocess
import time
import os
import json

LXC_CONF = "/etc/libvirt/lxc.conf"
TEMPLATES = 'templates/'
PG_LXC_DATA_PATH = '/var/lib/libvirt/filesystems/plumgrid-data'

PG_CONF = '%s/conf/pg/plumgrid.conf' % PG_LXC_DATA_PATH
PG_HN_CONF = '%s/conf/etc/hostname' % PG_LXC_DATA_PATH
PG_HS_CONF = '%s/conf/etc/hosts' % PG_LXC_DATA_PATH
PG_IFCS_CONF = '%s/conf/pg/ifcs.conf' % PG_LXC_DATA_PATH
AUTH_KEY_PATH = '%s/root/.ssh/authorized_keys' % PG_LXC_DATA_PATH
IFC_LIST_GW = '/var/run/plumgrid/lxc/ifc_list_gateway'

SUDOERS_CONF = '/etc/sudoers.d/ifc_ctl_sudoers'

BASE_RESOURCE_MAP = OrderedDict([
    (PG_CONF, {
        'services': ['plumgrid'],
        'contexts': [pg_gw_context.PGGwContext()],
    }),
    (PG_HN_CONF, {
        'services': ['plumgrid'],
        'contexts': [pg_gw_context.PGGwContext()],
    }),
    (PG_HS_CONF, {
        'services': ['plumgrid'],
        'contexts': [pg_gw_context.PGGwContext()],
    }),
    (PG_IFCS_CONF, {
        'services': [],
        'contexts': [pg_gw_context.PGGwContext()],
    }),
])


def determine_packages():
    '''
    Returns list of packages required by PLUMgrid Gateway as specified
    in the neutron_plugins dictionary in charmhelpers.
    '''
    pkgs = []
    tag = 'latest'
    for pkg in neutron_plugin_attribute('plumgrid', 'packages', 'neutron'):
        if 'plumgrid' in pkg:
            tag = config('plumgrid-build')
        elif pkg == 'iovisor-dkms':
            tag = config('iovisor-build')

        if tag == 'latest':
            pkgs.append(pkg)
        else:
            if tag in [i.ver_str for i in apt_cache()[pkg].version_list]:
                pkgs.append('%s=%s' % (pkg, tag))
            else:
                error_msg = \
                    "Build version '%s' for package '%s' not available" \
                    % (tag, pkg)
                raise ValueError(error_msg)
    return pkgs


def register_configs(release=None):
    '''
    Returns an object of the Openstack Tempating Class which contains the
    the context required for all templates of this charm.
    '''
    release = release or os_release('nova-compute', base='kilo')
    configs = templating.OSConfigRenderer(templates_dir=TEMPLATES,
                                          openstack_release=release)
    for cfg, rscs in resource_map().iteritems():
        configs.register(cfg, rscs['contexts'])
    return configs


def resource_map():
    '''
    Dynamically generate a map of resources that will be managed for a single
    hook execution.
    '''
    resource_map = deepcopy(BASE_RESOURCE_MAP)
    return resource_map


def restart_map():
    '''
    Constructs a restart map based on charm config settings and relation
    state.
    '''
    return {cfg: rscs['services'] for cfg, rscs in resource_map().iteritems()}


def ensure_files():
    '''
    Ensures PLUMgrid specific files exist before templates are written.
    '''
    write_file(SUDOERS_CONF,
               "\nnova ALL=(root) NOPASSWD: /opt/pg/bin/ifc_ctl_pp *\n",
               owner='root', group='root', perms=0o644)
    _exec_cmd(cmd=['rm', '-f', IFC_LIST_GW])


def restart_pg():
    '''
    Stops and Starts PLUMgrid service after flushing iptables.
    '''
    service_stop('plumgrid')
    time.sleep(2)
    _exec_cmd(cmd=['iptables', '-F'])
    service_start('plumgrid')
    time.sleep(5)


def stop_pg():
    '''
    Stops PLUMgrid service.
    '''
    service_stop('plumgrid')
    time.sleep(2)


def load_iovisor():
    '''
    Loads iovisor kernel module.
    '''
    modprobe('iovisor')


def remove_iovisor():
    '''
    Removes iovisor kernel module.
    '''
    _exec_cmd(cmd=['rmmod', 'iovisor'],
              error_msg='Error Loading Iovisor Kernel Module')


def get_mgmt_interface():
    '''
    Returns the managment interface.
    '''
    def interface_exists(interface):
        '''
        Checks if interface exists on node.
        '''
        try:
            subprocess.check_call(['ip', 'link', 'show', interface],
                                  stdout=open(os.devnull, 'w'),
                                  stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            return False
        return True

    mgmt_interface = config('mgmt-interface')
    if interface_exists(mgmt_interface):
        return mgmt_interface
    else:
        log('Provided managment interface %s does not exist'
            % mgmt_interface)
        return get_iface_from_addr(unit_get('private-address'))


def get_gw_interfaces():
    '''
    Gateway node can have multiple interfaces. This function parses json
    provided in config to get all gateway interfaces for this node.
    '''
    node_interfaces = ['eth1']
    try:
        all_interfaces = json.loads(config('external-interfaces'))
    except ValueError:
        log("Invalid JSON")
        return node_interfaces
    hostname = get_unit_hostname()
    if hostname in all_interfaces:
        node_interfaces = all_interfaces[hostname].split(',')
    return node_interfaces


def ensure_mtu():
    '''
    Ensures required MTU of the underlying networking of the node.
    '''
    interface_mtu = config('network-device-mtu')
    mgmt_interface = get_mgmt_interface()
    if mgmt_interface in get_bridges():
        attached_interfaces = get_bridge_nics(mgmt_interface)
        for interface in attached_interfaces:
            set_nic_mtu(interface, interface_mtu)
    set_nic_mtu(mgmt_interface, interface_mtu)


def _exec_cmd(cmd=None, error_msg='Command exited with ERRORs', fatal=False):
    '''
    Function to execute any bash command on the node.
    '''
    if cmd is None:
        log("No command specified")
    else:
        if fatal:
            subprocess.check_call(cmd)
        else:
            try:
                subprocess.check_call(cmd)
            except subprocess.CalledProcessError:
                log(error_msg)


def add_lcm_key():
    '''
    Adds public key of PLUMgrid-lcm to authorized keys of PLUMgrid Gateway.
    '''
    key = config('lcm-ssh-key')
    if key == 'null':
        log('lcm key not specified')
        return 0
    file_write_type = 'w+'
    if os.path.isfile(AUTH_KEY_PATH):
        file_write_type = 'a'
        try:
            fr = open(AUTH_KEY_PATH, 'r')
        except IOError:
            log('plumgrid-lxc not installed yet')
            return 0
        for line in fr:
            if key in line:
                log('key already added')
                return 0
    try:
        fa = open(AUTH_KEY_PATH, file_write_type)
    except IOError:
        log('Error opening file to append')
        return 0
    fa.write(key)
    fa.write('\n')
    fa.close()
    return 1
