/*
	Copyright (c) 2004-2008, The Dojo Foundation All Rights Reserved.
	Available via Academic Free License >= 2.1 OR the modified BSD license.
	see: http://dojotoolkit.org/license for details
*/


dojo._xdResourceLoaded(function(dojo, dijit, dojox){
return {depends: [["provide", "dojox.highlight.languages._static"],
["require", "dojox.highlight.languages.cpp"],
["require", "dojox.highlight.languages.delphi"]],
defineResource: function(dojo, dijit, dojox){if(!dojo._hasResource["dojox.highlight.languages._static"]){ //_hasResource checks added by build. Do not use _hasResource directly in your code.
dojo._hasResource["dojox.highlight.languages._static"] = true;
dojo.provide("dojox.highlight.languages._static");

/* common static languages */
dojo.require("dojox.highlight.languages.cpp")
// dojo.require("dojox.highlight.languages.java");
dojo.require("dojox.highlight.languages.delphi");

}

}};});
