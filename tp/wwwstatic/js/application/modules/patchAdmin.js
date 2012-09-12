define(
	['jquery', 'backbone', 'text!templates/patchAdmin.html' ],
	function ($, Backbone, myTemplate) {
		"use strict";
		var exports = {};
		exports.Model = Backbone.Model.extend({});
		exports.View = Backbone.View.extend({
			initialize: function () {
				this.template = myTemplate;
			},
			render: function () {
				var tmpl = _.template(this.template),
					that = this;

				this.$el.html('');

				this.$el.append(tmpl());

				return this;
			}
		});
		return exports;
	}
);