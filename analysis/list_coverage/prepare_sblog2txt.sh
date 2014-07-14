#!/bin/bash

# generate mozpub.txt and mozpubmini.txt domain lists
# from .log file output of lists2safebrowsing.py

if [ -e ../../tmp_out/mozpub-track-digest256.log ]; then
  echo "* generating mozpub.txt"
  egrep "^\[m" ../../tmp_out/mozpub-track-digest256.log \
    | egrep -v " DUP$" \
    | awk -F \> '{print $3}' | sed s/" RANK_.*$"/""/g \
    | sed s/"^[ ]*"/""/g > mozpub.txt
else
  echo "* missing mozpub-track-digest256.log (mozpub.txt)"
fi

if [ -e ../../tmp_out/mozpubmini-track-digest256.log ]; then
  echo "* generating mozpubmini.txt"
  egrep "^\[m" ../../tmp_out/mozpubmini-track-digest256.log \
    | egrep -v " DUP$" \
    | awk -F \> '{print $3}' | sed s/" RANK_.*$"/""/g \
    | sed s/"^[ ]*"/""/g > mozpubmini.txt
else
  echo "* missing mozpubmini-track-digest256.log (mozpubmini.txt)"
fi

