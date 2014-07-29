#!/usr/bin/env python2.6

import os
import operator
import fileinput
import sys
try:
  import simplejson as json
except:
  import json

# Each line is of the form
# docid { json blob }

NFIELDS = 2

for line in sys.stdin: 
  # Lines are tab-delimited
  l = line.split('\t')
  if len(l) != NFIELDS:
    continue

  docid = l[0]
  try:
    blob = json.loads(l[1])
  except:
    sys.stderr.write("reporter:status:format\n")
    continue

  # skip wrong format
  if blob["version"] != "1.2":
    sys.stderr.write("reporter:status:version\n")
    continue

  # Count the number of distinct users
  userid = blob["userId"].replace(":", "_")
  print "UniqValueCount:users_total\t%s" % blob["userId"]

  for c in blob["connections"]:
    if not (type(c) is list):
      sys.stderr.write("reporter:status:list\n")
      continue
    if c[0] == c[1]:
      print "LongValueSum:%s:first_domain\t1" % c[0]
      print "LongValueSum:%s:%s:user_first_domain\t1" % (userid, c[0])
    else:
      print "LongValueSum:%s:third_domain\t1" % c[0]
      print "LongValueSum:%s:%s:user_third_domain\t1" % (userid, c[1])
