require.config({
	paths: {
		// libs
		// Create shortcuts
		// i.e. Use 'jquery' insteaad of 'libs/jquery/jquery-1.8.0.min'
		jquery:             'libs/jquery/jquery-1.8.0.min',
		'jquery.ui':        'libs/jquery-ui/jquery-ui.custom.min',
		'jquery.bootstrap': 'libs/bootstrap/bootstrap.min',
		'underscore':       'libs/underscore/underscore-min',
		'backbone':         'libs/backbone/backbone-min',
		d3:                 'libs/d3/d3.v2.min'
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
], function ($, Backbone) {
], function ($, Backbone, Router) {
	"use strict";

	var user = {},
		Dashboard,
		dashboard,
		dashNav = {
			Model: {},
			View: {}
		};

	user.name = 'Luis';
	user.access = [
		{ name: 'Dashboard', href: '#dashboard' },
		{ name: 'Patches', href: '#patchAdmin' }
	];

	dashNav.Model = Backbone.Model.extend({
		defaults: {
			active: false
		},
	});

	Dashboard = Backbone.Collection.extend({
		model: dashNav.Model
	});

	dashNav.View.Button = Backbone.View.extend({
		tagName: "li",
		className: "",
		template: $('#dashboardNavButton').html(),

		events: {
			"click" : "toggleActive"
		},
		
		initialize: function () {
			this.model.bind('change', this.render, this);
			this.model.bind('destroy', this.remove, this);
		},

		render: function () {
			var tmpl = _.template(this.template);
			$(this.el).html(tmpl(this.model.toJSON()));
			return this;
		},
		
		toggleActive: function () {
			console.log("event");
			$(this.el).toggleClass('active');
		}
	});

	dashNav.View.Main = Backbone.View.extend({
		el: $("<ul/>").addClass('nav').appendTo('#dashboardNav'),

		initialize: function () {
			this.collection = new Dashboard(user.access);
			this.render();
		},

		render: function () {
			var that = this;
			this.$el.html('');
			_.each(this.collection.models, function (item) {
				that.renderDashButton(item);
			}, this);
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

		renderDashButton: function (item) {
			console.log(item);
			var buttonView = new dashNav.View.Button({
				model: item
			});
			this.$el.append(buttonView.render().el);
		user: {
			name: 'Luis',
			access: [
				{ name: 'Dashboard', href: '#dashboard' },
				{ name: 'Patches', href: '#patchAdmin' }
			]
		}
	});

	dashboard = new dashNav.View.Main();
});
/*
define([
	// Ensure the following resources are loaded
	// before executing the next function
	'jquery',
	'backbone', // Backbone will load underscore for us
	'router'
], function ($, Backbone, Router) {
	"use strict";
	Router.initialize();
});
*/