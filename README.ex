# Overview

This charm is responsible for configuring a node as a PLUMgrid Gateway.

Once deployed the charm triggers the necessary services for a PLUMgrid Gateway and configures the IO Visor kernel module as a PLUMgrid Software Gateway. It also configures additional interfaces on the node for external connectivity.

# Usage

Step by step instructions on using the charm:

    juju deploy neutron-api
    juju deploy neutron-plumgrid-plugin neutron-api
    juju deploy neutron-iovisor
    juju deploy plumgrid-director --to <Machince No of neutron-iovisor>
    juju add-unit neutron-iovisor
    juju deploy plumgrid-edge --to <Machice No of 2nd unit of neutron-iovisor>
    juju add-unit neutron-iovisor
    juju deploy plumgrid-gateway --to <Machice No of 3rd unit of neutron-iovisor>

    juju add-relation neutron-api neutron-plumgrid-plugin
    juju add-relation neutron-plumgrid-plugin neutron-iovisor
    juju add-relation neutron-iovisor plumgrid-director
    juju add-relation neutron-iovisor plumgrid-edge
    juju add-relation neutron-iovisor plumgrid-gateway
    juju add-relation plumgrid-director plumgrid-edge
    juju add-relation plumgrid-director plumgrid-gateway

For plumgrid-gateway to work make the configuration in the neutron-api, neutron-plumgrid-plugin, neutron-iovisor, plumgrid-director and plumgrid-edge charms as specified in the configuration section below.

## Known Limitations and Issues

This is an early access version of the PLUMgrid Gateway charm and it is not meant for production deployments. The charm currently only supports JUNO. This charm needs to be deployed on a node where a unit of neutron-iovisor charm exists. Also plumgrid-director and plumgrid-edge charms should not be deployed on the same node.

# Configuration

plumgrid-edge charm does not require any configuration itself but the following config is required in the other charms.

Example Config

    plumgrid-gateway:
        external-interface: eth1
    plumgrid-director:
        plumgrid-virtual-ip: "192.168.100.250"
    neutron-iovisor:
        install_sources: 'ppa:plumgrid-team/stable'
        install_keys: 'null'
    neutron-plumgrid-plugin:
        install_sources: 'ppa:plumgrid-team/stable'
        install_keys: 'null'
        enable-metadata: False
    neutron-api:
        neutron-plugin: "plumgrid"
        plumgrid-virtual-ip: "192.168.100.250"

The "external-interface" config parameter should be the interface that will provide external connectivity. 

The virtual IP passed on in the neutron-api charm has to be same as the one passed in the plumgrid-director charm.

# Contact Information

Bilal Baqar <bbaqar@plumgrid.com>
Bilal Ahmad <bilal@plumgrid.com>
