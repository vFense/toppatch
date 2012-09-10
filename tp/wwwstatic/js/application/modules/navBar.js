define(
	['jquery', 'backbone', 'app', './navButton'],
	function ($, Backbone, app, navButton) {
		"use strict";
		var NavBar = {
			ButtonSet: Backbone.Collection.extend({
				model: navButton.Model
			}),
			View: Backbone.View.extend({
				initialize: function () {
					this.collection =  new NavBar.ButtonSet(window.User.get('access'));
                    this.vent = app.vent;
                    this.vent.bind('all', this.setActive, this);
					this.render();
				},
                beforeRender: $.noop,
                onRender: $.noop,
				render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

					var that = this;
					this.$el.html('');
					_.each(this.collection.models, function (item) {
						that.renderButton(item);
					}, this);

                    if (this.onRender !== $.noop) { this.onRender(); }
					return this;
				},
				renderButton: function (item) {
					var buttonView = new navButton.View({
						model: item
					});
					this.$el.append(buttonView.render().el);
				},
				setActive: function (e) {
					// Check to make sure e and e.target are defined.
					if(e && e.target) {
						// The target should always be an anchor element
						// We want its parent li
						var $clicked = $(e.target).parent();
						
						// Check to see if the li element is part of this view's created element
						if ( $($clicked, this.$el).length === 1 ) {
							// If the li is not the active li, continue
							if(!$clicked.hasClass('active')) {
								// Set the li to active, and its siblings to not active
								$clicked.toggleClass('active', true).siblings().toggleClass('active',false);
							}
						}
					}
				}
			})
		};
		return NavBar;
	}
);