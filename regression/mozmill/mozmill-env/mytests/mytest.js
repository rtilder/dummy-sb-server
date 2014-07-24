"use strict";

// Iterates over a list of URLs (testInputData.sites) and
// opens them one by one in the same tab. It waits until
// each page loads before moving on to the next URL.

// Include required modules
var prefs = require("../../mozmill-tests/firefox/lib/prefs");
var tabs = require("../../mozmill-tests/firefox/lib/tabs");
var addons = require("../../mozmill-tests/firefox/lib/addons");

// Used to find and enable/disable ABP on demand
const ABP_ADDON = {
  name: "Adblock Plus",
  id: "{d10d0bf8-f5b5-c8b4-a8b2-2b9879e08c5d}"
};

// Are we blocking stuff for this test?
// true -> either using ABP or trackingprotection (see myprefs)
// false -> neither
const BLOCK_STUFF = true; // * EDIT THIS *

const myprefs = {
"privacy.trackingprotection.enabled": BLOCK_STUFF && true, // * EDIT THIS *
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

// Setup for the test
var setupModule = function(aModule)
{
  for (var pref in myprefs)
    prefs.preferences.setPref(pref, myprefs[pref]);

  aModule.controller = mozmill.getBrowserController();
  aModule.addonsManager = new addons.AddonsManager(aModule.controller);
}

function teardownModule(aModule) {
  for (var pref in myprefs)
    prefs.preferences.clearUserPref(pref);
}

// Run the test
var testSampleTestcase = function()
{
  addonsManager.open({type: "shortcut"});
  // Switch to the extension pane
  var category = addonsManager.getCategoryById({id: "extension"});
  /* if we are not in the correct category already, do switch */
  var categories = addonsManager.getElement({type: "categoriesList"});
  if (categories.getNode().getAttribute("last-selected")
      != "category-extension") {
    addonsManager.setCategory({category: category});
  }
  /* get the list of items in this category */
  var addonsList = addonsManager.getElement({type: "addonsList"});
  expect.equal(addonsList.getNode().localName, "richlistbox",
               "Correct node type for list of add-ons");

  /* find ABP */
  var addon = addonsManager.getAddons({attribute: "name",
                                       value: ABP_ADDON.name})[0];
  expect.equal(addon.getNode().getAttribute('value'), ABP_ADDON.id,
               "Add-on has the correct ID");
  expect.equal(addon.getNode().getAttribute('type'), "extension",
               "Add-on is of type 'extension'");

  // Firefox tracking protection is ON or we are not blocking stuff, do DISABLE ABP
  if (prefs.preferences.getPref("privacy.trackingprotection.enabled", false) == true || BLOCK_STUFF == false) {
    addonsManager.disableAddon({addon: addon});
  }
  // Firefox tracking protection is OFF, do ENABLE ABP
  else {
    addonsManager.enableAddon({addon: addon});
  }


dump("- INFO: Will block stuff? " + BLOCK_STUFF + "\n");
dump("- INFO: privacy.tracking.protection.enabled " + (prefs.preferences.getPref("privacy.trackingprotection.enabled", false) == true) + "\n");
dump("- INFO: AdblockPlus " + !(prefs.preferences.getPref("privacy.trackingprotection.enabled", false) == true || BLOCK_STUFF == false) + "\n");

  var testInputData = require("testInputData");

dump("- INFO: READY\n");

  // start with no tabs
  //tabs.closeAllTabs(controller);

  for (var i = 0; i < testInputData.sites.length; i++)
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
