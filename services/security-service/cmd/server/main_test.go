package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func call(t *testing.T, body string) (int, scanResp) {
	t.Helper()
	rec := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/scan", strings.NewReader(body))
	scan(rec, req)
	var out scanResp
	_ = json.Unmarshal(rec.Body.Bytes(), &out)
	return rec.Code, out
}

func TestScanSecureIRPasses(t *testing.T) {
	code, r := call(t, `{"ir":{"metadata":{"compliance":["CIS-1.5"],"region":"eu-west-1"},"resources":[{"id":"b","type":"AWS::S3","blockPublicAcls":true,"encryption":"aws:kms","versioning":true}]}}`)
	if code != 200 || r.Score != 100 || !r.Passed {
		t.Fatalf("code=%d resp=%+v", code, r)
	}
}

func TestScanInsecureIRFailsGate(t *testing.T) {
	code, r := call(t, `{"ir":{"metadata":{"compliance":["CIS-1.5"]},"resources":[{"id":"d","type":"AWS::RDS","private":false,"encrypted":false}]}}`)
	if code != 200 || r.Passed || len(r.Violations) != 3 {
		t.Fatalf("code=%d resp=%+v", code, r)
	}
}

func TestScanRejectsBadJSON(t *testing.T) {
	if code, _ := call(t, `{not json`); code != http.StatusBadRequest {
		t.Fatalf("want 400 got %d", code)
	}
}

func TestScoreBounds(t *testing.T) {
	if score(100, 1) != 0 || score(0, 0) != 100 {
		t.Fatal("score bounds wrong")
	}
}
