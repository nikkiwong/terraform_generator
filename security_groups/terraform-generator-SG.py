import sys
import os
import shutil
import json
import re  # Regex
import csv

security_group_csv = "../csv/security_group.csv"
conversions_csv = "../csv/conversions.csv"


def main():
    security_group_dict = csv_to_dict()

    # print(import_rules_from_excel())
    # exit(0)

    # print("Dictionary:")
    # print(json.dumps(rules_dict, indent = 4))

    dict_to_tf(security_group_dict)

# Convert data from CSV into a Python dictionary
def csv_to_dict():
    security_group_dict = {}

    rows = import_security_group_csv()
    security_group_list = ""

    # Create security group
    for row in rows:
        security_group_list, row_dict = parse_row(row, security_group_list)

        security_group_dict[security_group_list] = row_dict

    return security_group_dict

# Extract values from row into separate variables
def parse_row(row, previous_security_group_list):

    # Check if the security group list entry is blank. If so, use previous security group list value
    name = row[0].lower() if row[0] != "" else previous_security_group_list

    security_group_name = "" if row[1] == "-" else row[1]
    netw_security_group_id = "" if row[2] == "-" else row[2]
    netw_security_group_name = "" if row[3] == "-" else row[3]
    network_id = "" if row[4] == "-" else row[4]
    location = "" if row[5] == "-" else row[5]

    row = {"security_group_name": security_group_name, "netw_security_group_id": netw_security_group_id, "netw_security_group_name": netw_security_group_name, "network_id": network_id, "location": location}

    return name, row

# Convert Python dictionary into Terraform output
def dict_to_tf(security_group_dict):

    # # Write output to file
    if(len(sys.argv) > 2):
        output_file = sys.argv[1]
        cloud_type = sys.argv[2]
    else:
        print(f'ERROR: No output filename and/or cloud type of config entered. Exiting.')
        exit(1)

    # Make a copy of the file for a backup

    # if os.path.isfile(output_file):
    # 	print(f"Creating backup of {output_file}")
    # 	shutil.copyfile(output_file, output_file.replace('.tf', '.tf.bak'))

    # stdout_backup = sys.stdout # Keep copy of stdout for use later
    sys.stdout = open(output_file,'wt')

    for security_group_list in security_group_dict.keys():
        cloud_specific_terraform = get_cloud_specific_terraform(cloud_type, security_group_dict[security_group_list])
        print(f'resource "{cloud_specific_terraform["security_group_type"]}" "{security_group_list}" {{')
        cloud_specific_terraform.pop("security_group_type")
        for key in cloud_specific_terraform:
            print(f'    {key} = "{cloud_specific_terraform[key]}"')

        print('}') # Close resource
        print()

    # sys.stdout = stdout_backup # Redirect back to default location
    print("Finished writing to file.")

def get_cloud_specific_terraform(cloud_type, security_group_dict):
    if cloud_type.lower() == "oci":
        compartment_id = tf_conversion(security_group_dict["netw_security_group_id"])
        vcn_id = tf_conversion(security_group_dict["network_id"])
        return {"security_group_type": "oci_core_network_security_group", "compartment_id": compartment_id, "vcn_id": vcn_id, "display_name": security_group_dict["security_group_name"]}

    elif cloud_type.lower() == "aws":
        return {"security_group_type": "aws_security_group", "vpc_id": security_group_dict["network_id"], "name": security_group_dict["security_group_name"]}

    elif cloud_type.lower() == "azure":
        return {"security_group_type": "azurerm_resource_group", "resource_group_name": security_group_dict["netw_security_group_name"], "name": security_group_dict["security_group_name"], "location": security_group_dict["location"]}

    else:
        print(f'ERROR: "{cloud_type}" not recognisable cloud type. Exiting.')
        exit(1)

# Convert input values into a Terraform readable value
def tf_conversion(input_value):
# Check if input value matches CIDR value, e.g. x.x.x.x/x
# If so, no need to look up conversion list, just return value
    regex_pattern = "\d*\.\d*\.\d*\.\d*/\d*"
    if(re.match(regex_pattern, input_value)):
        return input_value

    lookup = conversions_csv_to_dict()

    if(input_value in lookup.keys()):
        return lookup[input_value]
    else:
        print(f'INFO: "{input_value}" not in conversion list. Exiting.')
        exit(1)

# Import conversion rules from 'conversions.csv'
def conversions_csv_to_dict():
    conversions_dict = {}

    with open(conversions_csv) as csv_file:
        read_csv = csv.reader(csv_file, delimiter=',')
        for row in read_csv:
            conversions_dict[row[0]] = row[1]

    return conversions_dict

# Read data in from CSV into an array of rows
def import_security_group_csv():
	csv_rows = []

	with open(security_group_csv) as csv_file:
		read_csv = csv.reader(csv_file, delimiter=',')
		for row in read_csv:
			if("resource_SG_name" not in row[0]): #"resource_SG_name will need to be changed if you're changing it to something else in the CSV file"
				csv_rows.append(row)

	return csv_rows


# Begin executing code
main()
