#!/bin/bash

# add -f to run ssh in background, parallellize
SSH="ssh -o StrictHostKeyChecking=no"

# Illinois
RTR1="hc50@pc2.instageni.illinois.edu -p 26811"

# Cornell
RTR2="hc50@pc1.geni.it.cornell.edu -p 30212"

# UCLA
RTR3="hc50@pc1.instageni.idre.ucla.edu -p 28612"

RTRS=("$RTR1" "$RTR2" "$RTR3")

# rtr2:eth4 < 10.10.102.2 - 10.10.102.3 > rtr3:eth3
$SSH $RTR1 "sudo ip r del 10.10.1.0/24; \
              sudo ip r add 10.10.1.0/24 via 10.10.100.3;"

$SSH $RTR2 "sudo ip r del 10.10.0.0/24; \
              sudo ip r add 10.10.0.0/24 via 10.10.102.3;"


              