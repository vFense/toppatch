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
                userName = userSettings['name'];
                //localStorage.clear();
                if(localStorage.getItem(userName) === null) {
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
                                'titles': ['Nodes in Network by OS', 'Nodes in Network by OS', 'Summary Charts']
                            },
                            access: [
                                { name: 'Dashboard', href: '#dashboard', active: false },
                                { name: 'Nodes', href: '#nodes', active: false },
                                { name: 'Patches', href: '#patches', active: false }
                            ]
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
                            spans: test.spans,
                            access: test.access
                        }
                    });
                    window.User = new User.Model();
                }

            }
        });

        deferred = new $.Deferred();
        require(['modules/pageHeader', 'modules/navBar'], function (PageHeader, DashNav) {
            var pageHeader = app.views.pageHeader = new PageHeader.View();
            $('body').prepend(pageHeader.render().$el);
            app.views.dashNav = new (DashNav.View.extend({
                onRender: function () { deferred.resolve(); }
            }))({
                el: $('<ul>').addClass('nav').appendTo(pageHeader.$('#dashboardNav'))
            });
        });
        require(['modules/pageFooter'], function (PageFooter) {
            var pageFooter = new PageFooter.View();
            $('body').append(pageFooter.render().$el);
        });

        app.vent.on("domchange:title", function (title) {
            app.$doc.attr('title', app.title + ': ' + title);
        });

        deferred.done(function () {
            require(['router'], function (Router) {
                Router.initialize();
            });
        });
    }
);