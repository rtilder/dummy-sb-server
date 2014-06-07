#!/usr/bin/python
"""Create a host list from the given easylist repo."""
# Usage: abp_hosts.py <input_directory> <output_file>

import os
import re
import sys

import hashlib

import urllib2

# simple catch-all expression to make sure we are not missing anything. 
# might include false positives but that's OK since this is our failsafe.
REGEXP_ASSERTION = re.compile("^[|]{2}");

# ignore comments, standard rule exceptions, hide filters
# '#' is for hiding elements, '@' is for exceptions to the blocklist
IGNR_REGEXP = re.compile("^!|[#]{2}|[@]{2}");

HOST_REGEXP = re.compile("^[|]{2}([a-z0-9-]+([.][a-z0-9-]+)+)[\\^/]")

RJCT_REGEXP = re.compile("\\.(jpg|png|gif|html|js)")

# book-keeping dictionary. 
# remembers previously-processed domains 
# so we don't print them more than once
domain_dict = {};

# bring a domain to canonical form

def canonicalize(d):

  if (not d or d == ""): 
    return d;

  # remove tab (0x09), CR (0x0d), LF (0x0a)
  d = re.subn("\t|\r|\n", "", d)[0];

  # unescape
  while (1):
    _d = d;
    d = urllib2.unquote(_d);
    # if decoding had no effect, stop
    if (d == _d):
      break;

  # remove leading and trailing dots
  d = re.subn("^\.+|\.+$", "", d)[0];

  # replace consequtive dots with a single dot
  d = re.subn("\.+", ".", d)[0];

  # lowercase the whole thing
  d = d.lower();

  # kill any trailing slashes (will place one before returning)
  re.subn("\/+$", "", d)[0];

  return "http://" + d + "/";

def find_hosts(filename, f_out, f_dbg, f_log):

  f_in = open(filename, "r")

  # total number of bytes that will be written to f_out for hashed hosts 
  # should be modulo 32
  hashdata_bytes = 0;

  # array holding hash bytes to be written to f_out 
  # we buffer output here because we need to know the 
  # final byte first (see hashdata_bytes)
  output = [];
  output_dbg = [];

  for line in f_in.readlines():

    # should we ignore this line?
    ignore = re.match(IGNR_REGEXP, line)

    if (ignore): 
      f_log.write("[IGNORING] %s\n" % line.strip());
      continue;

    # catch-all rule to make sure we are not missing anything
    assertion = re.match(REGEXP_ASSERTION, line)

    # match against our primary expression
    m = re.match(HOST_REGEXP, line)

    # match against our rejection expression
    r = re.search(RJCT_REGEXP, line)

    if (assertion) and (r):
      f_log.write("[REJECTED] %s\n" % line.strip());
      continue;

    match_s = ""
    if m and m.group(1):
      match_s = canonicalize(m.group(1));

    # match against the primary expression
    if (m):
      f_log.write("[m] %s >> %s\n" % (line.strip(), match_s));
    # did the primary expression miss something?
    elif (assertion):
      f_log.write("[MISSED] %s\n" % line.strip());
    # we shouldn't have any unknowns. 
    # either the ignore rule or the primary rule should match
    else:
      f_log.write("[UNKNOWN] %s\n" % line.strip());

    # print matches
    if m:

      # make sure we print each domain once, 
      # domain_dict remembers previously printed domains
      if (not (match_s in domain_dict)):

        hashdata_bytes += 32;

        # book keeping
        domain_dict[match_s] = 1;

        #f_out.write("%s\n" % (match_s, ))
        output_dbg.append(hashlib.sha256(match_s).hexdigest());
        output.append(hashlib.sha256(match_s).digest());

  # write safebrowsing-list format header
  f_dbg.write("mozpub-track-digest256:1:%s\n" % hashdata_bytes);
  f_out.write("mozpub-track-digest256:1:%s\n" % hashdata_bytes);

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
  f_log = open("log", "w");

  for root, dirs, files in os.walk(sys.argv[1]):
    # Process all of the files, one by one
    if root.find(".hg") != -1:
      continue
    for name in files:
      find_hosts(os.path.join(root, name), f_out, f_dbg, f_log);

  f_out.close();
  f_dbg.close();
  f_log.close();

if __name__ == "__main__":
  main()

