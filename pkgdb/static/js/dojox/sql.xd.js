/*
	Copyright (c) 2004-2008, The Dojo Foundation All Rights Reserved.
	Available via Academic Free License >= 2.1 OR the modified BSD license.
	see: http://dojotoolkit.org/license for details
*/


dojo._xdResourceLoaded(function(dojo, dijit, dojox){
return {depends: [["provide", "dojox.sql"],
["require", "dojox.sql._base"]],
defineResource: function(dojo, dijit, dojox){if(!dojo._hasResource["dojox.sql"]){ //_hasResource checks added by build. Do not use _hasResource directly in your code.
dojo._hasResource["dojox.sql"] = true;
dojo.provide("dojox.sql"); 
dojo.require("dojox.sql._base");

}

}};});