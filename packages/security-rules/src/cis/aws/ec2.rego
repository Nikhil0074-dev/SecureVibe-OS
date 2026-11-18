package cis.aws.ec2

import data.lib.utils
import rego.v1

deny contains msg if {
	some r in utils.resources_of("AWS::EC2")
	object.get(r, "associatePublicIp", false) == true
	msg := sprintf("CIS-5.x: EC2 '%s' must not associate a public IP", [r.id])
}

deny contains msg if {
	some r in utils.resources_of("AWS::EC2")
	object.get(r, "requireImdsV2", false) != true
	msg := sprintf("CIS-5.6: EC2 '%s' must require IMDSv2", [r.id])
}

deny contains msg if {
	some r in utils.resources_of("AWS::EC2")
	object.get(r, "encryptedRoot", false) != true
	msg := sprintf("CIS-2.2.1: EC2 '%s' root volume must be encrypted", [r.id])
}
