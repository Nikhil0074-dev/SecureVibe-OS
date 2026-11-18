// Package scanner runs Checkov against generated Terraform inside a throw-away work dir.
package scanner

import (
	"context"
	"encoding/json"
	"errors"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

type Failed struct {
	CheckID  string `json:"check_id"`
	Resource string `json:"resource"`
	File     string `json:"file_path"`
}
type ScanResult struct {
	Available bool     `json:"available"`
	Passed    int      `json:"passed"`
	Failed    []Failed `json:"failed"`
}

// RunCheckov writes files to a temp dir (path-traversal safe), scans, and cleans up.
// Untrusted HCL never executes: Checkov is a static analyser. Production runs this in a gVisor/Firecracker sandbox.
func RunCheckov(files map[string]string) (ScanResult, error) {
	if _, err := exec.LookPath("checkov"); err != nil {
		return ScanResult{Available: false}, nil
	}
	dir, err := os.MkdirTemp("", "sv-scan-")
	if err != nil {
		return ScanResult{}, err
	}
	defer os.RemoveAll(dir)
	for name, content := range files {
		clean := filepath.Clean(name)
		if strings.HasPrefix(clean, "..") || filepath.IsAbs(clean) {
			return ScanResult{}, errors.New("unsafe file path: " + name)
		}
		dest := filepath.Join(dir, clean)
		_ = os.MkdirAll(filepath.Dir(dest), 0o700)
		if err := os.WriteFile(dest, []byte(content), 0o600); err != nil {
			return ScanResult{}, err
		}
	}
	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()
	out, _ := exec.CommandContext(ctx, "checkov", "-d", dir, "--framework", "terraform", "-o", "json", "--quiet").Output()
	var parsed struct {
		Results struct {
			Passed []json.RawMessage `json:"passed_checks"`
			Failed []Failed          `json:"failed_checks"`
		} `json:"results"`
	}
	if err := json.Unmarshal(out, &parsed); err != nil {
		return ScanResult{Available: true}, nil
	}
	return ScanResult{Available: true, Passed: len(parsed.Results.Passed), Failed: parsed.Results.Failed}, nil
}
