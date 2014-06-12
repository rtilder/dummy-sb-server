"use strict";

// Iterates over a list of URLs (testInputData.sites) and 
// opens them one by one in the same tab. It waits until 
// each page loads before moving on to the next URL. 

// Include required modules
var tabs = require("../../mozmill-tests/firefox/lib/tabs");

//var {assert, expect} = require("../../mozmill-tests/lib/assertions");

// Setup for the test
var setupModule = function(aModule) 
{
  aModule.controller = mozmill.getBrowserController();
}

// Run the test
var testSampleTestcase = function() 
{
  var testInputData = require("testInputData");

  // start with no tabs
  tabs.closeAllTabs(controller);

  for (var i = 0; i < testInputData.sites.length; i++)
  {
    controller.open(testInputData.sites[i])

    // wait for page to load before trying to load next URL in this loop
    try {
      controller.waitForPageLoad(15000); // 15 sec

      dump(">>> TEST [" + i + "] " + testInputData.sites[i] + " OK\n");
    } 
    catch (e)
    {
      /* we expect AssertionError when waitForPageLoad() times out */
      if (e instanceof errors.AssertionError)
        dump(">>> TEST [" + i + "] " + testInputData.sites[i] + " TIMEOUT\n");
      /* unexpected error */
      else 
        throw e;
    }
  }
}
