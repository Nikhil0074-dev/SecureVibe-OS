package securevibe

import data.cis.aws.ec2
import data.cis.aws.iam
import data.cis.aws.rds
import data.cis.aws.s3
import data.cis.aws.vpc
import data.privacy.gdpr
import data.privacy.residency
import rego.v1

# Single entry point: every deny set in the bundle, queried as data.securevibe.deny
deny := (((((s3.deny | rds.deny) | vpc.deny) | ec2.deny) | iam.deny) | gdpr.deny) | residency.deny
