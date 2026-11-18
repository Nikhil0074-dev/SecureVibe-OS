package lib.utils

import rego.v1

# All resources of a given IR type
resources_of(t) := [r | some r in input.resources; r.type == t]

has_compliance(c) if c in input.metadata.compliance
