//the comments show the terraform fields with their corresponding fields which is found in the "security_group.csv" file.

#OCI
resource "oci_core_network_security_group" "test_network_security_group" { //"resource_SG_name" = "test_network_security_group"
    #Required
    compartment_id = "${var.compartment_id}"  //"network_security_group_container_id" = compartment_id
    vcn_id = "${oci_core_vcn.test_vcn.id}"  // "id (VPN/VCN)" = vcn_id
    //"SG_name" = display_name (if needed)
}

#AWS
resource "aws_security_group" "allow_tls" { //"resource_SG_name" = "allow_tls"
  name        = "allow_tls" //"SG_name" = name
  vpc_id      = "${aws_vpc.main.id}"  // "id (VPN/VCN)" = vpc_id

}

#AZURE
resource "azurerm_network_security_group" "test" { //"resource_SG_name" = "test"
  name                = "acceptanceTestSecurityGroup1"  //"SG_name" = name
  location            = "${azurerm_resource_group.test.location}"  // "location" = location
  resource_group_name = "${azurerm_resource_group.test.name}"  //"network_security_group_container_name" = resource_group_name

}