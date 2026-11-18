package privacy.residency

import rego.v1

default allowed_regions := ["eu-west-1", "eu-central-1", "eu-north-1", "eu-west-3"]

deny contains msg if {
	"GDPR" in input.metadata.compliance
	not input.metadata.region in allowed_regions
	msg := sprintf("GDPR-Ch5: region '%s' is outside the allowed EU list", [input.metadata.region])
}
