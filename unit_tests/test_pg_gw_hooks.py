from mock import MagicMock, patch

from test_utils import CharmTestCase

with patch('charmhelpers.core.hookenv.config') as config:
    config.return_value = 'neutron'
    import pg_gw_utils as utils

_reg = utils.register_configs
_map = utils.restart_map

utils.register_configs = MagicMock()
utils.restart_map = MagicMock()

import pg_gw_hooks as hooks

utils.register_configs = _reg
utils.restart_map = _map

TO_PATCH = [
    #'apt_update',
    #'apt_install',
    #'apt_purge',
    #'config',
    'CONFIGS',
    #'determine_packages',
    #'determine_dvr_packages',
    #'get_shared_secret',
    #'git_install',
    'log',
    #'relation_ids',
    #'relation_set',
    #'configure_ovs',
    #'use_dvr',
    'ensure_files',
    'stop_pg',
    'restart_pg',
]
NEUTRON_CONF_DIR = "/etc/neutron"

NEUTRON_CONF = '%s/neutron.conf' % NEUTRON_CONF_DIR


class PGGwHooksTests(CharmTestCase):

    def setUp(self):
        super(PGGwHooksTests, self).setUp(hooks, TO_PATCH)

        #self.config.side_effect = self.test_config.get
        hooks.hooks._config_save = False

    def _call_hook(self, hookname):
        hooks.hooks.execute([
            'hooks/{}'.format(hookname)])

    def test_install_hook(self):
        self._call_hook('install')
        self.ensure_files.assert_called_with()

    def test_plumgrid_edge_joined(self):
        self._call_hook('plumgrid-plugin-relation-joined')
        self.ensure_files.assert_called_with()
        self.CONFIGS.write_all.assert_called_with()
        self.restart_pg.assert_called_with()

    def test_stop(self):
        self._call_hook('stop')
        self.stop_pg.assert_called_with()
