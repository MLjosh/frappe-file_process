def get_list_context(context):
    context.filters = {
        "owner": frappe.session.user
    }
