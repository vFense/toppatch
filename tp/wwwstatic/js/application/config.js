require.config({
	// Initialize the app with the main application file
	deps: ['main'],

	paths: {
		// Create shortcuts
		// i.e. Use 'jquery' insteaad of typing out 'libs/jquery/jquery-1.8.1.min'
		jquery:             '../libs/jquery/jquery-1.8.1',
		'jquery.ui':        '../libs/jquery-ui/jquery-ui.custom.min',
		'jquery.bootstrap': '../libs/bootstrap/bootstrap.min',
		'underscore':       '../libs/underscore/underscore',
		'backbone':         '../libs/backbone/backbone',
		d3:                 '../libs/d3/d3.v2.min',
		text:				'../libs/require/plugins/text'
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
