define(
	['jquery', 'backbone','text!templates/navButton.html'],
	function ($, Backbone, buttonTemplate) {
		"use strict";
		var navButton = {
			Model: Backbone.Model.extend({
				defaults: {
					active: false
				}
			}),
			View : Backbone.View.extend({
				tagName: "li",
				className: "",
				template: buttonTemplate,
				events: {},
				initialize: function () {},
				render: function () {
					var tmpl = _.template(this.template);
					$(this.el).html(tmpl(this.model.toJSON()));
					return this;
				}
			})
		};
		return navButton;
	}
);