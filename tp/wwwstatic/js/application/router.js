// Filename: router.js
define([
	'jquery',
	'underscore',
	'backbone'
], function ($, _, Backbone) {
	"use strict";
	var AppRouter = Backbone.Router.extend({
		routes: {
			// Patch Routes
			'patchAdmin':            'showPatchAdmin',
			'patchAdmin/installed':  'showInstalledPatchAdmin',
			'patchAdmin/hidden':     'showHiddenPatchAdmin',
			'patchAdmin/detail/:id': 'showPatchDetail',

			// Default/Dashboard
			'dashboard': 'defaultAction',
			'*other':  'defaultAction'
		},
		showPatchAdmin: function () {
			console.log('show patchAdmin');
		},
		showInstalledPatchAdmin: function () {
		},
		showHiddenPatchAdmin: function () {
		},
		showPatchDetail: function () {
		},
		defaultAction: function (other) {
			if(other !== '') { console.log('>'+other+'<'); }
			console.log('show default');
		}
	}),
		initialize = function () {
			var app_router = new AppRouter();
			Backbone.history.start();
		};
	return {
		initialize: initialize
	};
});