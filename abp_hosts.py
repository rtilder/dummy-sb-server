#!/usr/bin/python
"""Create a host list from the given easylist repo."""
# Usage: abp_hosts.py <input_directory> <output_file>

import os
import re
import sys

import hashlib

import urllib2

import wwwranking

# IGNR_REGEXP
# REGEXP_ASSERTION
# HOST_URL_OPT_REGEXP
# RJCT_REGEXP

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

# ignore lines we REALLY KNOW WHAT THEY ARE 
# and figure they are NOT RELEVANT to us
IGNR_REGEXP = [
  # '^!' is for COMMENTS
  # '^##' is for HIDING elements
  # '^@@' is for EXCEPTIONS to the blocklist
  re.compile("^!|[#]{2}|[@]{2}"), 
  # '^domain##' and '^domain,domain2##' is for HIDING elements 
  # on specific domains. '^domain' and '^domain,domain2#@#' is 
  # for creating a HIDING EXCEPTION (do not hide) on specific domains.
  re.compile("^[~]*[a-z0-9\-]+([.][a-z0-9\-]+)+([,][~]*[a-z0-9\-]+([.][a-z0-9\-]+)+)*#[@]{0,1}#"),
  # rules ^[a-z0-9./&-+\[_:=;\?,^] will match .*RULE and 
  # that doesn't really work for us. definitely not rules starting with symbols
  re.compile("^[a-z0-9./&\-+\[_:=;\?,^]")
];

# match host-URL-options rules
HOST_URL_OPT_REGEXP = [
  # matching rule starting from the domain name of a URL
  re.compile("^[|]{2}" 
    # (foo.bar.com(:port))
    + "([a-z0-9\-]+(?:[.][a-z0-9\-]+)*[.][a-z0-9\-]+(?:\:[0-9]+)?)" 
    # (/(path)($option(,option)))
    + "(((?:\/|\^)[^\$]*)((?:\$(~*script|~*image|~*stylesheet|~*object|~*xmlhttprequest|~*object\-subrequest|~*subdocument|~*third\-party|~*popup)(?:,~*script|,~*image|,~*stylesheet|,~*object|,~*xmlhttprequest|,~*object\-subrequest|,~*subdocument|,~*third\-party|,~*popup)*$)|$)|$)"), 
  # matching rule start from the beginning of a URL
  re.compile("^[|]{1}" 
    # (scheme)
    + "(?:[a-z]+\:\/\/)?" 
    # (username(:password)@)
    + "(?:[a-z]+(?:\:[a-z0-9]+)?@)?" 
    # (foo.bar.com(:port))
    + "([a-z0-9\-]+(?:[.][a-z0-9\-]+)*[.][a-z0-9\-]+(?:\:[0-9]+)?)" 
    # (/(path)($option(,option)))
    + "(((?:\/|\^)[^\$]*)((?:\$(~*script|~*image|~*stylesheet|~*object|~*xmlhttprequest|~*object\-subrequest|~*subdocument|~*third\-party|~*popup)(?:,~*script|,~*image|,~*stylesheet|,~*object|,~*xmlhttprequest|,~*object\-subrequest|,~*subdocument|,~*third\-party|~*popup)*$)|$)|$)") 
];

RJCT_REGEXP = [
  # * anywhere in the rule
  re.compile("\*"),
  # rule is specific to a domain
  re.compile("(\$domain=[^,]+(,[a-z\-]+(=[^,]+)?)*$)|(\$([a-z\-]+(=[^,]+)?,)*domain=[^,]+$)")
]

# book-keeping dictionary. 
# remembers previously-processed domains 
# so we don't print them more than once
domain_dict = {};

# for a given domain try to find highest pagerank 
# by successively removing its subdomains
def lookup_pagerank(d):

  dotcount = d.count(".")

  # probably not a domain
  if (dotcount == 0):
    return -1;

  # make sure d is not an IP address
  ipaddr_exp = re.compile("^[0-9]+(\.[0-9]+){3}$");

  # no subdomains or this is an IP address
  if (dotcount == 1 or re.match(ipaddr_exp, d)):
    return wwwranking.pagerank(d);

  # find beginning of next subdomain
  x = d.find(".");
  
  this_pagerank = wwwranking.pagerank(d)
  hypr_pagerank = wwwranking.pagerank(d[x+1:]);

  if this_pagerank == -1:
    return hypr_pagerank;

  if hypr_pagerank == -1:
    return this_pagerank;

  # return minimum value (highest ranking) 
  # among this domain and its hyper domain 
  return min(this_pagerank, hypr_pagerank);


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

  # Note: we do NOT append the scheme 
  # because safebrowsing lookups ignore it
  return host + "/" + urllib2.quote(path);


def classifyRule(line):

  # should we ignore this line?

  ignore = False;

  for ignr_regexp in IGNR_REGEXP:
    ignore |= ((re.match(ignr_regexp, line) and True) or False);

    if (ignore):
      return ['ignore', None];

  # catch-all rule to make sure we are not missing anything
  assertion = re.match(REGEXP_ASSERTION, line)

  # match against our primary expression
  for host_regexp in HOST_URL_OPT_REGEXP:
    m = re.match(host_regexp, line);
    if (m):
      break;

  # match against our rejection expression
  r = False

  for rjct_regexp in RJCT_REGEXP:
    r |= ((re.search(rjct_regexp, line) and True) or False);

    if (assertion) and (r):
      return ['reject', None];

  # handle match against the primary expression
  if (m):
    return['safebrowsingSupports', m];

  # did the primary expression miss something?
  elif (assertion):
    return['missed', None];
  # we shouldn't have any unknowns. 
  # either the ignore rule or the primary rule should match
  else:
    return['unknown', None];


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

    [verdict, m] = classifyRule(line);

    # should we ignore this line?

    if (verdict == 'ignore'): 
      f_log.write("[IGNORING] %s\n" % line.strip());
      continue;

    if (verdict == 'reject'):
      f_log.write("[REJECTED] %s\n" % line.strip());
      continue;

    # handle match against the primary expression
    if (verdict == 'safebrowsingSupports'):
      # matching groups
      # 0: entire expression
      # 1: host
      # 2: path, query params, fragments and rule options
      # 3: path
      # 4: rule options

      # exclude query string from canonicalization and add it later
      [path, delim, query] = (m.group(3) or "").strip().partition("?");

      match_s = canonicalize(
        m.group(1) + "/" + re.subn("\^", "", (path or ""))[0]);

      # append query string blob to canonicalized host/path only if
      # there is an actual query string
      if (query != ""):
        match_s += (delim + query);

      # lookup pagerank for domain-wide rules (no path) with rule options
      #if (m.group(4) and 
      #    ((not m.group(3)) or re.match(r'^(\^|\/)*$', m.group(3)))):
      #else:
      #  pagerank = "RANK_IGNR";
      pagerank = "RANK_IGNR";

      f_log.write("[m] %s >> %s %s" 
        % (line.strip(), match_s, pagerank));

    # did the primary expression miss something?
    elif (verdict == 'missed'):
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

