require.config({
    // Initialize the app with the main application file
    deps: ['main'],

    paths: {
        // Create shortcuts
        // i.e. Use 'jquery' insteaad of typing out 'libs/jquery/jquery-1.8.1.min'
        'jquery'            : '../libs/jquery/jquery-1.8.1',
        'jquery.ui'         : '../libs/jquery-ui/jquery-ui.custom.min',
        'jquery.bootstrap'  : '../libs/bootstrap/bootstrap.min',
        'underscore'        : '../libs/underscore/underscore',
        'backbone'          : '../libs/backbone/backbone',
        'd3'                : '../libs/d3/d3.v2',
        'text'              : '../libs/require/plugins/text',
        
        // jQuery.ui modules
        'jquery.ui.Core'        : '../libs/jquery-ui/dev/jquery.ui.Core',
		'jquery.ui.Widget'      : '../libs/jquery-ui/dev/jquery.ui.Widget',
		'jquery.ui.Mouse'       : '../libs/jquery-ui/dev/jquery.ui.Mouse',
		'jquery.ui.Position'    : '../libs/jquery-ui/dev/jquery.ui.Position',
		'jquery.ui.Draggable'   : '../libs/jquery-ui/dev/jquery.ui.Draggable',
		'jquery.ui.Droppable'   : '../libs/jquery-ui/dev/jquery.ui.Droppable',
		'jquery.ui.Resizable'   : '../libs/jquery-ui/dev/jquery.ui.Resizable',
		'jquery.ui.Selectable'  : '../libs/jquery-ui/dev/jquery.ui.Selectable',
		'jquery.ui.Sortable'    : '../libs/jquery-ui/dev/jquery.ui.Sortable',
		'jquery.ui.Accordion'   : '../libs/jquery-ui/dev/jquery.ui.Accordion',
		'jquery.ui.Autocomplete': '../libs/jquery-ui/dev/jquery.ui.Autocomplete',
		'jquery.ui.Button'      : '../libs/jquery-ui/dev/jquery.ui.Button',
		'jquery.ui.Dialog'      : '../libs/jquery-ui/dev/jquery.ui.Dialog',
		'jquery.ui.Slider'      : '../libs/jquery-ui/dev/jquery.ui.Slider',
		'jquery.ui.Tabs'        : '../libs/jquery-ui/dev/jquery.ui.Tabs',
		'jquery.ui.Datepicker'  : '../libs/jquery-ui/dev/jquery.ui.Datepicker',
		'jquery.ui.Progressbar' : '../libs/jquery-ui/dev/jquery.ui.Progressbar'
    },

    shim: {
        'jquery.ui': {
            deps: ['jquery'],    // jQuery UI depends on jQuery
            exports: 'jQuery'
        },
        'jquery.bootstrap': {
            deps: ['jquery'],    // Bootstrap depends on jQuery
            exports: 'jQuery'
        },
        'backbone': {
            deps: ['jquery', 'underscore'],    // Backbone depends on jQuery and Underscore
            exports: 'Backbone'
        },
        'd3': {
            exports: 'd3'
        },
        
        // jQuery.ui modules
        'jquery.ui.Core'        : {exports: 'jQuery'},
        'jquery.ui.Widget'      : {exports: 'jQuery'},
        'jquery.ui.Mouse'       : {exports: 'jQuery', deps: ['jquery.ui.Core', 'jquery.ui.Widget']},
        'jquery.ui.Position'    : {exports: 'jQuery'},
        'jquery.ui.Draggable'   : {exports: 'jQuery', deps: ['jquery.ui.Core', 'jquery.ui.Widget', 'jquery.ui.Mouse']},
        'jquery.ui.Droppable'   : {exports: 'jQuery', deps: ['jquery.ui.Core', 'jquery.ui.Widget', 'jquery.ui.Mouse', 'jquery.ui.Draggable']},
        'jquery.ui.Resizable'   : {exports: 'jQuery', deps: ['jquery.ui.Core', 'jquery.ui.Widget', 'jquery.ui.Mouse']},
        'jquery.ui.Selectable'  : {exports: 'jQuery', deps: ['jquery.ui.Core', 'jquery.ui.Widget', 'jquery.ui.Mouse']},
        'jquery.ui.Sortable'    : {exports: 'jQuery', deps: ['jquery.ui.Core', 'jquery.ui.Widget', 'jquery.ui.Mouse']},
        'jquery.ui.Accordion'   : {exports: 'jQuery', deps: ['jquery.ui.Core', 'jquery.ui.Widget']},
        'jquery.ui.Autocomplete': {exports: 'jQuery', deps: ['jquery.ui.Core', 'jquery.ui.Widget', 'jquery.ui.Position']},
        'jquery.ui.Button'      : {exports: 'jQuery', deps: ['jquery.ui.Core', 'jquery.ui.Widget']},
        'jquery.ui.Dialog'      : {exports: 'jQuery', deps: ['jquery.ui.Core', 'jquery.ui.Widget', 'jquery.ui.Position']},
        'jquery.ui.Slider'      : {exports: 'jQuery', deps: ['jquery.ui.Core', 'jquery.ui.Widget', 'jquery.ui.Mouse']},
        'jquery.ui.Tabs'        : {exports: 'jQuery', deps: ['jquery.ui.Core', 'jquery.ui.Widget']},
        'jquery.ui.Datepicker'  : {exports: 'jQuery', deps: ['jquery.ui.Core']},
        'jquery.ui.Progressbar' : {exports: 'jQuery', deps: ['jquery.ui.Core', 'jquery.ui.Widget']}
    }
});
