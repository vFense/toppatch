// Filename: router.js
define(
	['backbone', 'app' ],
	function (Backbone, app) {
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
				// Start the Dashboard Nav Bar
				this.navBar = new NavBar.View();
				
				// Create a new ViewManager with #dashboard-view as its target element
				// All views sent to the ViewManager will render in the target element
                this.vent = app.vent;
				this.viewManager = new app.ViewManager('#dashboard-view');
			},
			home: function () {
				// Set the active Dashboard Nav Button
				this.navBar.setActive({target:$('#dashboardNav a[href$="dashboard"]')});
				
				// Update the main dashboard view
				this.viewManager.showView({ el: 'Home', render: function () {return true; }, close: function () { return true; }});
			},
			showPatchAdmin: function () {
				// Set the active Dashboard Nav Button
				this.navBar.setActive({target:$('#dashboardNav a[href$="patchAdmin"]')});
				
				// Update the main dashboard view
				this.viewManager.showView({ el: 'Patch Admin', render: function () {return true; }, close: function () { return true; }});
			},
			defaultAction: function (other) {
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
