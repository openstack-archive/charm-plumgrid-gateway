# Copyright (c) 2015, PLUMgrid Inc, http://plumgrid.com

# This file contains the class that generates context for PLUMgrid template files.

from charmhelpers.core.hookenv import (
    relation_ids,
    related_units,
    relation_get,
    config,
)
from charmhelpers.contrib.openstack import context

from socket import gethostname as get_unit_hostname


def _pg_dir_settings():
    '''
    Inspects relation with PLUMgrid director.
    '''
    pg_settings = {
        'pg_dir_ip': '192.168.100.201',
    }
    for rid in relation_ids('plumgrid'):
        for unit in related_units(rid):
            rdata = relation_get(rid=rid, unit=unit)
            pg_settings = {
                'pg_dir_ip': rdata['private-address'],
            }
    return pg_settings


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
        Generated Config for all PLUMgrid templates inside the templates folder.
        '''
        pg_ctxt = super(PGGwContext, self).pg_ctxt()
        if not pg_ctxt:
            return {}

        conf = config()
        pg_dir_settings = _pg_dir_settings()
        pg_ctxt['local_ip'] = pg_dir_settings['pg_dir_ip']

        unit_hostname = get_unit_hostname()
        pg_ctxt['pg_hostname'] = unit_hostname
        pg_ctxt['interface'] = "juju-br0"
        pg_ctxt['label'] = unit_hostname
        pg_ctxt['fabric_mode'] = 'host'

        pg_ctxt['ext_interface'] = conf['external-interface']

        return pg_ctxt
