#!/usr/bin/python

import sys

from charmhelpers.core.hookenv import (
    Hooks,
    UnregisteredHookError,
    log,
)

from pg_gw_utils import (
    register_configs,
    ensure_files,
    restart_pg,
    stop_pg,
)

hooks = Hooks()
CONFIGS = register_configs()


@hooks.hook()
def install():
    ensure_files()


@hooks.hook('plumgrid-plugin-relation-joined')
def plumgrid_dir():
    ensure_files()
    CONFIGS.write_all()
    restart_pg()


@hooks.hook('stop')
def stop():
    stop_pg()


def main():
    try:
        hooks.execute(sys.argv)
    except UnregisteredHookError as e:
        log('Unknown hook {} - skipping.'.format(e))


if __name__ == '__main__':
    main()
