"use strict";

var common = require("../mytests/common");

var setupModule = common.setupModule;
var teardownModule = common.teardownModule;

// Enable tracking protection.
common.myprefs["privacy.trackingprotection.enabled"] = true;

var testSampleTestcase = function() {
  return common.testSampleTestcase();
}
