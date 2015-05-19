from charmhelpers.contrib.openstack.neutron import neutron_plugin_attribute
from copy import deepcopy
from charmhelpers.core.hookenv import log
from charmhelpers.core.host import (
    write_file,
)
from charmhelpers.contrib.openstack import templating
from collections import OrderedDict
from charmhelpers.contrib.openstack.utils import (
    os_release,
)
import pg_gw_context
import subprocess
import time

#Dont need these right now
NOVA_CONF_DIR = "/etc/nova"
NEUTRON_CONF_DIR = "/etc/neutron"
NEUTRON_CONF = '%s/neutron.conf' % NEUTRON_CONF_DIR
NEUTRON_DEFAULT = '/etc/default/neutron-server'

#Puppet Files
P_PGKA_CONF = '/opt/pg/etc/puppet/modules/sal/templates/keepalived.conf.erb'
P_PG_CONF = '/opt/pg/etc/puppet/modules/plumgrid/templates/plumgrid.conf.erb'
P_PGDEF_CONF = '/opt/pg/etc/puppet/modules/sal/templates/default.conf.erb'

#Plumgrid Files
PGKA_CONF = '/var/lib/libvirt/filesystems/plumgrid/etc/keepalived/keepalived.conf'
PG_CONF = '/var/lib/libvirt/filesystems/plumgrid/opt/pg/etc/plumgrid.conf'
PGDEF_CONF = '/var/lib/libvirt/filesystems/plumgrid/opt/pg/sal/nginx/conf.d/default.conf'
PGHN_CONF = '/var/lib/libvirt/filesystems/plumgrid-data/conf/etc/hostname'
PGHS_CONF = '/var/lib/libvirt/filesystems/plumgrid-data/conf/etc/hosts'
PGIFCS_CONF = '/var/lib/libvirt/filesystems/plumgrid-data/conf/pg/ifcs.conf'
IFCTL_CONF = '/var/run/plumgrid/lxc/ifc_list_gateway'
IFCTL_P_CONF = '/var/lib/libvirt/filesystems/plumgrid/var/run/plumgrid/lxc/ifc_list_gateway'

#EDGE SPECIFIC
SUDOERS_CONF = '/etc/sudoers.d/ifc_ctl_sudoers'
FILTERS_CONF_DIR = '/etc/nova/rootwrap.d'
FILTERS_CONF = '%s/network.filters' % FILTERS_CONF_DIR

BASE_RESOURCE_MAP = OrderedDict([
    (PG_CONF, {
        'services': ['plumgrid'],
        'contexts': [pg_gw_context.PGGwContext()],
    }),
    (PGHN_CONF, {
        'services': ['plumgrid'],
        'contexts': [pg_gw_context.PGGwContext()],
    }),
    (PGHS_CONF, {
        'services': ['plumgrid'],
        'contexts': [pg_gw_context.PGGwContext()],
    }),
    (PGIFCS_CONF, {
        'services': [],
        'contexts': [pg_gw_context.PGGwContext()],
    }),
    (FILTERS_CONF, {
        'services': [],
        'contexts': [pg_gw_context.PGGwContext()],
    }),
])

TEMPLATES = 'templates/'


def determine_packages():
    return neutron_plugin_attribute('plumgrid', 'packages', 'neutron')


def register_configs(release=None):
    release = release or os_release('neutron-common', base='icehouse')
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
    return {k: v['services'] for k, v in resource_map().iteritems()}


def ensure_files():
    _exec_cmd(cmd=['cp', '--remove-destination', '-f', P_PG_CONF, PG_CONF])
    write_file(SUDOERS_CONF, "\nnova ALL=(root) NOPASSWD: /opt/pg/bin/ifc_ctl_pp *\n", owner='root', group='root', perms=0o644)
    _exec_cmd(cmd=['mkdir', '-p', FILTERS_CONF_DIR])
    _exec_cmd(cmd=['touch', FILTERS_CONF])


def restart_pg():
    _exec_cmd(cmd=['virsh', '-c', 'lxc:', 'destroy', 'plumgrid'], error_msg='ERROR Destroying PLUMgrid')
    _exec_cmd(cmd=['rm', IFCTL_CONF, IFCTL_P_CONF], error_msg='ERROR Removing ifc_ctl_gateway file')
    _exec_cmd(cmd=['iptables', '-F'])
    _exec_cmd(cmd=['virsh', '-c', 'lxc:', 'start', 'plumgrid'], error_msg='ERROR Starting PLUMgrid')
    time.sleep(5)
    _exec_cmd(cmd=['service', 'plumgrid', 'start'], error_msg='ERROR starting PLUMgrid service')
    time.sleep(5)


def stop_pg():
    _exec_cmd(cmd=['virsh', '-c', 'lxc:', 'destroy', 'plumgrid'], error_msg='ERROR Destroying PLUMgrid')
    time.sleep(2)
    _exec_cmd(cmd=['rm', IFCTL_CONF, IFCTL_P_CONF], error_msg='ERROR Removing ifc_ctl_gateway file')


def _exec_cmd(cmd=None, error_msg='Command exited with ERRORs'):
    if cmd is None:
        log("NO command")
    else:
        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError, e:
            log(error_msg)
