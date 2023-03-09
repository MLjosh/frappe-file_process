// Copyright (c) 2023, Josh Tinte and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Test", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Test', {
    refresh: function(frm) {
        frm.add_custom_button(__('Save'), function() {
            // Show a loading message before starting the save process
            frappe.show_alert('Saving in progress. Please wait...');
            // frappe.show_progress('Loading..', 70, 100, 'Please wait');

            // Call the save method
            frm.save('Save', function() {
                // After the save process completes, hide the loading message
                frappe.hide_alert();
            });
        });
    }
});

// frappe.ui.form.on("Test", {
//     refresh: function(frm) {
//         // Get the submit button element
//         var submitButton = frm.get_field("submit_button").$wrapper.find("button");

//         // Add an event listener to the submit button
//         submitButton.on("click", function() {
//             // Show an alert message
//             frappe.show_alert({
//                 message: "Please wait while the file is processing...",
//                 indicator: "orange",
//                 duration: 3
//             });
//         });
//     }
// });