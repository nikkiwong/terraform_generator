<h2>Usage</h2>

<h3>For all automation scripts:</h3>

Make sure you are in the folder of the python file you wish to run and also the csv files should be in the same structure as the corresponding sample files in the csv folder.

#currently security_groups script only supports aws, azure and oci cloud types
#First argument after the python filename is the terraform filename (whatever you want to call the file, ensure the extension .tf is included!), second argument is the cloud type.
Example of using the security group generator
<br/> python3 terraform-generator-SG.py "OCI_terraform_SG_file.tf" oci
<br/> python3 terraform-generator-SG.py "AWS_terraform_SG_file.tf" aws
<br/> python3 terraform-generator-SG.py "AZURE_terraform_SG_file.tf" azure

#currently security_groups script only supports aws, azure and oci cloud types
# 1st arg after the python filename is the terraform filename (whatever you want to call the file, ensure the extension .tf is included!), 2nd arg =  is the cloud type, 3rd arg = CSV file name with security group rules.
Example of using the security group rule generator
<br/> python3 terraform-generator-SGRule.py "OCI_terraform_SGRULE_file.tf" oci OCI_short_rule_sample.csv
<br/> python3 terraform-generator-SGRule.py "AWS_terraform_SGRULE_file.tf" aws AWS_short_rule_sample.csv
<br/> python3 terraform-generator-SGRule.py "AZURE_terraform_SGRULE_file.tf" azure Azure_short_rule_sample.csv
