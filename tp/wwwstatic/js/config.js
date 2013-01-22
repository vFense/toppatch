require.config({
    paths: {
        // Create shortcuts
        // i.e. Use 'jquery' insteaad of typing out 'libs/jquery/jquery-1.8.1.min'

        // Application
        // ---------------------------------------------------------------------

        'app'       : 'application/app',
        'main'      : 'application/main',
        'router'    : 'application/router',
        'd3charts'  : 'application/d3charts',
        'modules'   : 'application/modules',
        'modals'    : 'application/modules/modals',
        'templates' : 'application/templates',
        'utilities' : 'application/utilities',

        // Libraries
        // ---------------------------------------------------------------------
        'jquery'            : 'libs/jquery/jquery',
        'jquery.bootstrap'  : 'libs/bootstrap/bootstrap.min',
        'underscore'        : 'libs/underscore/underscore',
        'backbone'          : 'libs/backbone/backbone',
        'respond'           : 'libs/respond/respond.src',
        'd3'                : 'libs/d3/d3.v2',

        // Library Plugins
        // ---------------------------------------------------------------------
        'text'              : 'libs/require/plugins/text',
        'bootstrap-modal'   : 'libs/backbone/plugins/bootstrap-modal',
        'Rickshaw'          : 'libs/rickshaw/rickshaw',
        'nvd3'              : 'libs/nvd3/nv.d3',

        // jQuery.ui Library
        // ---------------------------------------------------------------------
        'jquery.ui.core'        : 'libs/jquery-ui/dev/jquery.ui.core',
        'jquery.ui.widget'      : 'libs/jquery-ui/dev/jquery.ui.widget',
        'jquery.ui.mouse'       : 'libs/jquery-ui/dev/jquery.ui.mouse',
        'jquery.ui.position'    : 'libs/jquery-ui/dev/jquery.ui.position',
        'jquery.ui.draggable'   : 'libs/jquery-ui/dev/jquery.ui.draggable',
        'jquery.ui.droppable'   : 'libs/jquery-ui/dev/jquery.ui.droppable',
        'jquery.ui.resizable'   : 'libs/jquery-ui/dev/jquery.ui.resizable',
        'jquery.ui.selectable'  : 'libs/jquery-ui/dev/jquery.ui.selectable',
        'jquery.ui.sortable'    : 'libs/jquery-ui/dev/jquery.ui.sortable',
        'jquery.ui.accordion'   : 'libs/jquery-ui/dev/jquery.ui.accordion',
        'jquery.ui.autocomplete': 'libs/jquery-ui/dev/jquery.ui.autocomplete',
        'jquery.ui.button'      : 'libs/jquery-ui/dev/jquery.ui.button',
        'jquery.ui.datepicker'  : 'libs/jquery-ui/dev/jquery.ui.datepicker',
        'jquery.ui.dialog'      : 'libs/jquery-ui/dev/jquery.ui.dialog',
        'jquery.ui.menu'        : 'libs/jquery-ui/dev/jquery.ui.menu',
        'jquery.ui.progressbar' : 'libs/jquery-ui/dev/jquery.ui.progressbar',
        'jquery.ui.slider'      : 'libs/jquery-ui/dev/jquery.ui.slider',
        'jquery.ui.spinner'     : 'libs/jquery-ui/dev/jquery.ui.spinner',
        'jquery.ui.tabs'        : 'libs/jquery-ui/dev/jquery.ui.tabs',
        'jquery.ui.tooltip'     : 'libs/jquery-ui/dev/jquery.ui.tooltip'
    },

    shim: {
        'jquery.bootstrap': {
            deps: ['jquery'],    // Bootstrap depends on jQuery
            exports: 'jQuery'
        },
        'underscore': {
            exports: '_'
        },
        'backbone': {
            deps: ['jquery', 'underscore'],    // Backbone depends on jQuery and Underscore
            exports: 'Backbone'
        },
        'd3': {
            exports: 'd3'
        },
        'Rickshaw': {
            deps: ['d3'],
            exports: 'Rickshaw'
        },
        'nvd3': {
            deps: ['d3'],
            exports: 'nv'
        },

        // jQuery.ui modules ----
        // UI Core
        'jquery.ui.core'        : {exports: 'jQuery'},
        'jquery.ui.widget'      : {exports: 'jQuery'},
        'jquery.ui.mouse'       : {exports: 'jQuery', deps: ['jquery.ui.core', 'jquery.ui.widget']},
        'jquery.ui.position'    : {exports: 'jQuery'},

        // Interactions
        'jquery.ui.draggable'   : {exports: 'jQuery', deps: ['jquery.ui.core', 'jquery.ui.widget', 'jquery.ui.mouse']},
        'jquery.ui.droppable'   : {exports: 'jQuery', deps: ['jquery.ui.core', 'jquery.ui.widget', 'jquery.ui.mouse', 'jquery.ui.draggable']},
        'jquery.ui.resizable'   : {exports: 'jQuery', deps: ['jquery.ui.core', 'jquery.ui.widget', 'jquery.ui.mouse']},
        'jquery.ui.selectable'  : {exports: 'jQuery', deps: ['jquery.ui.core', 'jquery.ui.widget', 'jquery.ui.mouse']},
        'jquery.ui.sortable'    : {exports: 'jQuery', deps: ['jquery.ui.core', 'jquery.ui.widget', 'jquery.ui.mouse']},

        // Widgets
        'jquery.ui.accordion'   : {exports: 'jQuery', deps: ['jquery.ui.core', 'jquery.ui.widget']},
        'jquery.ui.autocomplete': {exports: 'jQuery', deps: ['jquery.ui.core', 'jquery.ui.widget', 'jquery.ui.position', 'jquery.ui.menu']},
        'jquery.ui.button'      : {exports: 'jQuery', deps: ['jquery.ui.core', 'jquery.ui.widget']},
        'jquery.ui.datepicker'  : {exports: 'jQuery', deps: ['jquery.ui.core']},
        'jquery.ui.dialog'      : {exports: 'jQuery', deps: ['jquery.ui.core.js', 'jquery.ui.widget.js', 'jquery.ui.mouse.js', 'jquery.ui.position.js', 'jquery.ui.draggable.js', 'jquery.ui.resizable.js', 'jquery.ui.button.js']},
        'jquery.ui.menu'        : {exports: 'jQuery', deps: ['jquery.ui.core', 'jquery.ui.widget', 'jquery.ui.position']},
        'jquery.ui.progressbar' : {exports: 'jQuery', deps: ['jquery.ui.core', 'jquery.ui.widget']},
        'jquery.ui.slider'      : {exports: 'jQuery', deps: ['jquery.ui.core', 'jquery.ui.widget', 'jquery.ui.mouse']},
        'jquery.ui.spinner'     : {exports: 'jQuery', deps: ['jquery.ui.core', 'jquery.ui.widget', 'jquery.ui.button']},
        'jquery.ui.tabs'        : {exports: 'jQuery', deps: ['jquery.ui.core', 'jquery.ui.widget']}
    },

    // Load Respond.js, bootstrap, and our main application file
    // Modernizr must be in the document head for proper operation in IE.
    deps: ['respond', 'jquery.bootstrap', 'main']
});
