# Usage

## For all automation scripts:

Make sure you are in the folder of the python file you wish to run and also the csv files should be in the same structure as the corresponding sample files in the csv folder.

#### *currently security_groups script only supports aws, azure and oci cloud types
##### 1st arg after the python filename is the terraform filename (whatever you want to call the file, ensure the extension .tf is included!), 2nd argument = cloud type.
Example of using the security group generator
```python
python3 terraform-generator-SG.py "OCI_terraform_SG_file.tf" oci
python3 terraform-generator-SG.py "AWS_terraform_SG_file.tf" aws
python3 terraform-generator-SG.py "AZURE_terraform_SG_file.tf" azure
```

#### *currently security_groups script only supports aws, azure and oci cloud types
##### 1st arg after the python filename is the terraform filename (whatever you want to call the file, ensure the extension .tf is included!), 2nd arg =  is the cloud type, 3rd arg = CSV file name with security group rules.
Example of using the security group rule generator
```python
python3 terraform-generator-SGRule.py "OCI_terraform_SGRULE_file.tf" oci "OCI_short_rule_sample.csv"
python3 terraform-generator-SGRule.py "AWS_terraform_SGRULE_file.tf" aws "AWS_short_rule_sample.csv"
python3 terraform-generator-SGRule.py "AZURE_terraform_SGRULE_file.tf" azure "Azure_short_rule_sample.csv"
```
