#!/usr/bin/env bash
# Run every unit-test suite in the monorepo and print a summary. Live integration/UI tests need the stack (see README).
cd "$(dirname "$0")/.."
export PATH="${CARGO_BIN:-$PATH}"
pass=0; fail=0
run() { # run <label> <cmd...>
  local label="$1"; shift
  local out; out=$("$@" 2>&1); local rc=$?
  local line; line=$(echo "$out" | grep -E "passed|PASS:|test result|Tests " | tail -1)
  case "$label" in *go\ test*) line="$(echo "$out" | grep -c '^ok') packages ok, $(echo "$out" | grep -c 'no test files') without tests";; esac
  if [ $rc -eq 0 ]; then printf "  PASS  %-28s %s\n" "$label" "$line"; pass=$((pass+1)); else printf "  FAIL  %-28s\n%s\n" "$label" "$out" | head -30; fail=$((fail+1)); fi
}
echo "SecureVibe OS - unit test suites"
run "ir-schema (Zod/Vitest)"     bash -c "cd packages/ir-schema && npx vitest run"
run "security-rules (Rego/OPA)"  bash -c "cd packages/security-rules && opa test src tests"
run "compiler-service (pytest)"  bash -c "cd services/compiler-service && python3 -m pytest -q tests"
run "ai-service (pytest)"        bash -c "cd services/ai-service && python3 -m pytest -q tests"
run "security-service (go test)" bash -c "cd services/security-service && go vet ./... && go test ./..."
run "reverse-parser (cargo)"     bash -c "cd services/reverse-parser-service && cargo test"
run "devops-service (Vitest)"    bash -c "cd services/devops-service && npx vitest run"
run "e2e pipeline (script)"      python3 scripts/e2e.py
echo; echo "$pass suites passed, $fail failed"
[ $fail -eq 0 ]
