#!/bin/bash
set -x
set -e

if [ -z "$MOZMILL_PROFILE" ]
then
  MOZMILL_PROFILE="sl6hdyy9.default2"
fi

# couldn't get mozpub-track-digest256 to work without this. it was like it wasn't there. no matches.
CACHE_PREFIX=~/Library/Caches/Firefox/Profiles
ROAMING_PREFIX=~/Library/Application\ Support/Firefox/Profiles
FIREFOX=/Applications/FirefoxNightlyDebug.app/Contents/MacOS/firefox-bin
if [[ "$OSTYPE" == "linux-gnu" ]]
then
  ROAMING_PREFIX=~/.mozilla/firefox
  CACHE_PREFIX=~/.cache/mozilla/firefox
  FIREFOX=${NIGHTLY_OBJ}/dist/bin/firefox
fi

cp -r ${CACHE_PREFIX}/${MOZMILL_PROFILE}/safebrowsing \
  ${ROAMING_PREFIX}/${MOZMILL_PROFILE}

mozmill -b ${FIREFOX} --profile=${ROAMING_PREFIX}/${MOZMILL_PROFILE} -t mytests/mytest.js &> output.log
