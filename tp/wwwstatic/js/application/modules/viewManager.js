define(
	['underscore', 'backbone'],
	function (_, Backbone) {
		"use strict";

		// Zombie Prevention Part 1
		// Add close function to Backbone.View to prevent "Zombies"
		// By: Derick Bailey
		// See: http://bit.ly/odAfKo
		Backbone.View.prototype.close = function () {
			this.remove();
			this.unbind();
			if (this.onClose) {
				this.onClose();
			}
		};

		// Zombie Prevention Part 2
		// Object to manage transitions between views
		// By: Derick Bailey
		// See: http://bit.ly/odAfKo
		var viewManager = function (target) {
			var that = this;
			that.target = target;
			that.showView = function (view) {
				if (this.currentView) {
					this.currentView.close();
				}
				this.currentView = view;
				this.currentView.render();
				$(that.target).html(this.currentView.el);
			};
		};

		return viewManager;
	}
);
