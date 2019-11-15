#!/bin/bash

if [ $# -le 0 ]; then
    echo "usage: $0 [1,2,3]"
    exit 1
fi

NUM=$(($1-1))

DPIDS=(1 2 3)
IPS=("10.10.1.1/24" "10.10.2.1/24" "10.10.3.1/24")

sudo apt-get install curl gnupg apt-transport-https lsb-release
echo "deb https://packagecloud.io/faucetsdn/faucet/$(lsb_release -si | awk '{print tolower($0)}')/ $(lsb_release -sc) main" \
    | sudo tee /etc/apt/sources.list.d/faucet.list
curl -L https://packagecloud.io/faucetsdn/faucet/gpgkey | sudo apt-key add -

sudo apt-get update
sudo apt-get install openvswitch-switch

# replace datapath-id with an ID for your router! 1,2,3, etc.
sudo ovs-vsctl add-br br0 \
     -- set bridge br0 other-config:datapath-id=000000000000000${DPIDS[$NUM]} \
     -- set bridge br0 other-config:disable-in-band=true \
     -- set bridge br0 fail_mode=secure \
     -- add-port br0 eth1 -- set interface eth1 ofport_request=1 \
     -- add-port br0 eth2 -- set interface eth2 ofport_request=2 \
     -- add-port br0 eth3 -- set interface eth3 ofport_request=3 \
     -- add-port br0 eth4 -- set interface eth4 ofport_request=4 \

# enable the OVS bridge
sudo ip addr add dev br0 ${IPS[$NUM]}
sudo ip link set br0 up
