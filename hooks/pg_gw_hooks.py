#!/usr/bin/python

# Copyright (c) 2015, PLUMgrid Inc, http://plumgrid.com

# The hooks of this charm have been symlinked to functions
# in this file.

import sys
from charmhelpers.core.host import service_running
from charmhelpers.core.hookenv import (
    Hooks,
    UnregisteredHookError,
    log,
    config,
    status_set
)

from charmhelpers.fetch import (
    apt_install,
    configure_sources,
)

from pg_gw_utils import (
    register_configs,
    ensure_files,
    restart_map,
    stop_pg,
    determine_packages,
    load_iovisor,
    remove_iovisor,
    ensure_mtu,
    add_lcm_key,
    fabric_interface_changed,
    load_iptables,
    restart_on_change,
    restart_on_stop,
    director_cluster_ready,
    configure_pg_sources
)

hooks = Hooks()
CONFIGS = register_configs()


@hooks.hook()
def install():
    '''
    Install hook is run when the charm is first deployed on a node.
    '''
    status_set('maintenance', 'Executing pre-install')
    load_iptables()
    configure_sources(update=True)
    status_set('maintenance', 'Installing apt packages')
    pkgs = determine_packages()
    for pkg in pkgs:
        apt_install(pkg, options=['--force-yes'], fatal=True)
    load_iovisor()
    ensure_mtu()
    ensure_files()
    add_lcm_key()


@hooks.hook('plumgrid-relation-changed')
@restart_on_change(restart_map())
def plumgrid_changed():
    '''
    This hook is run when relation between plumgrid-gateway and
    plumgrid-director is made.
    '''
    if director_cluster_ready():
        ensure_mtu()
        CONFIGS.write_all()


@hooks.hook('config-changed')
@restart_on_stop()
@restart_on_change(restart_map())
def config_changed():
    '''
    This hook is run when a config parameter is changed.
    It also runs on node reboot.
    '''
    charm_config = config()
    if charm_config.changed('lcm-ssh-key'):
        if add_lcm_key():
            log("PLUMgrid LCM Key added")
    if charm_config.changed('fabric-interfaces'):
        if not fabric_interface_changed():
            log("Fabric interface already set")
    if (charm_config.changed('install_sources') or
        charm_config.changed('plumgrid-build') or
        charm_config.changed('install_keys') or
            charm_config.changed('iovisor-build')):
        stop_pg()
        status_set('maintenance', 'Upgrading apt packages')
        if charm_config.changed('install_sources'):
            if not configure_pg_sources():
                log('IOError: /etc/apt/sources.list couldn\'t be updated')
        configure_sources(update=True)
        pkgs = determine_packages()
        for pkg in pkgs:
            apt_install(pkg, options=['--force-yes'], fatal=True)
            remove_iovisor()
            load_iovisor()
    ensure_mtu()
    CONFIGS.write_all()


@hooks.hook('upgrade-charm')
@restart_on_change(restart_map())
def upgrade_charm():
    ensure_mtu()
    CONFIGS.write_all()


@hooks.hook('stop')
def stop():
    '''
    This hook is run when the charm is destroyed.
    '''
    stop_pg()


@hooks.hook('update-status')
def update_status():
    if service_running('plumgrid'):
        status_set('active', 'Unit is ready')
    else:
        status_set('blocked', 'plumgrid service not running')


def main():
    try:
        hooks.execute(sys.argv)
    except UnregisteredHookError as e:
        log('Unknown hook {} - skipping.'.format(e))


if __name__ == '__main__':
    main()
