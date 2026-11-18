package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
	"sync"

	"github.com/securevibe/security-service/internal/opa"
	"github.com/securevibe/security-service/internal/scanner"
)

type scanReq struct {
	IR    opa.IR            `json:"ir"`
	Files map[string]string `json:"files"`
}
type scanResp struct {
	Score      int                `json:"score"`
	Passed     bool               `json:"passed"`
	Violations []string           `json:"violations"`
	Checkov    scanner.ScanResult `json:"checkov"`
}

func score(v, resources int) int {
	if resources < 1 {
		resources = 1
	}
	s := 100 - 100*v/(resources*3)
	if s < 0 {
		s = 0
	}
	return s
}

func scan(w http.ResponseWriter, r *http.Request) {
	r.Body = http.MaxBytesReader(w, r.Body, 5<<20)
	var req scanReq
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	// Run IR policy evaluation and HCL scan in parallel.
	var wg sync.WaitGroup
	var viol []string
	var ck scanner.ScanResult
	wg.Add(2)
	go func() { defer wg.Done(); viol = opa.EvaluateIR(req.IR) }()
	go func() {
		defer wg.Done()
		if len(req.Files) > 0 {
			ck, _ = scanner.RunCheckov(req.Files)
		}
	}()
	wg.Wait()
	total := len(viol) + len(ck.Failed)
	resp := scanResp{Score: score(total, len(req.IR.Resources)), Violations: viol, Checkov: ck}
	resp.Passed = resp.Score >= 90
	if resp.Violations == nil {
		resp.Violations = []string{}
	}
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(resp)
}

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("POST /scan", scan)
	mux.HandleFunc("GET /health", func(w http.ResponseWriter, _ *http.Request) { w.Write([]byte(`{"status":"ok","service":"security"}`)) })
	port := os.Getenv("PORT")
	if port == "" {
		port = "8003"
	}
	log.Printf("security-service listening on :%s", port)
	log.Fatal(http.ListenAndServe(":"+port, mux))
}
