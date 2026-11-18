package cis.aws.rds

import data.lib.utils
import rego.v1

deny contains msg if {
	some r in utils.resources_of("AWS::RDS")
	object.get(r, "encrypted", false) != true
	msg := sprintf("CIS-2.3.1: RDS '%s' must be encrypted", [r.id])
}

deny contains msg if {
	some r in utils.resources_of("AWS::RDS")
	object.get(r, "private", false) != true
	msg := sprintf("CIS-2.3.3: RDS '%s' must not be publicly accessible", [r.id])
}

deny contains msg if {
	some r in utils.resources_of("AWS::RDS")
	object.get(r, "deletionProtection", false) != true
	msg := sprintf("RDS '%s' must enable deletion protection", [r.id])
}
