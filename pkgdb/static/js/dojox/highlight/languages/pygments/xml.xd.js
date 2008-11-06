/*
	Copyright (c) 2004-2008, The Dojo Foundation All Rights Reserved.
	Available via Academic Free License >= 2.1 OR the modified BSD license.
	see: http://dojotoolkit.org/license for details
*/


dojo._xdResourceLoaded(function(dojo, dijit, dojox){
return {depends: [["provide", "dojox.highlight.languages.pygments.xml"],
["require", "dojox.highlight._base"]],
defineResource: function(dojo, dijit, dojox){if(!dojo._hasResource["dojox.highlight.languages.pygments.xml"]){ //_hasResource checks added by build. Do not use _hasResource directly in your code.
dojo._hasResource["dojox.highlight.languages.pygments.xml"] = true;
dojo.provide("dojox.highlight.languages.pygments.xml");

dojo.require("dojox.highlight._base");
dojox.highlight.languages.pygments.xml = {a: 1};
dojox.highlight.languages.xml = {
	defaultMode: {
		contains: [
			"name entity",
			"comment", "comment preproc",
			"_tag"
		]
	},
	modes: [
		// comments
		{
			className: "comment",
			begin: "<!--", end: "-->"
		},
		{
			className: "comment preproc",
			begin: "\\<\\!\\[CDATA\\[", end: "\\]\\]\\>"
		},
		{
			className: "comment preproc",
			begin: "\\<\\!", end: "\\>"
		},
		{
			className: "comment preproc",
			begin: "\\<\\?", end: "\\?\\>",
			relevance: 5
		},

		// strings
		{
			className: "string",
			begin: "'", end: "'",
			illegal: "\\n",
			relevance: 0
		},
		{
			className: "string",
			begin: '"', 
			end: '"',
			illegal: "\\n",
			relevance: 0
		},
		
		// names
		{
			className: "name entity",
			begin: "\\&[a-z]+;", end: "^"
		},
		{
			className: "name tag",
			begin: "\\b[a-z0-9_\\:\\-]+\\b", end: "^"
		},
		{
			className: "name attribute",
			begin: "\\b[a-z0-9_\\:\\-]+=", end: "^",
			relevance: 0
		},
		
		
		{
			className: "_tag",
			begin: "\\<", end: "\\>",
			contains: ["name tag", "name attribute", "string"]
		},
		{
			className: "_tag",
			begin: "\\</", end: "\\>",
			contains: ["name tag"]
		}
	]
};

}

}};});
