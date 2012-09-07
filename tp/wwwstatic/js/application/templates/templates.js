var TEMPLATES = {
	"account/dropdownMenu": function () {
		"use strict";
		var template = [];

		template.push('<li class="dropdown">\n<a href="#" class="dropdown-toggle" data-toggle="dropdown">\n<i class="icon-user"></i><span>');
		template.push(' <%= name %> ');
		template.push('</span><i class="icon-caret-down"></i>\n</a>\n<ul class="dropdown-menu">\n<li><a href="javascript:;">My Profile</a></li>\n<li class="divider"></li>\n<li><a href="javascript:;">Logout</a></li>\n</ul>\n</li>\n');

		return template.join("");
	},
	"dashboard/navigation": function () {
		"use strict";
		var template = [];

		template.push('<nav class="clearfix">\n');
		template.push('<ul class="nav">\n<li class="active"><a href="#dashboard">Dashboard</a></li>\n');
		template.push('<% if( access && access.patches === true ) { %> <li><a id="deploy" href="#patches">Patches</a></li>\n <% } %>');
		template.push('</ul>\n');
		template.push('<ul class="nav pull-right">\n<li class="dropdown">\n<a href="#" class="dropdown-toggle" data-toggle="dropdown">\n<i class="icon-cog"></i><span>Settings </span><span><i class="icon-caret-down"></i>\n</a>\n<ul class="dropdown-menu">\n<li><a href="javascript:;">Account Settings</a></li>\n<li><a href="#" id="restore">Restore Defaults</a></li>\n<li><a href="#widgetProperties" data-toggle="modal" id="addwidget" onclick="setProperties(this, \'new\');">Add Widget</a></li>\n<li class="divider"></li>\n<li><a href="javascript:;">Help</a></li>\n</ul>\n</li>\n</ul>');
		template.push('</nav>');

		return template.join("");
	},
	"dashboard/summary/list": function () {
		"use strict";
		var template = [];

		template.push('<summary class="row-fluid clearfix">');
		template.push('<% var span = ["span12","span6","span4","span3"]; %>');
		template.push('<% for(var i = 0, len = count; i < len; i += 1) { var extraClass= data[i] < 0?" error":"";%>');
		template.push('<dl class="<%= span[len-1] || "span2" %><% if(obj.format && $.type(obj.format[i]) === "function") { print(obj.format[i].apply(window, [data[i]])); } %>">\n');
		template.push('<dt><%= keys[i] %></dt>\n<dd><%= Math.abs(data[i]) %></dd>\n</dl>\n');
		template.push('<% } %>');
		template.push('</summary>');

		return template.join("");
	}
};