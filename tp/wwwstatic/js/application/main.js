require(
    ['jquery', 'backbone', 'app'],
    function ($, Backbone, app) {
        "use strict";

        // Deferred object resolved after header and footer render.
        var deferred = new $.Deferred();

        app.getUserSettings();

        // Load and render header and footer elements
        require(
            ['modules/pageHeader', 'modules/pageFooter', 'modules/navBar'],
            function (PageHeader, PageFooter, NavBar) {
                var pageHeader = new PageHeader.View(),
                    pageFooter = new PageFooter.View(),
                    navBar = new NavBar.View();

                // Prepend header to body
                // Append footer to body
                $('body').prepend(pageHeader.render().$el)
                         .append(pageFooter.render().$el);

                // Insert nav bar into header
                pageHeader.$('#dashboardNav').append(navBar.render().$el);

                // resolve the deferred object
                deferred.resolve();
            }
        );

        // Listen for event to change the page title
        app.vent.on("domchange:title", function (title) {
            if (title && title.trim() !== '') {
                app.$doc.attr('title', app.title + ': ' + title);
            } else {
                app.$doc.attr('title', app.title);
            }
        });

        // When the above Deferred object is resolved, start the router
        require(['router'], function (Router) {
            deferred.done(function () {
                Router.initialize();
            });
        });
    }
);
