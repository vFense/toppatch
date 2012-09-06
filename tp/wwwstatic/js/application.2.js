require.config({
	paths: {
		// Create shortcuts
		// i.e. Use 'jquery' insteaad of 'libs/jquery/jquery-1.8.0.min'
		jquery:             'libs/jquery/jquery-1.8.0.min',
		'jquery.ui':        'libs/jquery-ui/jquery-ui.custom.min',
		'jquery.bootstrap': 'libs/bootstrap/bootstrap.min',
		'underscore':       'libs/underscore/underscore-min',
		'backbone':         'libs/backbone/backbone-min',
		d3:                 'libs/d3/d3.v2.min',
		text:				'libs/require/plugins/text',
		app:				'application',
		modules:			'application/modules',
		templates:			'application/templates'
	},
	shim: {
		'jquery.ui': {
			deps: ['jquery'],	// jQuery UI depends on jQuery
			exports: 'jquery'
		},
		'jquery.bootstrap': {
			deps: ['jquery'],	// Bootstrap depends on jQuery
			exports: 'jquery'
		},
		'backbone': {
			deps: ['jquery', 'underscore'],	// Backbone depends on jQuery and Underscore
			exports: 'Backbone'
		}
	}
});

define([
	// Ensure the following resources are loaded
	// before executing the next function
	'jquery',
	'backbone', // Backbone will load underscore for us
	'application/router',
	'd3',
	'jquery.ui',
	'jquery.bootstrap'
], function ($, Backbone, Router) {
	"use strict";

	// Use TP locally to modify the global object
	var TP = window.TopPatch = {
		App: {
			// Semantic versioning
			// See: http://semver.org/
			version: "0.1.0",
			versionDescription: "Initial Development",
			dispatch: _.extend({}, Backbone.Events),
			options: {}
		},
		user: {
			name: 'Luis',
			access: [
				{ name: 'Dashboard', href: '#dashboard' },
				{ name: 'Patches', href: '#patchAdmin' }
			]
		}
	};

	Router.initialize();
});
