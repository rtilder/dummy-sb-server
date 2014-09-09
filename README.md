Dummy Safe Browsing server
================
Cram hosts collected from various sources into the safebrowsing digest256 format.

To generate: make mozpub && ls tmp_out/mozpub-track-digest256*

mozpub-track-digest256 is the list in the safebrowsing digest256 format. A Safe Browsing server will want to return that to satify client requests.

mozpub-track-digest256.log and mozpub-track-digest256.dbg are non-essential files that provide extra and debug information on the list and how it was generated. For instance '.log' indicates exactly which entries are on the list.

List naming
========================
The current Firefox client code points to mozpub-track-digest256 (http://mxr.mozilla.org/mozilla-central/source/modules/libpref/init/all.js#4233). The parser used by the client is determined by the suffix. The use of the list is determined by the presence of "-track-" (http://mxr.mozilla.org/mozilla-central/source/toolkit/components/url-classifier/nsUrlClassifierDBService.cpp#1040). We may switch to shavar at any time to be more space efficient -- however, any change in table name must be coordinated with changes in the client code.

Checking for correctness
========================
0) Start a clean profile
1) Enable browser.safebrowsing.debug
2) (optional) Point browser.trackingprotection.updateURL at the staging server
3) Restart firefox
4) Check the contents of the safebrowsing directory in the roaming profile. On linux that's ~/.cache/mozilla/firefox/<profile>/safebrowsing/. It should *not* contain any files named mozpub-track-digest*.
5) Enable privacy.trackingprotection.enabled.
6) You may see the update messages in the console if browser.safebrowsing.debug is enabled. Make sure that the updateURL is as expected.
7) Check the contents of the safebrowsing directory again. You should see 3 files: mozpub-track-digest.{sbstore,pset,cache}
8) Dump the contents of these files with http://github.com/kontaxis/sbdbdump/dump.py <safebrowsingdir> --v --name mozpub-track-digest.
9) Check that the hashes match the lines in "make mozpub && grep hash tmp_out/disconnect/mozpub-track-digest256.log | cut -f2 -d" "
