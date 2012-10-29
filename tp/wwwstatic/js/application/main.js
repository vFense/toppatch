require(
    ['jquery', 'backbone', 'app'],
    function ($, Backbone, app) {
        "use strict";

        var User = {},
            userSettings,
            deferred, userName;
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

        // Deferred object resolved when header is fully rendered.
        deferred = new $.Deferred();

        // Load header, render it, and then render the nav buttons
        require(['modules/pageHeader', 'modules/navBar'], function (PageHeader, DashNav) {
            var pageHeader = new PageHeader.View();
            $('body').prepend(pageHeader.render().$el);
            app.views.dashNav = new (DashNav.View.extend({
                onRender: function () { deferred.resolve(); }
            }))({
                el: $('<ul>').addClass('nav').appendTo(pageHeader.$('#dashboardNav'))
            });
        });

        // Load footer and render it
        require(['modules/pageFooter'], function (PageFooter) {
            var pageFooter = new PageFooter.View();
            $('body').append(pageFooter.render().$el);
        });

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
););
