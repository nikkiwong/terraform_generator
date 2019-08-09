import sys
import os
import shutil
import json
import re # Regex
import csv
import xlrd

rules_csv = "../csv/OCI_long_rule_sample.csv"
conversions_csv = "../csv/conversions.csv"


def main():
	rules_dict = csv_to_dict()
	dict_to_tf(rules_dict)

def oci_conversions(security_group_rule_dict):
    if(security_group_rule_dict["protocol"]!="all"):
        security_group_rule_dict["protocol"] = tf_conversion(security_group_rule_dict["protocol"])

    if("source" in security_group_rule_dict):
        security_group_rule_dict["source"] = tf_conversion(security_group_rule_dict["source"])

    if("destination" in security_group_rule_dict):
        security_group_rule_dict["destination"] = tf_conversion(security_group_rule_dict["destination"])

    # print(security_group_rule_dict)
    return security_group_rule_dict

def oci_check_protocol_options(security_group_rule_dict):
    if (security_group_rule_dict["protocol"] == "tcp" or security_group_rule_dict["protocol"] == "udp"):
        if ("ports" in security_group_rule_dict):
            # Extract port min and port max from ports
            if("-" in security_group_rule_dict["ports"]):
                port_min = security_group_rule_dict["ports"].split("-")[0]
                port_max = security_group_rule_dict["ports"].split("-")[1]
            else:
                port_min = security_group_rule_dict["ports"]
                port_max = security_group_rule_dict["ports"]
            port_type = "source" if (security_group_rule_dict["direction"] == "ingress") else "destination"

            security_group_rule_dict[security_group_rule_dict["protocol"]+"_options"] = {port_type+"_port_range": {"max": port_max, "min": port_min}}
            del security_group_rule_dict["ports"]

    #not sure how to structure this field in csv file yet so this is only a placeholder
    elif (security_group_rule_dict["protocol"] == "icmp"):
        if("icmp_type" in security_group_rule_dict):
            security_group_rule_dict[security_group_rule_dict["protocol"]+"_options"] = {"type": security_group_rule_dict["icmp_type"]}
            del security_group_rule_dict["icmp_type"]

    # print(security_group_rule_dict)
    # print()
    return security_group_rule_dict


#maps the correct function to corresponding cloud system. I placed this variable here because the functions needs to be declared before you assign them.
#I didn't write the functions for aws or azure as I don't know how their csv file will look.
cloud_options = {
    "oci": {"protocol_check": oci_check_protocol_options, "sg_rule_type": "oci_core_network_security_group_security_rule", "conversions": oci_conversions}
    #"aws" : {"protocol_check": aws_check_protocol_options, "sg_rule_type": "aws_core_network_security_group_security_rule", "conversions": aws_conversions}
    #"azure" : {"protocol_check": azure_check_protocol_options, "sg_rule_type": "azure_core_network_security_group_security_rule", "conversions": azure_conversions}
}
        

# Convert data from CSV into a Python dictionary
def csv_to_dict():
    rules_dict = {}
    security_group_name = ""

    field_names, rows = import_rules_csv()

    #dynamically calls the correct cloud specific check protocol options function
    check_protocol = cloud_options[sys.argv[2]]["protocol_check"]

    # Create security lists
    for row in rows:
        security_group_name, security_group_rule_name, security_group_rule_dict = parse_row(field_names, row, security_group_name)

        security_group_rule_dict = check_protocol(security_group_rule_dict)

        #dynamically calls the correct cloud specific conversion function
        value_conversions = cloud_options[sys.argv[2]]["conversions"]
        security_group_rule_dict = value_conversions(security_group_rule_dict)

        rules_dict[security_group_rule_name] = security_group_rule_dict 

    return rules_dict

    
# Extract values from row into dictionay objects
def parse_row(field_names, row, previous_security_group_name):

    security_group_rule_dict = {}
	
    # Check if the security list entry is blank. If so, use previous security list value
    row[2] = row[2].lower() if row[2] != "" else previous_security_group_name

    direction_options_in = "inbound" if (sys.argv[2].lower() == "azure") else "ingress"
    direction_options_out = "outbound" if (sys.argv[2].lower() == "azure") else "egress"

    #Check if the correct values are entered for direction
    if(row[1].lower() not in [direction_options_in, direction_options_out]):
        print(f'ERROR: {field_names[1]} does not equal {direction_options_in}/{direction_options_out}. Value found: {row[1].lower()}')
        print('Exiting.')
        exit(1)

    for i in range(0,len(row)):
        if i==3:
            #don't want to add security_group_rule_name as a value as this will be the main key for the security_group_rule_dict
            continue

        elif(field_names[i].lower() == "protocol" and (row[i] == "" or row[i] == "-")):
            security_group_rule_dict[field_names[i].lower()] = "all"

        elif(len(row[i])>0 and row[i] != "-" and row[i] != ""):
            #only add the fields which have values
            if(field_names[i].lower() == "source" or field_names[i].lower() == "destination"):
                security_group_rule_dict[field_names[i].lower()] = row[i]
            else:
                security_group_rule_dict[field_names[i].lower()] = row[i].lower()
        # else:
        #     print("empty fields")
        #     print(field_names[i])
        #     print()

    return row[2], row[3], security_group_rule_dict


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
def import_rules_csv():
    field_names=[]
    csv_rows = []
    
    with open(rules_csv) as csv_file:
        read_csv = csv.reader(csv_file, delimiter=',')
        for row in read_csv:
            if("protocol" in row[0]):
                row[0] = "protocol"
                field_names = row
            elif("protocol" not in row[0] and row[0] != ""):
                csv_rows.append(row)
            #else:
                #print("You are missing required fields for {row[3]}.)
                #print(Exiting...")
                #exit(1)

    return field_names, csv_rows

def print_options_dict(d, n=1, k=""):
    if k != "":
        print(f'{"    "*n}{k}{{')
    for k, v in d.items():
        if isinstance(v, dict):
            print_options_dict(v, n+1, k)
        else:
            print(f'{"    " * (n+1)}{k} = "{v}",')
    if k != "":
        print(f'{"    " * (n)}}}')


# Convert Python dictionary into Terraform output
def dict_to_tf(security_group_rule_dict):

    # Write output to file
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

    for security_group_rule in security_group_rule_dict.keys():
        print(f'resource "{cloud_options[sys.argv[2]]["sg_rule_type"]}" "{security_group_rule}" {{')
        for rule in security_group_rule_dict[security_group_rule]:

            #Checks for nested dictionaries so it can be parsed
            if isinstance(security_group_rule_dict[security_group_rule][rule], dict):
                print(f'    {rule} = {{')
                print_options_dict(security_group_rule_dict[security_group_rule][rule])
            else:    
                print(f'    {rule} = "{security_group_rule_dict[security_group_rule][rule]}"')
        print('}') # Close resource
        print()

    # sys.stdout = stdout_backup # Redirect back to default location
    print("Finished writing to file.")


# Begin executing code
main()