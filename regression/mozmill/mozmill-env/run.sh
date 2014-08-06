#!/bin/bash
set -x
set -e

if [ -z $MOZMILL_PROFILE ]
then
  echo "Must specify \$MOZMILL_PROFILE"
  exit -1
fi

TEST=disabled.js
if [ $ENABLE_TRACKING_PROTECTION ]
then
  TEST=enabled.js
fi

# Optionally install addons
if [ ! -z "$ADDON" ]
then
  ADDON="-a $ADDON"
fi

# couldn't get mozpub-track-digest256 to work without this. it was like it wasn't there. no matches.
CACHE_PREFIX=~/Library/Caches/Firefox/Profiles
ROAMING_PREFIX=~/Library/Application\ Support/Firefox/Profiles
FIREFOX=/Applications/FirefoxNightly.app/Contents/MacOS/firefox-bin
if [[ "$OSTYPE" == "linux-gnu" ]]
then
  ROAMING_PREFIX=~/.mozilla/firefox
  CACHE_PREFIX=~/.cache/mozilla/firefox
  FIREFOX=${NIGHTLY_OBJ}/dist/bin/firefox
fi

cp -r ${CACHE_PREFIX}/${MOZMILL_PROFILE}/safebrowsing \
  "${ROAMING_PREFIX}/${MOZMILL_PROFILE}"

mozmill -b ${FIREFOX} ${ADDON} --profile=${ROAMING_PREFIX}/${MOZMILL_PROFILE} -t mytests/${TEST} &> $TEST.log
