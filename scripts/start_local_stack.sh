#!/usr/bin/env bash
# Start every backend service locally without Docker (needs: python deps, go, node deps installed, postgres on :5432).
# Usage: scripts/start_local_stack.sh   ->  logs in /tmp/sv-*.log
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export DATABASE_URL="${DATABASE_URL:-postgres://securevibe:securevibe@localhost:5432/securevibe}"
bg() { # bg <dir> <log> <cmd...>  : fully detached so callers/pipes never wait on it
  local dir="$1" log="$2"; shift 2
  (cd "$dir" && setsid nohup "$@" >"$log" 2>&1 </dev/null &) >/dev/null 2>&1
}
(cd "$ROOT/services/security-service" && go build -o /tmp/sv-security ./cmd/server) || exit 1
(cd "$ROOT/apps/api-gateway" && npx nest build >/dev/null 2>&1) || exit 1
bg "$ROOT/services/ai-service"        /tmp/sv-ai.log        python3 -m uvicorn src.main:app --port 8001
bg "$ROOT/services/compiler-service"  /tmp/sv-compiler.log  python3 -m uvicorn src.main:app --port 8002
bg "$ROOT"                            /tmp/sv-security.log  /tmp/sv-security
[ -x "$ROOT/services/reverse-parser-service/target/debug/reverse-parser-service" ] && \
bg "$ROOT/services/reverse-parser-service" /tmp/sv-reverse.log ./target/debug/reverse-parser-service
bg "$ROOT/services/devops-service"    /tmp/sv-devops.log    npx tsx src/server.ts
bg "$ROOT/apps/api-gateway"           /tmp/sv-gateway.log   node dist/main.js
sleep 10
for p in 8001 8002 8003 8004 8005; do printf "%s " "$p"; curl -s -m 3 localhost:$p/health; echo; done
