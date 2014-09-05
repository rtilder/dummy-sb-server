#!/bin/bash
#set -x
#set -e

ALLTOGETHER=alldomains.txt
COUNTED=counted.txt
DOMAIN_LISTS="tmp_out/tpl/abine/domains.txt \
              tmp_out/tpl/privacychoice/domains.txt \
              tmp_out/tpl/truste/domains.txt \
              tmp_out/disconnect/domains.txt"

rm -f $ALLTOGETHER
rm -f $ALLTOGETHER.sorted
rm -f $COUNTED
rm -f $COUNTED.cut
rm -f $ALLTOGETHER.csv

# All the lists in one big list
for i in $DOMAIN_LISTS
do
  cat $i >> $ALLTOGETHER
done

sort $ALLTOGETHER | uniq > $ALLTOGETHER.sorted

# substrings will match here, so wc $COUNTED > sorted uniqed $COUNTED
#for i in `head $ALLTOGETHER.sorted`
for i in `cat $ALLTOGETHER.sorted`
do
  DISCONNECT=`grep $i tmp_out/disconnect/domains.txt | wc -l`
  ABINE=`grep $i tmp_out/tpl/abine/domains.txt | wc -l`
  PRIVACYCHOICE=`grep $i tmp_out/tpl/privacychoice/domains.txt | wc -l`
  TRUSTE=`grep $i tmp_out/tpl/truste/domains.txt | wc -l`
  echo $i,$DISCONNECT,$ABINE,$PRIVACYCHOICE,$TRUSTE >> $ALLTOGETHER.csv
done

#sort $COUNTED | uniq | cut -f1 -d: > $COUNTED.cut
#
#echo "total: `wc $ALLTOGETHER.sorted`"
#echo "hits: `wc $COUNTED.cut`"
#echo "disconnect: `grep disconnect $COUNTED.cut | wc`"
#echo "abine: `grep abine $COUNTED.cut | wc`"
#echo "privacychoice: `grep privacychoice $COUNTED.cut | wc`"
#echo "truste: `grep truste $COUNTED.cut | wc`"
