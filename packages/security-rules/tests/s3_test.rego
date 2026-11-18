package cis.aws.s3_test

import data.cis.aws.s3
import rego.v1

test_secure_bucket_passes if {
	count(s3.deny) == 0 with input as {"resources": [{"id": "b", "type": "AWS::S3", "blockPublicAcls": true, "encryption": "aws:kms", "versioning": true}]}
}

test_public_bucket_denied if {
	count(s3.deny) > 0 with input as {"resources": [{"id": "b", "type": "AWS::S3", "blockPublicAcls": false, "encryption": "aws:kms", "versioning": true}]}
}
