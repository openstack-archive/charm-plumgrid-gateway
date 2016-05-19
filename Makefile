#!/usr/bin/make
PYTHON := /usr/bin/env python

virtualenv:
	virtualenv .venv
	.venv/bin/pip install flake8 nose coverage mock pyyaml netifaces \
        netaddr jinja2 pyflakes pep8 six pbr funcsigs psutil

lint: virtualenv
	.venv/bin/flake8 --exclude hooks/charmhelpers hooks unit_tests tests --ignore E402
	@charm proof

unit_test: virtualenv
	@echo Starting tests...
	@.venv/bin/nosetests --nologcapture  --with-coverage unit_tests

bin/charm_helpers_sync.py:
	@mkdir -p bin
	@bzr cat lp:charm-helpers/tools/charm_helpers_sync/charm_helpers_sync.py \
        > bin/charm_helpers_sync.py

sync: bin/charm_helpers_sync.py
	@$(PYTHON) bin/charm_helpers_sync.py -c charm-helpers-sync.yaml

publish: lint unit_test
	bzr push lp:charms/plumgrid-gateway
	bzr push lp:charms/trusty/plumgrid-gateway

test:
	@echo Starting Amulet tests...
	@juju test -v -p AMULET_HTTP_PROXY,AMULET_OS_VIP --timeout 2700
