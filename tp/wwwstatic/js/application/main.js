require(
    ['jquery', 'backbone', 'app'],
    function ($, Backbone, app) {
        "use strict";

        var User = {},
            userSettings,
            userName,
            deferred;

        $.ajax({
            url: '/api/userInfo',
            dataType: 'json',
            async: false,
            success: function (json) {
                userSettings = json;
                userName = userSettings.name;
                if (localStorage.getItem(userName) === null) {
                    User.Model = Backbone.Model.extend({
                        defaults: {
                            name: userName,
                            show: {
                                brandHeader: true,
                                dashNav: true,
                                copyFooter: true
                            },
                            widgets: {
                                'graph': ['pie', 'bar', 'summary'],
                                'spans': [6, 6, 12],
                                'titles': ['Patches by Severity', 'Nodes in Network by OS', 'Summary Charts']
                            }
                        }
                    });
                    window.User = new User.Model();
                    localStorage.setItem(userName, JSON.stringify(window.User));
                } else {
                    var test = JSON.parse(localStorage.getItem(userName));
                    User.Model = Backbone.Model.extend({
                        defaults: {
                            name: test.name,
                            show: test.show,
                            widgets: test.widgets,
                            access: test.access
                        }
                    });
                    window.User = new User.Model();
                }

            }
        });

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
