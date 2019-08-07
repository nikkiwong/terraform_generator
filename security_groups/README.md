<h2>Usage</h2>

#first argument after the python filename is the terraform filename (whatever you want to call the file, ensure the extension .tf is included!), second argument is the cloud type.

#currently only supports aws, azure and oci cloud types
<br/> python3 generator.py "OCI_terraform_file.tf" oci
<br/> python3 generator.py "AWS_terraform_file.tf" aws
<br/> python3 generator.py "AZURE_terraform_file.tf" azure
