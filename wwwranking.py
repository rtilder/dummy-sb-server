#!/usr/bin/python

import sys
import urllib2
import json
import re

def pagerank(domain):

  response = urllib2.urlopen(
    "http://wwwranking.webdatacommons.org" 
    + "/Q/?pageIndex=0&pageSize=10&search=" 
    + domain)

  # get HTTP response data
  data = response.read()

  # parse data as JSON
  data_o = json.loads(data);

  if "data" in data_o:
    # iterate over the data elements returned
    for obj in data_o["data"]:
      # for each element iterate over its keys
      for o in obj:
        # if harmonic key's value ends with our domain, we have our match
        if o == "harmonic" and obj[o].find(">" + domain + "</a>") != -1:
          if "pagerank" in obj:
            return int(obj["pagerank"].encode('ascii'))

  return -1;

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print "Usage:", sys.argv[0], "www.example.com"
    exit(1);

  print pagerank(sys.argv[1]);
