require(
    ['jquery', 'backbone', 'app'],
    function ($, Backbone, app) {
        "use strict";

        var User = {},
            userSettings,
            userName,
            deferred;

        app.getUserSettings();

        // Deferred object resolved after header and footer render.
        deferred = new $.Deferred();
        // Load and render page base page elements
        // Insert nav bar to header.
        require(
            ['modules/pageHeader', 'modules/pageFooter', 'modules/navBar'],
            function (PageHeader, PageFooter, NavBar) {
                var pageHeader = new PageHeader.View(),
                    pageFooter = new PageFooter.View(),
                    navBar = new NavBar.View({
                        el: $('<ul>').addClass('nav')
                    });

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
        deferred.done(function () {
            require(['router'], function (Router) {
                Router.initialize();
            });
        });
    }
);
