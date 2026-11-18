package cis.aws.vpc

import data.lib.utils
import rego.v1

# CIS 3.9 - VPC flow logging
deny contains msg if {
	some r in utils.resources_of("AWS::VPC")
	object.get(r, "enableFlowLogs", false) != true
	msg := sprintf("CIS-3.9: VPC '%s' must enable flow logs", [r.id])
}

deny contains msg if {
	some r in utils.resources_of("AWS::SG")
	some i in r.ingress
	i.cidr == "0.0.0.0/0"
	msg := sprintf("CIS-5.2: SG '%s' allows 0.0.0.0/0 ingress on port %d", [r.id, i.port])
}
