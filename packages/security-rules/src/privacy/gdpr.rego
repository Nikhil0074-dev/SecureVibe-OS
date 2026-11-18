package privacy.gdpr

import data.lib.utils
import rego.v1

# Art.32 - PII stores must be encrypted and non-public
deny contains msg if {
	utils.has_compliance("GDPR")
	some r in utils.resources_of("AWS::S3")
	r.containsPii == true
	object.get(r, "blockPublicAcls", false) != true
	msg := sprintf("GDPR-Art32: PII bucket '%s' must not be public", [r.id])
}

deny contains msg if {
	utils.has_compliance("GDPR")
	some r in utils.resources_of("AWS::S3")
	r.containsPii == true
	object.get(r, "encryption", "") != "aws:kms"
	msg := sprintf("GDPR-Art32: PII bucket '%s' must use KMS", [r.id])
}
