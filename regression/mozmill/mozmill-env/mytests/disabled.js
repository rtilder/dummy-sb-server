"use strict";

var common = require("../mytests/common");

// Iterates over a list of URLs (testInputData.sites) and
// opens them one by one in the same tab. It waits until
// each page loads before moving on to the next URL.

var setupModule = common.setupModule;
var teardownModule = common.teardownModule;
var testSampleTestcase = function() {
  dump("running sample\n");
  return common.testSampleTestcase();
}
