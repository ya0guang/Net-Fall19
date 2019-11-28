#!/bin/bash

# add -f to run ssh in background, parallellize
SSH="ssh -o StrictHostKeyChecking=no"

# update these entries to match your username and allocated resources!
# Illinois
RTR1="hc50@pc2.instageni.illinois.edu -p 26811"
NODE11="hc50@pc1.instageni.illinois.edu -p 26810"
NODE12="hc50@pc2.instageni.illinois.edu -p 26810"

# Cornell
RTR2="hc50@pc1.geni.it.cornell.edu -p 30212"
NODE21="hc50@pc1.geni.it.cornell.edu -p 30210"
NODE22="hc50@pc1.geni.it.cornell.edu -p 30211"

# UCLA
RTR3="hc50@pc1.instageni.idre.ucla.edu -p 28612"
NODE31="hc50@pc1.instageni.idre.ucla.edu -p 28611"
NODE32="hc50@pc1.instageni.idre.ucla.edu -p 28610"

ALL_NODES=("$RTR1" "$RTR2" "$RTR3"
	   "$NODE11" "$NODE12"
	   "$NODE21" "$NODE22"
	   "$NODE31" "$NODE32")

RTRS=("$RTR1" "$RTR2" "$RTR3")
 
HOSTS=("$NODE11" "$NODE12"
       "$NODE21" "$NODE22"
       "$NODE31" "$NODE32")

# Run commands below
# For example, this clears all IPs from dataplane interfaces
# and resets /etc/hosts

# NOTE: build a map of which ethX interfaces connect to each other
# before flushing!

# e.g.
# rtr1:eth3 < 10.10.100.1 - 10.10.100.3 > rtr3:eth4
# rtr1:eth4 < 10.10.101.1 - 10.10.101.2 > rtr2:eth3
# rtr2:eth4 < 10.10.102.2 - 10.10.102.3 > rtr3:eth3
for h in "${RTRS[@]}"; do
    $SSH $h "hostname; sudo ip addr flush dev eth1; \
    	    	       sudo ip addr flush dev eth2; \
		       sudo ip addr flush dev eth3; \
		       sudo ip addr flush dev eth4; \
		       head -n 1 /etc/hosts | sudo tee /etc/hosts;"
done

for h in "${HOSTS[@]}"; do
    $SSH $h "hostname; sudo ip addr flush dev eth1; \
    	     head -n 1 /etc/hosts | sudo tee /etc/hosts"
done

# Next step: assign desired IPs to each site hosts and routers
# Update /etc/hosts if desired

$SSH $NODE11 "hostname; sudo ip addr add 10.10.0.11/24 dev eth1; \
				sudo ip route add 10.10.0.0/16 via 10.10.0.1;"
$SSH $NODE12 "hostname; sudo ip addr add 10.10.0.12/24 dev eth1; \
				sudo ip route add 10.10.0.0/16 via 10.10.0.1;"

$SSH $NODE21 "hostname; sudo ip addr add 10.10.1.21/24 dev eth1; \
				sudo ip route add 10.10.0.0/16 via 10.10.1.1;"
$SSH $NODE22 "hostname; sudo ip addr add 10.10.1.22/24 dev eth1; \
				sudo ip route add 10.10.0.0/16 via 10.10.1.1;"

$SSH $NODE31 "hostname; sudo ip addr add 192.168.0.31/24 dev eth1; \
				sudo ip route add 192.168.0.0/24 via 192.168.0.1; \
				sudo ip route add 10.10.0.0/16 via 192.168.0.1;"
$SSH $NODE32 "hostname; sudo ip addr add 192.168.0.32/24 dev eth1; \
				sudo ip route add 192.168.0.0/24 via 192.168.0.1; \
				sudo ip route add 10.10.0.0/16 via 192.168.0.1;"


$SSH $RTR1 "hostname; sudo ip addr add 10.10.0.1/24 dev eth1; \
		      sudo ip addr add 10.10.100.1/24 dev eth3; \
		      sudo ip addr add 10.10.101.1/24 dev eth4; \
			  sudo ip route add 10.10.1.0/24 via 10.10.101.2; \
			  sudo ip route add 192.168.0.0/24 via 10.10.100.3; \
			  echo '127.0.0.1       localhost loghost localhost.hc50.ch-geni-net.instageni.illinois.edu' | sudo tee /etc/hosts; \
			  echo '10.10.101.2 router2 router2.hc50.ch-geni-net.geni.it.cornell.edu' | sudo tee -a /etc/hosts; \
			  echo '10.10.100.3 router3 router3.hc50.ch-geni-net.instageni.idre.ucla.edu' | sudo tee -a /etc/hosts;"


$SSH $RTR2 "hostname; sudo ip addr add 10.10.1.1/24 dev eth1; \
		      sudo ip addr add 10.10.101.2/24 dev eth3; \
		      sudo ip addr add 10.10.102.2/24 dev eth4; \
			  sudo ip route add 10.10.0.0/24 via 10.10.101.1; \
			  sudo ip route add 192.168.0.0/24 via 10.10.102.3; \
			  echo '127.0.0.1       localhost loghost localhost.hc50.ch-geni-net.geni.it.cornell.edu' | sudo tee /etc/hosts; \
			  echo '10.10.101.1 router1 router1.hc50.ch-geni-net.instageni.illinois.edu' | sudo tee -a /etc/hosts; \
			  echo '10.10.102.3 router3 router3.hc50.ch-geni-net.instageni.idre.ucla.edu' | sudo tee -a /etc/hosts;"

$SSH $RTR3 "hostname; sudo ip addr add 192.168.0.1/24 dev eth1; \
		      sudo ip addr add 10.10.100.3/24 dev eth3; \
		      sudo ip addr add 10.10.102.3/24 dev eth4; \
			  sudo ip route add 10.10.0.0/24 via 10.10.100.1; \
			  sudo ip route add 10.10.1.0/24 via 10.10.102.2; \
			  echo '127.0.0.1       localhost loghost localhost.hc50.ch-geni-net.instageni.idre.ucla.edu' | sudo tee /etc/hosts; \
			  echo '10.10.100.1 router1 router1.hc50.ch-geni-net.instageni.illinois.edu' | sudo tee -a /etc/hosts; \
			  echo '10.10.102.2 router2 router2.hc50.ch-geni-net.geni.it.cornell.edu' | sudo tee -a /etc/hosts; \
			  sudo iptables -t nat -A POSTROUTING -s 10.10.0.0/24 -o eth3 -j MASQUERADE; \
			  sudo iptables -t nat -A POSTROUTING -s 10.10.1.0/24 -o eth4 -j MASQUERADE; \
			  sudo iptables -t nat -A PREROUTING -p tcp --dport 12345 -j DNAT --to 192.168.0.32;"

# Then: add static routes on the routers and hosts to enable
# connectivity

# ...

