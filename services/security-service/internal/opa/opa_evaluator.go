// Package opa evaluates the IR against the security policies.
// Rules mirror packages/security-rules/*.rego one-to-one. When the `opa` binary is available
// it is used as the source of truth (EvaluateWithOPA); the native engine is the fast fallback.
package opa

import (
	"bytes"
	"encoding/json"
	"fmt"
	"os/exec"
	"strings"
)

type IR struct {
	Metadata struct {
		Compliance []string `json:"compliance"`
		Region     string   `json:"region"`
	} `json:"metadata"`
	Resources []map[string]any `json:"resources"`
}

var euRegions = map[string]bool{"eu-west-1": true, "eu-central-1": true, "eu-north-1": true, "eu-west-3": true}

func boolf(r map[string]any, k string) bool  { v, _ := r[k].(bool); return v }
func strf(r map[string]any, k string) string { v, _ := r[k].(string); return v }

// EvaluateIR returns human-readable violations.
func EvaluateIR(ir IR) []string {
	var v []string
	gdpr := false
	for _, c := range ir.Metadata.Compliance {
		if c == "GDPR" {
			gdpr = true
		}
	}
	for _, r := range ir.Resources {
		id, t := strf(r, "id"), strf(r, "type")
		switch t {
		case "AWS::S3":
			if !boolf(r, "blockPublicAcls") {
				v = append(v, fmt.Sprintf("CIS-2.1.5: S3 '%s' must set blockPublicAcls=true", id))
			}
			if strf(r, "encryption") != "aws:kms" {
				v = append(v, fmt.Sprintf("CIS-2.1.1: S3 '%s' must use aws:kms encryption", id))
			}
			if !boolf(r, "versioning") {
				v = append(v, fmt.Sprintf("CIS-2.1.3: S3 '%s' must enable versioning", id))
			}
			if gdpr && boolf(r, "containsPii") && !boolf(r, "blockPublicAcls") {
				v = append(v, fmt.Sprintf("GDPR-Art32: PII bucket '%s' must not be public", id))
			}
			if gdpr && boolf(r, "containsPii") && strf(r, "encryption") != "aws:kms" {
				v = append(v, fmt.Sprintf("GDPR-Art32: PII bucket '%s' must use KMS", id))
			}
		case "AWS::RDS":
			if !boolf(r, "encrypted") {
				v = append(v, fmt.Sprintf("CIS-2.3.1: RDS '%s' must be encrypted", id))
			}
			if !boolf(r, "private") {
				v = append(v, fmt.Sprintf("CIS-2.3.3: RDS '%s' must not be publicly accessible", id))
			}
			if !boolf(r, "deletionProtection") {
				v = append(v, fmt.Sprintf("RDS '%s' must enable deletion protection", id))
			}
		case "AWS::VPC":
			if !boolf(r, "enableFlowLogs") {
				v = append(v, fmt.Sprintf("CIS-3.9: VPC '%s' must enable flow logs", id))
			}
		case "AWS::EC2":
			if boolf(r, "associatePublicIp") {
				v = append(v, fmt.Sprintf("CIS-5.x: EC2 '%s' must not associate a public IP", id))
			}
			if !boolf(r, "requireImdsV2") {
				v = append(v, fmt.Sprintf("CIS-5.6: EC2 '%s' must require IMDSv2", id))
			}
			if !boolf(r, "encryptedRoot") {
				v = append(v, fmt.Sprintf("CIS-2.2.1: EC2 '%s' root volume must be encrypted", id))
			}
		case "AWS::SG":
			if ing, ok := r["ingress"].([]any); ok {
				for _, i := range ing {
					if m, ok := i.(map[string]any); ok && strf(m, "cidr") == "0.0.0.0/0" {
						port, _ := m["port"].(float64)
						v = append(v, fmt.Sprintf("CIS-5.2: SG '%s' allows 0.0.0.0/0 ingress on port %d", id, int(port)))
					}
				}
			}
		}
	}
	if gdpr && !euRegions[ir.Metadata.Region] {
		v = append(v, fmt.Sprintf("GDPR-Ch5: region '%s' is outside the allowed EU list", ir.Metadata.Region))
	}
	return v
}

// EvaluateWithOPA shells out to `opa eval` against the Rego bundle (authoritative engine).
func EvaluateWithOPA(irJSON []byte, policyDir string) ([]string, error) {
	cmd := exec.Command("opa", "eval", "-f", "json", "-d", policyDir, "--stdin-input",
		"data.securevibe.deny") // aggregator in packages/security-rules/src/main.rego
	cmd.Stdin = bytes.NewReader(irJSON)
	out, err := cmd.Output()
	if err != nil {
		return nil, err
	}
	var res struct {
		Result []struct {
			Expressions []struct {
				Value []string `json:"value"`
			} `json:"expressions"`
		} `json:"result"`
	}
	if err := json.Unmarshal(out, &res); err != nil {
		return nil, err
	}
	var msgs []string
	for _, r := range res.Result {
		for _, e := range r.Expressions {
			for _, m := range e.Value {
				if strings.TrimSpace(m) != "" {
					msgs = append(msgs, m)
				}
			}
		}
	}
	return msgs, nil
}
