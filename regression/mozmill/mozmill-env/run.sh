#!/bin/bash

mozmill -b /Applications/FirefoxNightlyDebug.app/Contents/MacOS/firefox-bin --profile=~/Library/Application\ Support/Firefox/Profiles/YOURPROFILEHERE/ -t mytests/mytest.js &> output.log
