package scanner

import "testing"

func TestRejectsPathTraversal(t *testing.T) {
	// Only meaningful when checkov exists; when absent RunCheckov returns Available=false before writing anything.
	res, err := RunCheckov(map[string]string{"../evil.tf": "x"})
	if err == nil && res.Available {
		t.Fatal("expected path traversal to be rejected")
	}
}

func TestGracefulWhenCheckovMissing(t *testing.T) {
	res, err := RunCheckov(map[string]string{"main.tf": ""})
	if err != nil {
		t.Fatal(err)
	}
	_ = res // Available may be true or false depending on host; must never panic
}
