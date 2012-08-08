// BootStrap
jQuery(document).ready(function ($) {
	"use strict";
	// Add collapse button for Bootstrap collapsable nav bars.
	// This is to prevent unneeded markup in the HTML
	$('.nav-collapse').parent().prepend(
		$('<a class="btn btn-navbar noPrint" data-toggle="collapse" data-target=".nav-collapse">')
			.append('<span class="icon-bar"/><span class="icon-bar"/><span class="icon-bar"/>')
	);
});