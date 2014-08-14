abp-hostblocking
================
Cram hosts collected from various sources into the safebrowsing digest256 format.

To generate: make mozpub && ls tmp_out/mozpub-track-digest256*

mozpub-track-digest256 is the list in the safebrowsing digest256 format. A Safe Browsing server will want to return that to satify client requests.

mozpub-track-digest256.log and mozpub-track-digest256.dbg are non-essential files that provide extra and debug information on the list and how it was generated. For instance '.log' indicates exactly which entries are on the list.
