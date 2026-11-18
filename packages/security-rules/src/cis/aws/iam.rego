package cis.aws.iam

import rego.v1

# Applies to raw IAM policy documents embedded in IR (extension point).
deny contains msg if {
	some p in input.iamPolicies
	some s in p.statements
	s.effect == "Allow"
	some a in s.actions
	a == "*"
	msg := sprintf("CIS-1.16: IAM policy '%s' uses wildcard action", [p.name])
}
