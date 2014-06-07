#!/bin/bash

l=$1;
d=$2;
s=$3;

if [ "$l" == "" ] || [ "$d" == "" ] || [ "$s" == "" ]; then
  echo "Usage: $0 log dbg safebrowsing-file"
  exit
fi

# check first entry

# text to sha256 hash in hex representation
egrep "^\[m\]" $l | head -n 1 | awk '{print $4}' | tr -d '\n' \
| openssl dgst -sha256

# sha256 hash in hex representation as computed by the tool
head -n 2 $d | tail -n 1;

# sha256 hash as computed by the tool in hex representation
hash_bytes=`head -n 1 $s | awk -F \: '{print $3}'`
tail -c ${hash_bytes} $s | head -c 32 | xxd -p | tr -d '\n'

echo ""
