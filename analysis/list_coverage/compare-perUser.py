#!/usr/bin/python

# given an input file in the format <domain:type frequency>
# (e.g., foo.com:third_domain 10) and a lookup file in the format <domain/>
# (e.g., foo.com/) report which of the input file domains have exact matches
# in the lookup file entries
#
# trailing slashes are ignored (domain/ is a match against domain)
#

import sys
import os
import re
import operator

lookup_dict = {}
input_first_dict = {}
input_third_dict = {}

def main():
  if len(sys.argv) < 3:
    sys.exit("Usage: " + sys.argv[0] + " <input_file.tsv> <lookup_file.txt>");

  # populate lookup dictionary (blacklist) using the lookup file
  f_lookup = open(sys.argv[2], "r");
  for line in f_lookup.readlines():
    # strip trailing newline and/or slash
    line = re.subn("\/$", "", line.strip())[0];
    lookup_dict[line] = 1
  f_lookup.close();

  # go over the input file and populate two dictionaries
  # for first and third-party domains respectively
  f_in = open(sys.argv[1], "r");
  for line in f_in.readlines():
    # tokenize line to [user, domain, party, frequency]
    e = re.compile('([^:]+):([^:]+):([^\t]+)\t([0-9]+)$');
    m = re.match(e, line.strip());
    if (not m):
      print "[ERR]", line
      break;
    else:
      user = m.group(1);
      domain = m.group(2);
      party  = m.group(3);
      frequency = m.group(4);
      if (party == "user_first_domain"):
        input_first_dict[domain] = frequency;
      elif (party == "user_third_domain"):
        input_third_dict[domain] = frequency;
      else:
        print "[UNKNOWN]", party
        sys.exit(-1);
  f_in.close();

  # reverse num sort of first and third-party dictionaries based on values
  sinput_first_dict = \
    sorted(input_first_dict.iteritems(),
      key=lambda (k, v): (int(v), k), reverse=True);
  sinput_third_dict = \
    sorted(input_third_dict.iteritems(),
      key=lambda (k, v): (int(v), k), reverse=True);

  # update first and third-party dictionaries with rank (high = popular)
  # instead of frequency
  cnt = 1;
  for i in sinput_first_dict:
    input_first_dict[i[0]] = cnt;
    cnt += 1;

  cnt = 1;
  for i in sinput_third_dict:
     input_third_dict[i[0]] = cnt;
     cnt += 1;

  # go over input file one more time and this time check against lookup_dict
  # (blacklist)
  f_in = open(sys.argv[1], "r");
  for line in f_in.readlines():
    # tokenize line to [user, domain, party, frequency]
    e = re.compile('([^:]+):([^:]+):([^\t]+)\t([0-9]+)$');
    m = re.match(e, line.strip());
    # we skip error checking because this is the second pass
    user = m.group(1);
    domain = m.group(2);
    party = m.group(3);
    frequency = m.group(4);
    # look up rank among peers
    rank = "N/A";
    if (party == "user_first_domain"):
      rank = \
        str(input_first_dict[domain]) + " / " + str(len(sinput_first_dict));
    elif (party == "user_third_domain"):
      rank = \
        str(input_third_dict[domain]) + " / " + str(len(sinput_third_dict));
    # present
    if domain in lookup_dict:
      print "[HIT]", user, domain, party, frequency, rank
    else:
      print "[MISS]", user, domain, party, frequency, rank
  f_in.close();

if __name__ == "__main__":
  main()
