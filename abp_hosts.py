#!/usr/bin/python
"""Create a host list from the given easylist repo."""
# Usage: abp_hosts.py <input_directory> <output_file>

import os
import re
import sys

import hashlib

import urllib2

# catching rules matched against the domain name of a candidate URL
# 
# simple catch-all expression to make sure we are not missing anything. 
# might include false positives but that's OK since this is our failsafe.
#
# ^|  matches starting from the beginning of the URL (as opposed to *rule*) 
#     e.g., ^|http://www.example.com is a valid rule
#           ^|www.example.com        is NOT a valid rule
# ^|| matches starting from the beginning of the domain name
#     e.g., ^||www.example.com        is a valid rule
#           ^||http://www.example.com is NOT a valid rule
# 
# Note: one could specify rule "www.example.com" although 
# that translates to "*www.example.com*" and is not correct. 
# easylist doesn't contain any cases like that.
# 
REGEXP_ASSERTION = re.compile("^[|]{1,2}");

# ignore lines we really know what they are 
# and figure they are not relevant to us
IGNR_REGEXP = [
  # '^!' is for comments
  # '^##' is for hiding elements
  # '^@@' is for exceptions to the blocklist
  re.compile("^!|[#]{2}|[@]{2}"), 
  # '^domain##' and '^domain,domain2##' is for hiding elements 
  # on specific domains. '^domain' and '^domain,domain2#@#' is 
  # for creating a hiding exception (do not hide) on specific domains.
  re.compile("^[~]*[a-z0-9-]+([.][a-z0-9-]+)+([,][~]*[a-z0-9-]+([.][a-z0-9-]+)+)*#[@]{0,1}#"),
  # rules ^[a-z0-9./&-+\[_:=;\?,^] will match .*RULE and 
  # that doesn't really work for us. definitely not rules starting with symbols
  re.compile("^[a-z0-9./&\-+\[_:=;\?,^]")
];

HOST_REGEXP = [
  # matching rule starting from the domain name of a URL
  re.compile("^[|]{2}([a-z0-9-]+(?:[.][a-z0-9-]+)*[.][a-z0-9-]+)[\\^/](?:\?|\$(?:third-party|popup|subdocument|image|~[^,]+)(?:,third-party|,popup|,subdocument|,image|,~[^,]+)*$|$)"),
  # matching rule start from the beginning of a URL
  re.compile("^[|]{1}(?:http\:\/\/|https\:\/\/)([a-z0-9-]+(?:[.][a-z0-9-]+)*[.][a-z0-9-]+)[\\^/](?:\?|\$(?:third-party|popup|subdocument|image|~[^,]+)(?:,third-party|,popup|,subdocument|,image|,~[^,]+)*$|$)")
];

RJCT_REGEXP = [
  # rule ends in jpg|png|gif|html|php|js|swf|jsp|aspx
  re.compile("[.](jpg|png|gif|htm[l]?|php|js|swf|jsp|asp[x]?)?$"),
  # rule ends in _ or -
  re.compile("(_|\-)$"),
  # somewhere in the middle of the rule but not in the domain
  re.compile("^[|]{2}([a-z0-9-]+(?:[.][a-z0-9-]+)*[.][a-z0-9-]+)[\\^/].*[.](jpg|png|gif|htm[l]?|php|js|swf|jsp|asp[x]?)?(\?|\$|$)"),
  # somewhere in the midlee of the rule but not in the domain
  re.compile("^[|]{2}([a-z0-9-]+(?:[.][a-z0-9-]+)*[.][a-z0-9-]+)[\\^/].*(_|\-)(\?|\$|$)"),
  # somewhere in the middle of the rule but not in the domain
  re.compile("^[|]{1}(?:http\:\/\/|https\:\/\/)([a-z0-9-]+(?:[.][a-z0-9-]+)*[.][a-z0-9-]+)[\\^/].*[.](jpg|png|gif|htm[l]?|php|js|swf|jsp|asp[x]?)?(\?|\$|$)"), 
  # somewhere in the middle of the rule but not in the domain
  re.compile("^[|]{1}(?:http\:\/\/|https\:\/\/)([a-z0-9-]+(?:[.][a-z0-9-]+)*[.][a-z0-9-]+)[\\^/].*(_|\-)(\?|\$|$)"), 
  # *
  re.compile("\*")
]

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

  return d + "/";

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

    ignore = False;

    for ignr_regexp in IGNR_REGEXP:
      ignore |= ((re.match(ignr_regexp, line) and True) or False);

    if (ignore): 
      f_log.write("[IGNORING] %s\n" % line.strip());
      continue;

    # catch-all rule to make sure we are not missing anything
    assertion = re.match(REGEXP_ASSERTION, line)

    # match against our primary expression
    for host_regexp in HOST_REGEXP:
      m = re.match(host_regexp, line);
      if (m):
        break;

    # match against our rejection expression
    r = False

    for rjct_regexp in RJCT_REGEXP:
      r |= ((re.search(rjct_regexp, line) and True) or False);

    if (assertion) and (r):
      f_log.write("[REJECTED] %s\n" % line.strip());
      continue;

    match_s = ""
    if m and m.group(1):
      match_s = canonicalize(m.group(1));

    # match against the primary expression
    if (m):
      f_log.write("[m] %s >> %s" % (line.strip(), match_s));
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

        f_log.write("\n");

        hashdata_bytes += 32;

        # book keeping
        domain_dict[match_s] = 1;

        #f_out.write("%s\n" % (match_s, ))
        output_dbg.append(hashlib.sha256(match_s).hexdigest());
        output.append(hashlib.sha256(match_s).digest());

      else:

        f_log.write(" DUP\n");

  # write safebrowsing-list format header
  f_dbg.write("a:1:32:%s\n" % hashdata_bytes);
  f_out.write("a:1:32:%s\n" % hashdata_bytes);

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

