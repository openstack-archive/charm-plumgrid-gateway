# About the Plumgrid Platform

The PLUMgrid Platform is a software-only solution that provides a rich set of distributed network functions such as routers, switches, NAT, IPAM, DHCP, and it also supports security policies, end-to-end encryption, and third party Layer 4-7 service insertion.

# Overview

This charm is responsible for configuring a node as a PLUMgrid Gateway.

Once deployed the charm triggers the necessary services for a PLUMgrid Gateway and configures the IO Visor kernel module as a PLUMgrid Software Gateway. It also configures additional interfaces on the node for external connectivity.

# Usage

Instructions on using the charm:

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

This charm currently doesn't support Ubuntu 16.04.

# Configuration

Example Config

    plumgrid-gateway:
        external-interfaces: '{"node01":"eth5,eth2","node02":"eth4,eth8"}'
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

The "external-interfaces" config parameter should be the interfaces that will provide external connectivity on each of the gateway nodes. Should be provided as a json in a string with hostname and interface names.
Provide the source repo path for PLUMgrid Debs in 'install_sources' and the corresponding keys in 'install_keys'.
The virtual IP passed on in the neutron-api charm has to be same as the one passed in the plumgrid-director charm.

# Contact Information

Bilal Baqar <bbaqar@plumgrid.com>
Javeria Khan <javeriak@plumgrid.com>
Junaid Ali <junaidali@plumgrid.com>
