# Copyright (c) 2023, Josh Tinte and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
# from frappe.desk.page.setup_wizard.install import create_route

import csv
import re
import os
# import pandas as pd
from frappe.utils.file_manager import get_file, save_file
# from frappe.utils.csvutils import read_csv_file


#google drive
import requests
import json

from frappe import get_doc
import io
from frappe import db
from frappe import msgprint
from frappe.utils import now
from frappe.utils import now_datetime, format_datetime

import datetime

import random
from datetime import datetime



class FileProcess(Document):

	def before_save(self):
		
		subscribed_customers = frappe.get_all("Customer", filters={"subscriber": 1})
		user = frappe.get_doc("User", frappe.session.user)
		# user_email = frappe.db.get_value("User", frappe.session.user, "email")

		logged_in_user_name = user.full_name
		for customer in subscribed_customers:
			customer_name = customer['name']
			if logged_in_user_name == customer_name:
				# frappe.msgprint("Subscriber")
				break


		else:
			frappe.throw("You must be a subscriber to process files!")

		if self.file:
		    if not self.file.lower().endswith('.csv'):
		        frappe.throw("Please attach CSV File only!")


		ip_ranges = []
		query = """
		SELECT StartIP, end_ip, abuseemails, isp
		FROM `tabMax Mind`
		"""
		results = db.sql(query, as_dict=True)

		for row in results:
		    ip_ranges.append({
		        "StartIP": row["StartIP"],
		        "end_ip": row["end_ip"],
		        "abuseemails": row["abuseemails"],
		        "isp" : row["isp"]
		    })
		##console print
		# msgprint(json.dumps(ip_ranges), title="IP Ranges")

		# # create a dictionary to store the lookup results
		# lookup_results = {}



		# Open the CSV file for reading
		# with open(f"./frappe.test{self.file}", "r") as csv_file:


		try:
			# Open the CSV file and read its contents into a list of dictionaries
			with open(f"./frappe.test/public{self.file}") as file:
			    reader = csv.DictReader(file)
			    data = list(reader)
			    if 'src_ip' not in reader.fieldnames:
			    	frappe.throw("Incorrect file!")

		except Exception as e:
			try:
				# Open the CSV file and read its contents into a list of dictionaries
				with open(f"./frappe.test{self.file}") as file:
				    reader = csv.DictReader(file)
				    data = list(reader)
				    if 'src_ip' not in reader.fieldnames:
				    	frappe.throw("Incorrect file!")
				
			except Exception as e:
				frappe.throw("Error in Processing your file. Please make sure you have uploaded the correct file.")
				

# ----------------- test--------------

# 		# Open the CSV file and read its contents into a list of dictionaries
# 		with open(f"./frappe.test{self.file}") as file:
# 		    reader = csv.DictReader(file)
# 		    data = list(reader)

# ----------------- test--------------

		# Create an empty dictionary to store the results for
		# src_ip :[content]
		results = {}
		# get key results for ip


		# Loop through the data and extract the relevant information
		for row in data:
		    src_ip = row['src_ip']
		    content = f"{row['DateTime']}|{row['source']}|{row['src_ip']}|{row['msg_info']}|{row['dst_ip']}"
		    if src_ip not in results:
		        results[src_ip] = []
		    if len(results[src_ip]) < 5:
		        results[src_ip].append(content)

		# Add the header to each list of contents
		for src_ip in results:
		    results[src_ip].insert(0, "DateTime|Source|SourceIP|Details|Destination")

		# # Print the results for testing
		# for src_ip, contents in results.items():
		#     frappe.msgprint(f"{src_ip}:{contents}")


		ips_to_lookup = list(results.keys())
		# msgprint(json.dumps(ips_to_lookup), title="ips_to_lookup")



		# lookup abuse contact information for each IP address and store results in a dictionary
		result_ips_lookup = {}
		for ip_to_lookup in ips_to_lookup:
		    abuseemails = None
		    isp = None
		    for ip_range in ip_ranges:
		        start_ip_int = int(''.join([bin(int(x)+256)[3:] for x in ip_range['StartIP'].split('.')]), 2)
		        end_ip_int = int(''.join([bin(int(x)+256)[3:] for x in ip_range['end_ip'].split('.')]), 2)
		        ip_to_lookup_int = int(''.join([bin(int(x)+256)[3:] for x in ip_to_lookup.split('.')]), 2)
		        if start_ip_int <= ip_to_lookup_int <= end_ip_int:
		            abuseemails = ip_range['abuseemails']
		            isp = ip_range['isp']
		            break
		    result_ips_lookup[ip_to_lookup] = [abuseemails, isp]

		# msgprint(json.dumps(result_ips_lookup), title="result_ips_lookup")


		# append the dictionaries of result_ips_lookup and results
		combined_dict = {}

		for key in result_ips_lookup.keys():
		    if key in results:
		        combined_dict[key] = [result_ips_lookup[key], results[key]]
		    else:
		        combined_dict[key] = [result_ips_lookup[key]]

		for key in results.keys():
		    if key not in combined_dict:
		        combined_dict[key] = [results[key]]


		for key, value in combined_dict.items():
		    email = value[0][0]
		    company = value[0][1]
		    data = value[1]
		    # # Split each line using comma separator, join using tab separator, and join all lines using newline separator
		    # formatted_data = '<br>'.join(['\t'.join(line.split(',')) for line in data])
		    # Create the table header
		    table_header = '<tr><th>{}</th></tr>'.format('</th><th>'.join(data[0].split('|')))

		    # Create the table rows
		    table_rows = ''
		    for line in data[1:]:
		        table_rows += '<tr><td>{}</td></tr>'.format('</td><td>'.join(line.split('|')))

		    # Combine the table header and rows
		    table = '<table>{}</table>'.format(table_header + table_rows)
		    content = f"""

		    Greetings Fellow Sys Ad/s <br><br>

		    Kindly take a look at one or more of your IP addresses that were seen attacking/probing our network.<br>
		    It may be compromised and it could be attacking other networks as well. Our Timezone is GMT +8. Please see the logs below:
		    <br><br>
		    {table}
		    <br><br>

		    Regards, BNS Team<br><br>

		    This Abuse Notification service is performed by BNS Network Monitoring Service on behalf of our clients.<br>
		    For more information, check out: https://bnshosting.net/pricing/network-monitoring-service/

		    """
		    dt = datetime.now()
		    dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
		    # dt_str = dt.strftime('%b. %d, %Y %H:%M:%S')

		    # Get current date and time
		    now_dt = datetime.now()

		    # Format current date and time as a string
		    dt_string = now_dt.strftime("%Y%d")

		    # Generate a random number between 0 and 9999
		    rand_num = random.randint(0, 9999)
		    result_rand_num = "{:04d}".format(rand_num)

		    # Combine date-time and random number
		    issue_name = f"ISS-{dt_string}-{result_rand_num}"
		    current_user_email = frappe.get_doc("User", frappe.session.user).email

		    content_no_ip = f"""
		    Dear Valued Customer,<br>
		    We regret to inform you that this {key} IP address you have provided us is not currently listed in our database. We sincerely apologize for any inconvenience this may have caused. Rest assured, we have taken immediate action and added this IP address to our records to ensure that future email logs are sent to the designated abuse email addresses.
		    Thank you for bringing this to our attention and we appreciate your patience and understanding.This is the email logs that did not send.<br><br>
		    {table}

		    """

		    try:
		    	if email is None:
		    		new_issue = frappe.get_doc({
		    		    "doctype": "Issue",
		    		    "subject": f"Notice : IP address {key} is not listed in our records",
		    		    "description": content_no_ip,
		    		    "raised_by"  : current_user_email,
		    		    "assigned_to": "samplebns088@gmail.com",
		    		    # "recipients" : f"{email}",
		    		    # "date": dt_str,
		    		    # "issue_id" : issue_name,
		    		    "status": "Open"
		    		})
		    		new_issue.insert(ignore_permissions=True)


		    	if email is not None:
			    	frappe.sendmail(
			    		sender="samplebns088@gmail.com",
			    		recipients=f"{email}",
			    	    subject=f"Abuse Alerts: {company}: {key}",
			    	    message=content
			    	    )
			    	frappe.msgprint("sent!")

		    		new_issue = frappe.get_doc({
		    		    "doctype": "Issue",
		    		    "subject": f"Abuse Alerts: {company}: {key}",
		    		    "description": content,
		    		    "raised_by"  : current_user_email,
		    		    "assigned_to": "samplebns088@gmail.com",
		    		    # "recipients" : f"{email}",
		    		    # "date": dt_str,
		    		    # "issue_id" : issue_name,
		    		    "status": "Open"
		    		})
		    		new_issue.insert(ignore_permissions=True)


		    	try:
		    		self.issue_id = issue_name
		    		self.date = dt_str
		    		self.status = "Processed"
		    		# frappe.msgprint("Success: File Added!")
		    	
		    	except Exception as e:
		    		frappe.msgprint("Failed: File Error!")
		    except Exception as e:
		    	frappe.msgprint("Message not sent!")

		  


# 	def before_save(self):

		# subscribed_customers = frappe.get_all("Customer", filters={"subscriber": 1})
		# user = frappe.get_doc("User", frappe.session.user)
		# # user_email = frappe.db.get_value("User", frappe.session.user, "email")

		# logged_in_user_name = user.full_name
		# for customer in subscribed_customers:
		# 	customer_name = customer['name']
		# 	if logged_in_user_name == customer_name:
		# 		# frappe.msgprint("Subscriber")
		# 		break


		# else:
		# 	frappe.throw("You must be a subscriber to process files!")

		# if self.file:
		#     if not self.file.lower().endswith('.csv'):
		#         frappe.throw("Please attach CSV File only!")

# 		# doc = frappe.db.get_value("File Process", "file")

# 		# file = get_file(doc)


# # -------- start query for Max Mind -----------------------------------
# 		ip_ranges = []
# 		query = """
# 		SELECT StartIP, end_ip, abuseemails, isp
# 		FROM `tabMax Mind`
# 		"""
# 		results = db.sql(query, as_dict=True)

# 		for row in results:
# 		    ip_ranges.append({
# 		        "StartIP": row["StartIP"],
# 		        "end_ip": row["end_ip"],
# 		        "abuseemails": row["abuseemails"],
# 		        "isp" : row["isp"]
# 		    })
# 		##console print
# 		# msgprint(json.dumps(ip_ranges), title="IP Ranges")

# 		# # create a dictionary to store the lookup results
# 		# lookup_results = {}



# 		# Open the CSV file for reading
# 		# with open(f"./frappe.test{self.file}", "r") as csv_file:


# 		try:
# 			# Open the CSV file and read its contents into a list of dictionaries
# 			with open(f"./frappe.test/public{self.file}") as file:
# 			    reader = csv.DictReader(file)
# 			    data = list(reader)
# 			    if 'src_ip' not in reader.fieldnames:
# 			    	frappe.throw("Incorrect file!")

# 		except Exception as e:
# 			try:
# 				# Open the CSV file and read its contents into a list of dictionaries
# 				with open(f"./frappe.test{self.file}") as file:
# 				    reader = csv.DictReader(file)
# 				    data = list(reader)
# 				    if 'src_ip' not in reader.fieldnames:
# 				    	frappe.throw("Incorrect file!")
				
# 			except Exception as e:
# 				frappe.throw("Error in Processing your file. Please make sure you have uploaded the correct file.")
				

# # ----------------- test--------------

# # 		# Open the CSV file and read its contents into a list of dictionaries
# # 		with open(f"./frappe.test{self.file}") as file:
# # 		    reader = csv.DictReader(file)
# # 		    data = list(reader)

# # ----------------- test--------------

# 		# Create an empty dictionary to store the results for
# 		# src_ip :[content]
# 		results = {}
# 		# get key results for ip


# 		# Loop through the data and extract the relevant information
# 		for row in data:
# 		    src_ip = row['src_ip']
# 		    content = f"{row['DateTime']},{row['source']},{row['src_ip']},{row['dst_ip']},{row['msg_info']}"
# 		    if src_ip not in results:
# 		        results[src_ip] = []
# 		    if len(results[src_ip]) < 4:
# 		        results[src_ip].append(content)

# 		# Add the header to each list of contents
# 		for src_ip in results:
# 		    results[src_ip].insert(0, "DateTime,Source,Source IP,Destination,Details")

# 		# # Print the results for testing
# 		# for src_ip, contents in results.items():
# 		#     frappe.msgprint(f"{src_ip}:{contents}")


# 		ips_to_lookup = list(results.keys())
# 		# msgprint(json.dumps(ips_to_lookup), title="ips_to_lookup")



# 		# lookup abuse contact information for each IP address and store results in a dictionary
# 		result_ips_lookup = {}
# 		for ip_to_lookup in ips_to_lookup:
# 		    abuseemails = None
# 		    isp = None
# 		    for ip_range in ip_ranges:
# 		        start_ip_int = int(''.join([bin(int(x)+256)[3:] for x in ip_range['StartIP'].split('.')]), 2)
# 		        end_ip_int = int(''.join([bin(int(x)+256)[3:] for x in ip_range['end_ip'].split('.')]), 2)
# 		        ip_to_lookup_int = int(''.join([bin(int(x)+256)[3:] for x in ip_to_lookup.split('.')]), 2)
# 		        if start_ip_int <= ip_to_lookup_int <= end_ip_int:
# 		            abuseemails = ip_range['abuseemails']
# 		            isp = ip_range['isp']
# 		            break
# 		    result_ips_lookup[ip_to_lookup] = [abuseemails, isp]

# 		# msgprint(json.dumps(result_ips_lookup), title="result_ips_lookup")


# 		dt = datetime.now()
# 		dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
# 		# dt_str = dt.strftime('%b. %d, %Y %H:%M:%S')

# 		# Get current date and time
# 		now_dt = datetime.now()

# 		# Format current date and time as a string
# 		dt_string = now_dt.strftime("%Y%d")

# 		# Generate a random number between 0 and 9999
# 		rand_num = random.randint(0, 9999)
# 		result_rand_num = "{:04d}".format(rand_num)

# 		# Combine date-time and random number
# 		issue_name = f"ISS-{dt_string}-{result_rand_num}"

# ---------------- end issue id ------------


# 		# append the dictionaries of result_ips_lookup and results
# 		combined_dict = {}

# 		for key in result_ips_lookup.keys():
# 		    if key in results:
# 		        combined_dict[key] = [result_ips_lookup[key], results[key]]
# 		    else:
# 		        combined_dict[key] = [result_ips_lookup[key]]

# 		for key in results.keys():
# 		    if key not in combined_dict:
# 		        combined_dict[key] = [results[key]]


# 		for key, value in combined_dict.items():
# 		    email = value[0][0]
# 		    company = value[0][1]
# 		    data = value[1]
# 		    # # Split each line using comma separator, join using tab separator, and join all lines using newline separator
# 		    # formatted_data = '<br>'.join(['\t'.join(line.split(',')) for line in data])
# 		    # Create the table header
# 		    table_header = '<tr><th>{}</th></tr>'.format('</th><th>'.join(data[0].split(',')))

# 		    # Create the table rows
# 		    table_rows = ''
# 		    for line in data[1:]:
# 		        table_rows += '<tr><td>{}</td></tr>'.format('</td><td>'.join(line.split(',')))

# 		    # Combine the table header and rows
# 		    table = '<table>{}</table>'.format(table_header + table_rows)
# 		    content = f"""

# 		    Greetings Fellow Sys Ad/s <br><br>

# 		    Kindly take a look at one or more of your IP addresses that were seen attacking/probing our network.<br>
# 		    It may be compromised and it could be attacking other networks as well. Our Timezone is GMT +8. Please see the logs below:
# 		    <br><br><br>
# 		    {table}
# 		    <br><br><br>

# 		    Regards, BNS Team<br><br>

# 		    This Abuse Notification service is performed by BNS Network Monitoring Service on behalf of our clients.<br>
# 		    For more information, check out: https://bnshosting.net/pricing/network-monitoring-service/

# 		    """


# 		    try:
# 		    	frappe.sendmail(
# 		    		sender="sampleBNS088@gmail.com",
# 		    		recipients=f"{email}",
# 		    	    subject=f"Abuse Alerts: {company}: {key}",
# 		    	    message=content
# 		    	    )
# 		    	frappe.msgprint("Message Sent!")
# 		    	try:
# 		    		new_issue = frappe.get_doc({
# 		    		    "doctype": "File Process Issue",
# 		    		    "subject": f"Abuse Alerts: {company}: {key}",
# 		    		    "email_content": content,
# 		    		    "recipients" : f"{email}",
# 		    		    "date": dt_str,
# 		    		    "issue_id" : issue_name,
# 		    		    "status": "Message Sent"
# 		    		})
# 		    		new_issue.insert(ignore_permissions=True)
# 		    	except Exception as e:
# 		    		frappe.throw(msg="Add Issue Error!")

# 		    	try:
# 		    		self.issue_id = issue_name
# 		    		self.date = dt_str
# 		    		self.status = "Processed"
# 		    		frappe.msgprint("Success: File Added!")
		    	
# 		    	except Exception as e:
# 		    		frappe.throw("Failed: File Error!")
# 		    except Exception as e:
# 		    	frappe.throw("Message not sent!")

		  
