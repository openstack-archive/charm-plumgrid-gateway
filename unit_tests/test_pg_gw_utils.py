from mock import MagicMock
from collections import OrderedDict
import charmhelpers.contrib.openstack.templating as templating

templating.OSConfigRenderer = MagicMock()

import pg_gw_utils as nutils

from test_utils import (
    CharmTestCase,
)
import charmhelpers.core.hookenv as hookenv


TO_PATCH = [
    'os_release',
    'neutron_plugin_attribute',
]


class DummyContext():

    def __init__(self, return_value):
        self.return_value = return_value

    def __call__(self):
        return self.return_value


class TestPGGwUtils(CharmTestCase):

    def setUp(self):
        super(TestPGGwUtils, self).setUp(nutils, TO_PATCH)
        #self.config.side_effect = self.test_config.get

    def tearDown(self):
        # Reset cached cache
        hookenv.cache = {}

    def test_register_configs(self):
        class _mock_OSConfigRenderer():
            def __init__(self, templates_dir=None, openstack_release=None):
                self.configs = []
                self.ctxts = []

            def register(self, config, ctxt):
                self.configs.append(config)
                self.ctxts.append(ctxt)

        self.os_release.return_value = 'trusty'
        templating.OSConfigRenderer.side_effect = _mock_OSConfigRenderer
        _regconfs = nutils.register_configs()
        confs = ['/var/lib/libvirt/filesystems/plumgrid/opt/pg/etc/plumgrid.conf',
                 '/var/lib/libvirt/filesystems/plumgrid-data/conf/etc/hostname',
                 '/var/lib/libvirt/filesystems/plumgrid-data/conf/etc/hosts',
                 '/var/lib/libvirt/filesystems/plumgrid-data/conf/pg/ifcs.conf',
                 '/etc/nova/rootwrap.d/network.filters']
        self.assertItemsEqual(_regconfs.configs, confs)

    def test_resource_map(self):
        _map = nutils.resource_map()
        svcs = ['plumgrid']
        confs = [nutils.PG_CONF]
        [self.assertIn(q_conf, _map.keys()) for q_conf in confs]
        self.assertEqual(_map[nutils.PG_CONF]['services'], svcs)

    def test_restart_map(self):
        _restart_map = nutils.restart_map()
        expect = OrderedDict([
            (nutils.PG_CONF, ['plumgrid']),
            (nutils.PGHN_CONF, ['plumgrid']),
            (nutils.PGHS_CONF, ['plumgrid']),
            (nutils.PGIFCS_CONF, []),
            (nutils.FILTERS_CONF, []),
        ])
        self.assertEqual(expect, _restart_map)
        for item in _restart_map:
            self.assertTrue(item in _restart_map)
            self.assertTrue(expect[item] == _restart_map[item])
