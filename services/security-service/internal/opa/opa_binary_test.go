package opa

import (
	"encoding/json"
	"os/exec"
	"sort"
	"testing"
)

// Parity test: the native Go engine and the authoritative Rego bundle (real `opa` binary) must agree.
func TestGoEngineMatchesRego(t *testing.T) {
	if _, err := exec.LookPath("opa"); err != nil {
		t.Skip("opa binary not installed")
	}
	ir := map[string]any{
		"metadata": map[string]any{"compliance": []string{"GDPR"}, "region": "us-east-1"},
		"resources": []map[string]any{
			{"id": "b", "type": "AWS::S3", "blockPublicAcls": false, "encryption": "none", "versioning": false, "containsPii": true},
			{"id": "d", "type": "AWS::RDS", "private": false, "encrypted": false, "deletionProtection": false},
			{"id": "v", "type": "AWS::VPC", "enableFlowLogs": false},
			{"id": "e", "type": "AWS::EC2", "associatePublicIp": true, "requireImdsV2": false, "encryptedRoot": false},
			{"id": "s", "type": "AWS::SG", "ingress": []map[string]any{{"port": 22, "cidr": "0.0.0.0/0"}}},
		},
	}
	raw, _ := json.Marshal(ir)
	var parsed IR
	_ = json.Unmarshal(raw, &parsed)

	goV := EvaluateIR(parsed)
	regoV, err := EvaluateWithOPA(raw, "../../../../packages/security-rules/src")
	if err != nil {
		t.Fatalf("opa eval failed: %v", err)
	}
	sort.Strings(goV)
	sort.Strings(regoV)
	if len(goV) != len(regoV) {
		t.Fatalf("engines disagree: go=%d rego=%d\ngo=%v\nrego=%v", len(goV), len(regoV), goV, regoV)
	}
	for i := range goV {
		if goV[i] != regoV[i] {
			t.Errorf("mismatch:\n go:   %s\n rego: %s", goV[i], regoV[i])
		}
	}
}

func TestSecureIRHasNoViolations(t *testing.T) {
	var ir IR
	ir.Metadata.Region = "eu-west-1"
	ir.Metadata.Compliance = []string{"GDPR"}
	ir.Resources = []map[string]any{
		{"id": "b", "type": "AWS::S3", "blockPublicAcls": true, "encryption": "aws:kms", "versioning": true, "containsPii": true},
		{"id": "d", "type": "AWS::RDS", "private": true, "encrypted": true, "deletionProtection": true},
	}
	if v := EvaluateIR(ir); len(v) != 0 {
		t.Fatalf("expected none, got %v", v)
	}
}
