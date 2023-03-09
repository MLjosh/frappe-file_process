import frappe

def get_context(context):
	# do your magic here

	context.filters = {
	    "owner": frappe.session.user
	}