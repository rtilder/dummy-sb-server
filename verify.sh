#!/bin/bash

# log file (log)
l=$1;
# debug file (.dbg)
d=$2;
# actual file in safebrowsing format 
s=$3;

if [ "$l" == "" ] || [ "$d" == "" ] || [ "$s" == "" ]; then
  echo "Usage: $0 log dbg safebrowsing-file"
  exit
fi

if [ ! -e "$l" ] || [ ! -e "$d" ] || [ ! -e "$s" ]; then
  echo "ERROR! One or more of the specified files could not be found."
  exit
fi

IFS=$'\n';

line_count=0;

# iterate through the matching entries in the log file
for entry in `egrep "^\[m\]" $l | egrep -v " DUP\$" | awk '{print $4}'`; do

  let line_count=line_count+1;

  # 1. extract parsed domain (in human test form) from the log file
  domain=`echo -n $entry | tr -d '\n'`

  # calculate sha256 of parsed domain
  domain_sha256=`echo -n $domain | openssl dgst -sha256`

  # 2. get corresponding line from dbg file
  # this is a sha256 hash of the parsed domain in hex as computed by the tool
  domain_computed_sha256_hex=`head -n $((1+${line_count})) $d | tail -n 1`;

  # 3. get corresponding line from actual safebrowsing file
  # this is a sha256 hash of the parsed domain as computed by the tool. 
  # we convert it to hex.

  # figure out how many bytes is the hash payload (entire file minus the header)
  hash_bytes=`head -n 1 $s | awk -F \: '{print $4}'`

  domain_computed_sha256=`tail -c $((${hash_bytes}-$((32*$((${line_count}-1)))))) $s | head -c 32 | xxd -p | tr -d '\n'`

  error=0;

  if [ "${domain_sha256}" != "${domain_computed_sha256_hex}" ]; then
    error=1;
  fi

  if [ "${domain_sha256}" != "${domain_computed_sha256}" ]; then
    error=1;
  fi

  if [ "$error" == "1" ]; then
    echo "#${line_count} MISMATCH"
    echo "'${domain}'"
    echo "'${domain_sha256}'"
    echo "'${domain_computed_sha256_hex}'"
    echo "'${domain_computed_sha256}'"
    exit -1
  fi

done

echo "Processed ${line_count} entries"
