# Copyright (c) 2015, PLUMgrid Inc, http://plumgrid.com

# This file contains the class that generates context for
# PLUMgrid template files.

from charmhelpers.contrib.openstack import context
from charmhelpers.contrib.openstack.utils import get_host_ip
from charmhelpers.core.hookenv import (
    relation_ids,
    related_units,
    relation_get,
)
from socket import (
    gethostname,
    getfqdn
)


def _pg_dir_context():
    '''
    Inspects relation with PLUMgrid director.
    '''
    ctxt = {
        'opsvm_ip': '127.0.0.1',
        'director_ips': [],
    }
    for rid in relation_ids('plumgrid'):
        for unit in related_units(rid):
            rdata = relation_get(rid=rid, unit=unit)
            ctxt['director_ips'
                 ].append(str(get_host_ip(rdata['private-address'])))
            if "opsvm_ip" in rdata:
                ctxt['opsvm_ip'] = \
                    rdata['opsvm_ip']
    return ctxt


class PGGwContext(context.NeutronContext):

    @property
    def plugin(self):
        '''
        Over-riding function in NeutronContext Class to return 'plumgrid'
        as the neutron plugin.
        '''
        return 'plumgrid'

    @property
    def network_manager(self):
        '''
        Over-riding function in NeutronContext Class to return 'neutron'
        as the network manager.
        '''
        return 'neutron'

    def _save_flag_file(self):
        '''
        Over-riding function in NeutronContext Class.
        Function only needed for OVS.
        '''
        pass

    def pg_ctxt(self):
        '''
        Generated Config for all PLUMgrid templates inside the
        templates folder.
        '''
        pg_ctxt = super(PGGwContext, self).pg_ctxt()
        if not pg_ctxt:
            return {}

        pg_dir_context = _pg_dir_context()
        pg_dir_ips = sorted(pg_dir_context['director_ips'])
        dir_count = len(pg_dir_ips)
        pg_ctxt['director_ips_string'] = (str(pg_dir_ips[0]) + ',' +
                                          str(pg_dir_ips[1]) + ',' +
                                          str(pg_dir_ips[2])
                                          if dir_count == 3 else
                                          str(pg_dir_ips[0])
                                          if dir_count == 1 else
                                          '')
        unit_hostname = gethostname()
        pg_ctxt['pg_hostname'] = unit_hostname
        pg_ctxt['pg_fqdn'] = getfqdn()
        from pg_gw_utils import (
            get_mgmt_interface,
            get_gw_interfaces,
            get_fabric_interface
        )
        pg_ctxt['interface'] = get_mgmt_interface()
        pg_ctxt['fabric_interface'] = get_fabric_interface()
        pg_ctxt['label'] = unit_hostname
        pg_ctxt['fabric_mode'] = 'host'
        pg_ctxt['ext_interfaces'] = get_gw_interfaces()
        pg_ctxt['opsvm_ip'] = pg_dir_context['opsvm_ip']

        return pg_ctxt
