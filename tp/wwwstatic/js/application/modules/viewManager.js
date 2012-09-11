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
		var ViewManager = function (options) {
			var that = this,
                final,
                lastSelect;
            that.selector = 'body';
            that.$selector = undefined;
            that.set = function (opts) { _.extend(that, opts); final(); };
            that.get = function (name) { return that[name]; };
			that.showView = function (view) {
				if (this.currentView) {
					this.currentView.close();
				}
                that.$selector.html(view.render().el);
				this.currentView = view;
				return view;
			};
            _.extend(that, options);

            // Self invoking function for final set up
            final = (function () {
                if ($.type(that.selector) === 'string' && that.selector !== lastSelect) {
                    that.$selector = $(that.selector);
                    lastSelect = that.selector;
                }
            }());
		};

        return ViewManager;
	}
);
