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
			    this.viewManager = new app.ViewManager();
			},
			home: function () {
                var that = this;
                this.vent.trigger('nav', 'dashboard');

				// Update the main dashboard view
                require(['modules/mainDash'], function (myView) {
                    var view = new myView.View();
                    that.viewManager.showView('#dashboard-view', view);
                });
			},
			showPatchAdmin: function () {
                var that = this;
                this.vent.trigger('nav', 'patchAdmin');

				// Update the main dashboard view
                this.showView({ el: 'Patch Admin Page', render: function () { return this.el; }, close: function () {  return true; }});
			},
			defaultAction: function (other) {
                var that = this;
                this.vent.trigger('nav', '404');

				this.showView({ el: '404: Not Found', render: function () { return true; }, close: function () {  return true; }});
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
