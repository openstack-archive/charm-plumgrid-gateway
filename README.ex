# Overview

This charm is responsible for configuring a node as a PLUMgrid Gateway.

Once deployed the charm triggers the necessary services for a PLUMgrid Gateway and configures the IO Visor kernel module as a PLUMgrid Software Gateway. It also configures additional interfaces on the node for external connectivity.

# Usage

Step by step instructions on using the charm:

    juju deploy neutron-api
    juju deploy neutron-api-plumgrid
    juju deploy plumgrid-director
    juju deploy nova-compute
    juju deploy plumgrid-edge
    juju deploy plumgrid-gateway

    juju add-relation neutron-api neutron-api-plumgrid
    juju add-relation neutron-api-plumgrid plumgrid-director
    juju add-relation plumgrid-director plumgrid-edge
    juju add-relation nova-compute plumgrid-edge
    juju add-relation plumgrid-director plumgrid-gateway

For plumgrid-gateway to work make the configuration in the neutron-api, neutron-api-plumgrid, plumgrid-director and plumgrid-edge charms as specified in the configuration section below.

## Known Limitations and Issues

This is an early access version of the PLUMgrid Gateway charm and it is not meant for production deployments. The charm currently only supports Kilo Openstack Release.

# Configuration

Example Config

    plumgrid-gateway:
        external-interface: eth1
        install_sources: 'ppa:plumgrid-team/stable'
        install_keys: 'null'
    plumgrid-edge:
        install_sources: 'ppa:plumgrid-team/stable'
        install_keys: 'null'
    plumgrid-director:
        plumgrid-virtual-ip: "192.168.100.250"
        install_sources: 'ppa:plumgrid-team/stable'
        install_keys: 'null'
    neutron-api-plumgrid:
        install_sources: 'ppa:plumgrid-team/stable'
        install_keys: 'null'
        enable-metadata: False
    neutron-api:
        neutron-plugin: "plumgrid"
        plumgrid-virtual-ip: "192.168.100.250"

The "external-interface" config parameter should be the interface that will provide external connectivity. 
Provide the source repo path for PLUMgrid Debs in 'install_sources' and the corresponding keys in 'install_keys'.
The virtual IP passed on in the neutron-api charm has to be same as the one passed in the plumgrid-director charm.

# Contact Information

Bilal Baqar <bbaqar@plumgrid.com>
Bilal Ahmad <bilal@plumgrid.com>
