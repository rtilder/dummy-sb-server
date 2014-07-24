#!/bin/bash

# YOUR PROFILE HERE
profile="sl6hdyy9.default2"

# couldn't get mozpub-track-digest256 to work without this. it was like it wasn't there. no matches.
cp ~/Library/Caches/Firefox/Profiles/${profile}/safebrowsing/* ~/Library/Application\ Support/Firefox/Profiles/${profile}/safebrowsing/

mozmill -b /Applications/FirefoxNightlyDebug.app/Contents/MacOS/firefox-bin --profile=/Users/mozilla/Library/Application\ Support/Firefox/Profiles/${profile}/ -t mytests/mytest.js &> output.log
