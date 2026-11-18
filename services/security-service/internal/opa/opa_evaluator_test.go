package opa

import "testing"

func TestInsecureS3AndRDSDetected(t *testing.T) {
	var ir IR
	ir.Metadata.Region = "us-east-1"
	ir.Metadata.Compliance = []string{"GDPR"}
	ir.Resources = []map[string]any{
		{"id": "b", "type": "AWS::S3", "blockPublicAcls": false, "containsPii": true},
		{"id": "d", "type": "AWS::RDS", "private": false, "encrypted": false},
	}
	if got := len(EvaluateIR(ir)); got < 6 {
		t.Fatalf("expected >=6 violations, got %d", got)
	}
}
