from mock import MagicMock, patch, call
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
    'remove_iovisor',
    'apt_install',
    'CONFIGS',
    'log',
    'configure_sources',
    'ensure_files',
    'stop_pg',
    'load_iovisor',
    'ensure_mtu',
    'add_lcm_key',
    'determine_packages',
    'load_iptables',
    'director_cluster_ready',
    'status_set',
    'configure_analyst_opsvm'
]
NEUTRON_CONF_DIR = "/etc/neutron"

NEUTRON_CONF = '%s/neutron.conf' % NEUTRON_CONF_DIR


class PGGwHooksTests(CharmTestCase):

    def setUp(self):
        super(PGGwHooksTests, self).setUp(hooks, TO_PATCH)
        # self.config.side_effect = self.test_config.get
        hooks.hooks._config_save = False

    def _call_hook(self, hookname):
        hooks.hooks.execute([
            'hooks/{}'.format(hookname)])

    def test_install_hook(self):
        _pkgs = ['plumgrid-lxc', 'iovisor-dkms']
        self.determine_packages.return_value = [_pkgs]
        self._call_hook('install')
        self.configure_sources.assert_called_with(update=True)
        self.apt_install.assert_has_calls([
            call(_pkgs, fatal=True,
                 options=['--force-yes']),
        ])
        self.load_iovisor.assert_called_with()
        self.ensure_mtu.assert_called_with()
        self.ensure_files.assert_called_with()
        self.add_lcm_key.assert_called_with()

    def test_plumgrid_changed(self):
        self._call_hook('plumgrid-relation-changed')
        self.director_cluster_ready.return_value = True
        self.ensure_mtu.assert_called_with()
        self.CONFIGS.write_all.assert_called_with()

    def test_stop(self):
        self._call_hook('stop')
        self.stop_pg.assert_called_with()
