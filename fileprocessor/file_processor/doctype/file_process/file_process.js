// Copyright (c) 2023, Josh Tinte and contributors
// For license information, please see license.txt

// frappe.ui.form.on("File Process", {
// 	refresh(frm) {

// 	},
// });

// frappe.ui.form.on('File Process', {
//   refresh: function(frm) {
//     frappe.db.get_list('File', {
//       fields: ['name', 'file_name'],
//       filters: {
//         file_url: ['like', '%.db']
//       }
//     }).then(function(result) {
//       var options = [];
//       result.forEach(function(row) {
//         options.push(row.file_name);
//       });
//       frm.set_df_property('file_names', 'options', options);
//     });
//   }
// });

frappe.ui.form.on("File Process", {
    before_save: function(frm) {
        frappe.call({
            method: "fileprocess.file_process.doctype.file_process.before_save",
            callback: function(r) {
                if (r.exc) {
                    frappe.msgprint({
                        title: __('Error'),
                        indicator: 'red',
                        message: __('An error occurred while saving.'),
                        traceback: r.exc
                    });
                }
            }
        });
    }
});