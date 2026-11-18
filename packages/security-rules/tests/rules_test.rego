package rules_test

import data.cis.aws.ec2
import data.cis.aws.rds
import data.cis.aws.vpc
import data.privacy.gdpr
import data.privacy.residency
import rego.v1

secure := {
	"metadata": {"compliance": ["GDPR"], "region": "eu-west-1"},
	"resources": [
		{"id": "v", "type": "AWS::VPC", "enableFlowLogs": true},
		{"id": "d", "type": "AWS::RDS", "encrypted": true, "private": true, "deletionProtection": true},
		{"id": "e", "type": "AWS::EC2", "associatePublicIp": false, "requireImdsV2": true, "encryptedRoot": true},
		{"id": "s", "type": "AWS::SG", "vpc": "v", "ingress": [{"port": 443, "cidr": "10.0.0.0/16"}]},
		{"id": "b", "type": "AWS::S3", "containsPii": true, "blockPublicAcls": true, "encryption": "aws:kms", "versioning": true},
	],
}

test_secure_passes_everything if {
	count(rds.deny) == 0 with input as secure
	count(vpc.deny) == 0 with input as secure
	count(ec2.deny) == 0 with input as secure
	count(gdpr.deny) == 0 with input as secure
	count(residency.deny) == 0 with input as secure
}

test_rds_unencrypted_and_public if {
	bad := {"resources": [{"id": "d", "type": "AWS::RDS", "encrypted": false, "private": false, "deletionProtection": false}]}
	count(rds.deny) == 3 with input as bad
}

test_vpc_flow_logs_required if {
	count(vpc.deny) == 1 with input as {"resources": [{"id": "v", "type": "AWS::VPC", "enableFlowLogs": false}]}
}

test_sg_open_world_denied if {
	count(vpc.deny) == 1 with input as {"resources": [{"id": "s", "type": "AWS::SG", "ingress": [{"port": 22, "cidr": "0.0.0.0/0"}]}]}
}

test_ec2_public_ip_denied if {
	count(ec2.deny) == 3 with input as {"resources": [{"id": "e", "type": "AWS::EC2", "associatePublicIp": true}]}
}

test_gdpr_pii_bucket_public_denied if {
	bad := {"metadata": {"compliance": ["GDPR"]}, "resources": [{"id": "b", "type": "AWS::S3", "containsPii": true, "blockPublicAcls": false, "encryption": "none"}]}
	count(gdpr.deny) == 2 with input as bad
}

test_gdpr_not_applied_without_compliance if {
	count(gdpr.deny) == 0 with input as {"metadata": {"compliance": ["CIS-1.5"]}, "resources": [{"id": "b", "type": "AWS::S3", "containsPii": true, "blockPublicAcls": false}]}
}

test_residency_non_eu_denied if {
	count(residency.deny) == 1 with input as {"metadata": {"compliance": ["GDPR"], "region": "us-east-1"}}
}
