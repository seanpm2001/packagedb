dojo._xdResourceLoaded(function(dojo, dijit, dojox){
return {depends: [["provide", "tests.back"]],
defineResource: function(dojo, dijit, dojox){if(!dojo._hasResource["tests.back"]){ //_hasResource checks added by build. Do not use _hasResource directly in your code.
dojo._hasResource["tests.back"] = true;
dojo.provide("tests.back");
if(dojo.isBrowser){
	doh.registerUrl("tests.back", dojo.moduleUrl("tests", "back.html"));
}

}

}};});