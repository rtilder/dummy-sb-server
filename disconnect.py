#!/usr/bin/python
"""Create a host list from the given easylist repo."""
# Usage: disconnect.py <input_json> <output_file>

import json
import os
import re
import sys

import hashlib

import urllib2

# book-keeping dictionary. 
# remembers previously-processed domains 
# so we don't print them more than once
domain_dict = {};

# bring a URL to canonical form as described at 
# https://developers.google.com/safe-browsing/developers_guide_v2

def canonicalize(d):

  if (not d or d == ""): 
    return d;

  # remove tab (0x09), CR (0x0d), LF (0x0a)
  d = re.subn("\t|\r|\n", "", d)[0];

  # remove any URL fragment
  fragment_index = d.find("#")
  if (fragment_index != -1):
    d = d[0:fragment_index]

  # repeatedly unescape until no more hex encodings
  while (1):
    _d = d;
    d = urllib2.unquote(_d);
    # if decoding had no effect, stop
    if (d == _d):
      break;

  # extract hostname (scheme://)(username(:password)@)hostname(:port)(/...)
  # extract path
  url_components = re.match(
    re.compile(
      "^(?:[a-z]+\:\/\/)?(?:[a-z]+(?:\:[a-z0-9]+)?@)?([^\/^\?^\:]+)(?:\:[0-9]+)?(\/(.*)|$)"), d);
  host = url_components.group(1);
  path = url_components.group(2) or "";
  path = re.subn("^(\/)+", "", path)[0];

  # remove leading and trailing dots
  host = re.subn("^\.+|\.+$", "", host)[0];

  # replace consequtive dots with a single dot
  host = re.subn("\.+", ".", host)[0];

  # lowercase the whole thing
  host = host.lower();

  # percent-escape any characters <= ASCII 32, >= 127, or '#' or '%'
  _path = "";
  for i in path:
    if (ord(i) <= 32 or ord(i) >= 127 or i == '#' or i == '%'):
      _path += urllib2.quote(i);
    else:
      _path += i;

  # Note: we do NOT append the scheme
  # because safebrowsing lookups ignore it
  return host + "/" + _path;


def find_hosts(filename, f_out, f_dbg, f_log):
  # Total number of bytes that will be written to f_out for hashed hosts 
  # should be 0 modulo 32
  hashdata_bytes = 0;
  # Array holding hash bytes to be written to f_out. Buffer output here
  # because we need to know the final byte first (see hashdata_bytes)
  output = [];
  output_dbg = [];

  f_in = open(filename, "r")
  blob = json.loads(f_in.read())
  block_categories = ["Analytics", "Advertising"]
  categories = blob["categories"]
  for c in categories:
    if c in block_categories:
      # Objects of type
      # { Automattic: { http://automattic.com: [polldaddy.com] }}
      # Domain lists may or may not contain the address of the top-level site.
      for org in categories[c]:
        for orgname in org:
          top_domains = org[orgname]
          for top in top_domains:
            domains = top_domains[top]
            for d in domains:
              if not d in domain_dict:
                d = canonicalize(d)
                domain_dict[d] = 1
                hashdata_bytes += 32;
                try:
                  output_dbg.append(hashlib.sha256(d).hexdigest());
                  output.append(hashlib.sha256(d).digest());
                except:
                  f_log.write("error processing " + json.dumps(d) + "\n")


  f_log.write(json.dumps(domain_dict, sort_keys=True, indent=2))

  # write safebrowsing-list format header
  f_dbg.write("a:1:32:%s\n" % (hashdata_bytes));
  f_out.write("a:1:32:%s\n" % (hashdata_bytes));

  # write safebrowsing-list format hash data
  for o in output_dbg:
    f_dbg.write("%s\n" % o);

  for o in output:
    f_out.write(o);


def main():
  """Read the easylist repo and output matching hosts."""
  if len(sys.argv) < 3:
    sys.exit("Usage: abp_hosts.py <input_directory> <output_file>")

  # output file, 
  # representation of extracted hosts in safebrowsing-list format
  f_out = open(sys.argv[2], "wb")

  # output file, 
  # debug version of f_out. binary hashes are now in hex format 
  # and they are followed by a LF
  f_dbg = open(sys.argv[2] + ".dbg", "w");

  # log file
  f_log = open(sys.argv[2] + ".log", "w");

  find_hosts(sys.argv[1], f_out, f_dbg, f_log);

  f_out.close();
  f_dbg.close();
  f_log.close();

if __name__ == "__main__":
  main()


