# Overview

This charm provides the PLUMgrid Gateway configuration for a node.


# Usage

To deploy (partial deployment of linked charms only):

    juju deploy neutron-api
    juju deploy neutron-iovisor
    juju deploy plumgrid-director
    juju deploy plumgrid-gateway
    juju add-relation plumgrid-gateway neutron-iovisor
    juju add-relation plumgrid-gateway plumgrid-director

