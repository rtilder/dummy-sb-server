#!/bin/bash  

NODEBIN=`which node 2> /dev/null || echo /home/ec2-user/local/bin/node`

sudo ${NODEBIN} index.js $@
