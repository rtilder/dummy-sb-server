#!/bin/bash

# alexa top 1000

curl http://s3.amazonaws.com/alexa-static/top-1m.csv.zip -o top-1m.csv.zip && \
unzip top-1m.csv.zip && \
(IFS=$'\n'; echo "var sites = ["; for i in `head -n 1000 top-1m.csv | awk -F \, '{print $2}'`; do echo "\"$i\","; done; echo "\"example.com\""; echo "];"; echo "exports.sites = sites";) > testInputData.js

echo -e "\nREADY"
