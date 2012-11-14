define(
    ['jquery', 'underscore', 'backbone', 'app', 'modules/tabNavigation', 'text!templates/modals/admin/main.html'],
    function ($, _, Backbone, app, tabNav, myTemplate) {
        "use strict";
        return {
            View: Backbone.View.extend({
                className: 'admin-main-view',
                initialize: function () {
                    this.template = myTemplate;
                    this.navigation = new tabNav.View({
                        tabs: [
                            {text: 'General', href: 'testAdmin'},
                            {text: 'Nodes', href: 'testAdmin/nodes'}
                        ]
                    });
                },

                beforeRender: function () {
                    this.rendered = false;
                },
                onRender: function () {
                    // update the active tab
                    this.navigation.setActive(app.router.getCurrentFragment());

                    this.rendered = true;
                },
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var that = this,
                        template = _.template(this.template),
                        $el = this.$el,
                        $header,
                        $content,
                        $footer;

                    $el.empty();
                    $el.html(template({}));

                    $header = $el.find('.modal-header');
                    $content = $el.find('.modal-body');
                    $footer = $el.find('.modal-footer .content');
                    if (this.onRender !== $.noop) { this.onRender(); }


                    return this;
                }
            })
        };
    }
);
