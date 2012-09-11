// Filename: router.js
define(
	['jquery', 'backbone', 'app' ],
	function ($, Backbone, app) {
		"use strict";
		var AppRouter = Backbone.Router.extend({
			routes: {
				// Dashboard
				'':           'home',
				'dashboard':  'home',

				// Patch Routes
				'patchAdmin': 'showPatchAdmin',

				// Default
				'*other':     'defaultAction'
			},
			initialize: function () {
				// Create a new ViewManager with #dashboard-view as its target element
				// All views sent to the ViewManager will render in the target element
                this.vent = app.vent;
				this.viewManager = new app.ViewManager('#dashboard-view');
			},
			home: function () {
                this.vent.trigger('nav:dashboard');

				// Update the main dashboard view
				this.viewManager.showView({ el: 'Home', render: function () { return true; }, close: function () { return true; }});
			},
			showPatchAdmin: function () {
                this.vent.trigger('nav:patchAdmin');

				// Update the main dashboard view
				this.viewManager.showView({ el: 'Patch Admin', render: function () { return true; }, close: function () { return true; }});
			},
			defaultAction: function (other) {
                this.vent.trigger('nav:404');

				this.viewManager.showView({ el: '404: Not Found', render: function () { return true; }, close: function () {  return true; }});
			}
		});

		return {
			initialize: function () {
				this.app_router = new AppRouter();
				Backbone.history.start();
			}
		};
	}
);
