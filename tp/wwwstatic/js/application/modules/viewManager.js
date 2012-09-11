define(
	['jquery', 'backbone'],
	function ($, Backbone) {
		"use strict";

		// Zombie Prevention Part 1
		// Add close function to Backbone.View to prevent "Zombies"
		// Inspired by: Derick Bailey
		// See: http://bit.ly/odAfKo
        _.extend(Backbone.View.prototype, {
            close: function () {
                if (this.beforeClose) {
                    this.beforeClose();
                }
                this.remove();
                this.unbind();
            }
        });

		// Zombie Prevention Part 2
		// Object to manage transitions between views
		// Inspired by: Derick Bailey
		// See: http://bit.ly/odAfKo
		var viewManager = function () {
			var that = this;
			that.showView = function (selector, view) {
				if (this.currentView) {
					this.currentView.close();
				}
                $(selector).html(view.render().el);
				this.currentView = view;
				return view;
			};
		};

		return viewManager;
	}
);
