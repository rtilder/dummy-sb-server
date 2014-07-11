#!/usr/bin/python
"""Create a host list from the given easylist repo."""
# Usage: abp_hosts.py <input_directory> <output_file>

import os
import re
import socket
import sys

import hashlib

import urllib2

# IGNR_REGEXP
# HOST_REGEXP

# ignore lines we REALLY KNOW WHAT THEY ARE
# and figure they are NOT RELEVANT to us
IGNR_REGEXP = [
  # '#' is for COMMENTS
  # ':' is expiration metadata
  # "msFilterList" is magic word
  re.compile("^:|#|msFilterList"),
  # '- ' is for substring rules
  re.compile("^- "),
  # "+d ' is for white-list rules
  re.compile("^\+d ")
];

# match host rules
HOST_REGEXP = [
  re.compile("^\-d "
    # domain
    + "([a-z0-9\-]+(?:[.][a-z0-9\-]+)*[.][a-z0-9]+)[ ]*$")
];

RJCT_REGEXP = [
  # * anywhere in the rule
  re.compile("\*"),
  # "-d TOKEN TOKEN" implies URL substrings which we do not support
  re.compile("^\-d [^ ]+[ ]+[^ ]+[ ]*$")
]

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


def classifyRule(line):

  # should we ignore this line?

  ignore = False;

  for ignr_regexp in IGNR_REGEXP:
    ignore |= ((re.match(ignr_regexp, line) and True) or False);

    if (ignore):
      return ['ignore', None];

  # match against our primary expression
  for host_regexp in HOST_REGEXP:
    m = re.match(host_regexp, line);
    if (m):
      break;

  # match against our rejection expression
  r = False

  for rjct_regexp in RJCT_REGEXP:
    r |= ((re.search(rjct_regexp, line) and True) or False);

    if (r):
      return ['reject', None];

  # handle match against the primary expression
  if (m):
    # Skip hosts that don't exist
    # Note: This is too slow. Let's keep it off for now.
    #try:
    #  socket.gethostbyname(m.group(1));
    #except:
    #  return ['nxdomain', None]
    return['safebrowsingSupports', m];

  # we shouldn't have any unknowns.
  # either the ignore rule or the primary rule should match
  else:
    return['unknown', None];


def find_hosts(filename, f_out, f_dbg, f_log, chunk):

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

    [verdict, m] = classifyRule(line);

    # should we ignore this line?

    if (verdict == 'ignore'):
      f_log.write("[IGNORING] %s\n" % line.strip());
      continue;

    if (verdict == 'reject'):
      f_log.write("[REJECTED] %s\n" % line.strip());
      continue;

    if (verdict == 'nxdomain'):
      f_log.write("[REJECTED] nxdomain %s\n" % line.strip());
      continue;

    # handle match against the primary expression
    if (verdict == 'safebrowsingSupports'):
      # matching groups
      # 0: entire expression
      # 1: host

      match_s = canonicalize(m.group(1));

      # lookup pagerank for domain-wide rules (no path) with rule options
      #if (m.group(4) and
      #    ((not m.group(3)) or re.match(r'^(\^|\/)*$', m.group(3)))):
      #else:
      #  pagerank = "RANK_IGNR";
      pagerank = "RANK_IGNR";

      f_log.write("[m] %s >> %s %s"
        % (line.strip(), match_s, pagerank));

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
  f_dbg.write("a:%u:32:%s\n" % (chunk, hashdata_bytes));
  f_out.write("a:%u:32:%s\n" % (chunk, hashdata_bytes));

  # write safebrowsing-list format hash data
  for o in output_dbg:
    f_dbg.write("%s\n" % o);

  for o in output:
    f_out.write(o);


def main(dir, f_out, f_dbg, f_log, chunk):
  socket.setdefaulttimeout(5);

  for root, dirs, files in os.walk(dir):
    # Process all of the files, one by one
    if root.find(".hg") != -1:
      continue
    for name in files:
      find_hosts(os.path.join(root, name), f_out, f_dbg, f_log, chunk);
      chunk += 1;

  return chunk;
