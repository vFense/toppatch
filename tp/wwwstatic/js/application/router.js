// Filename: router.js
	"use strict";
	var AppRouter = Backbone.Router.extend({
		routes: {
			// Patch Routes
			'patchAdmin':            'showPatchAdmin',
			'patchAdmin/installed':  'showInstalledPatchAdmin',
			'patchAdmin/hidden':     'showHiddenPatchAdmin',
			'patchAdmin/detail/:id': 'showPatchDetail',
define(
	['backbone', 'modules/viewManager', 'modules/navBar' ],
	function (Backbone, ViewManager, NavBar) {

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