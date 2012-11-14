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
                            {text: 'Approve Nodes', href: 'testAdmin/nodes'},
                            {text: 'Add Time Block', href: 'testAdmin/timeblock'},
                            {text: 'See Time Blocks', href: 'testAdmin/listblocks'}
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

                    var template = _.template(this.template),
                        $el = this.$el,
                        $header,
                        $content,
                        $footer;

                    $el.empty();
                    $el.html(template({}));

                    $header = $el.find('.modal-header');
                    $content = $el.find('.modal-body');
                    $footer = $el.find('.modal-footer .content');

                    $header.addClass('tabs').html(this.navigation.render().el);

                    if (this._contentView) {
                        $content.empty().html(this._contentView.el);
                    }

                    if (this.onRender !== $.noop) { this.onRender(); }

                    return this;
                },

                setContentView: function (view) {
                    // Close the last content view if any.
                    if (this._contentView) {
                        var popover = this._contentView.$el.find('#dow');
                        if (popover.data('popover')) { popover.popover('destroy'); }
                        this._contentView.close();
                    }

                    if (view instanceof Backbone.View) {
                        this._contentView = view;
                        this._contentView.render();
                        this._contentView.delegateEvents();
                    } else {
                        this._contentView = null;
                    }

                    this.render();

                    return this;
                },

                getContentView: function () {
                    return this._contentView;
                },

                beforeClose: function () {
                    if (this.navigation) {
                        this.navigation.close();
                    }
                    if (this._contentView) {
                        this._contentView.close();
                    }
                }
            })
        };
    }
);
