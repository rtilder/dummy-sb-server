"use strict";

// Include required modules
var prefs = require("../../mozmill-tests/firefox/lib/prefs");
var tabs = require("../../mozmill-tests/firefox/lib/tabs");

var myprefs = {
// caching prefs
"network.http.use-cache": false,
"browser.cache.disk.enable": false,
"browser.cache.memory.enable": false,
"image.cache.size": 0,
"media.cache_size": 0,
"network.buffer.cache.size": 0,
"network.prefetch-next": false,
"network.dns.disablePrefetch": true,
"network.predictor.enabled": false,
"network.dnsCacheEntries": 0,
"network.dnsCacheExpiration": 1,
// IPv6 always complicates things (timeouts)
"network.dns.disableIPv6": true
};
exports.myprefs = myprefs;

var controller;
exports.controller = controller;

// Setup for the test
exports.setupModule = function(aModule)
{
  for (var pref in myprefs) {
    prefs.preferences.setPref(pref, myprefs[pref]);
  }

  aModule.controller = mozmill.getBrowserController();
  controller = aModule.controller;
}

exports.teardownModule = function teardownModule(aModule) {
  for (var pref in myprefs) {
    prefs.preferences.clearUserPref(pref);
  }
}

// Iterates over a list of URLs (testInputData.sites) and
// opens them one by one in the same tab. It waits until
// each page loads before moving on to the next URL.
exports.testSampleTestcase = function()
{
  dump("- INFO: privacy.trackingprotection.enabled " + (prefs.preferences.getPref("privacy.trackingprotection.enabled", false)) + "\n");

  var testInputData = require("testInputData");

  dump("- INFO: READY\n");

  // start with no tabs
  //tabs.closeAllTabs(controller);

  //for (var i = 0; i < testInputData.sites.length; i++)
  for (var i = 0; i < 10; ++i)
  {
    dump(">>> TEST_DEBUG [" + i + "] " + testInputData.sites[i] + " START\n");

    let tries = 3; // tries before giving up on a URL

    while (tries > 0)
    {
      //dump(">>> TEST_DEBUG [" + i + "] " + testInputData.sites[i] + " will close all tabs\n");

      tabs.closeAllTabs(controller);

      //dump(">>> TEST_DEBUG [" + i + "] " + testInputData.sites[i] + " will close all tabs DONE\n");

      // time before
      var t_start = (new Date()).getTime();

      //dump(">>> TEST_DEBUG [" + i + "] " + testInputData.sites[i] + " will open controller\n");

      controller.open(testInputData.sites[i])

      //dump(">>> TEST_DEBUG [" + i + "] " + testInputData.sites[i] + " will open controller DONE\n");

      // wait for page to load before trying to load next URL in this loop
      try {
        controller.waitForPageLoad(60000); // 60 sec timeout

        // time after
        var t_finish = (new Date()).getTime();

        dump(">>> TEST [" + i + "] " + testInputData.sites[i] +
          " OK (" + (t_finish - t_start) + " ms) [FINAL_RESULT]\n");

        break; // move on
      }
      catch (e)
      {
        /* we expect AssertionError when waitForPageLoad() times out */
        if (e instanceof errors.AssertionError)
          dump(">>> TEST [" + i + "] " + testInputData.sites[i] + " TIMEOUT" +
               ((tries-1)?"\n":" [FINAL_RESULT]\n"));
        /* unexpected error */
        else {
          dump(">>> TEST [" + i + "] " + testInputData.sites[i] + " UNKNOWN_FAILURE" +
               ((tries-1)?"\n":" [FINAL_RESULT]\n"));
          throw e;
        }
      }

      tries--; // one less try
    }

    dump(">>> TEST_DEBUG [" + i + "] " + testInputData.sites[i] + " FINISH\n");
  }
}

