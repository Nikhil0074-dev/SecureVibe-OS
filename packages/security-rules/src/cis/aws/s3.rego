package cis.aws.s3

import data.lib.utils
import rego.v1

# CIS 2.1.5 - block public access
deny contains msg if {
	some r in utils.resources_of("AWS::S3")
	object.get(r, "blockPublicAcls", false) != true
	msg := sprintf("CIS-2.1.5: S3 '%s' must set blockPublicAcls=true", [r.id])
}

# CIS 2.1.1 - encryption at rest with KMS
deny contains msg if {
	some r in utils.resources_of("AWS::S3")
	object.get(r, "encryption", "") != "aws:kms"
	msg := sprintf("CIS-2.1.1: S3 '%s' must use aws:kms encryption", [r.id])
}

# Versioning
deny contains msg if {
	some r in utils.resources_of("AWS::S3")
	object.get(r, "versioning", false) != true
	msg := sprintf("CIS-2.1.3: S3 '%s' must enable versioning", [r.id])
}
