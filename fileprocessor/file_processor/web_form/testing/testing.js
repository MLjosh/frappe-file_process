// frappe.ready(function() {
// 	// bind events here
// })

frappe.ready(function() {
	// show a processing message while the page is loading
	var overlay = $('<div>').addClass('processing-overlay').text('Loading...');
	$('body').append(overlay);
	
	// bind events here
	
	// hide the overlay once everything is loaded
	$(window).on('load', function() {
		overlay.fadeOut();
	});
});
