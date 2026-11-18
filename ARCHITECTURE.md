# Architecture (C4)

**L1 Context** — Developer → SecureVibe → {GitHub API, AWS Pricing/Infracost, Claude API, Terraform Registry}.

**L2 Containers** — web (Next.js :3000) → api-gateway (NestJS :4000, SSE) → ai-service (:8001), compiler-service (:8002),
security-service (Go :8003), reverse-parser-service (Rust :8004), devops-service (Node :8005); data: Postgres (IR JSONB), Redis, Neo4j, Pinecone, S3.

**L3 AI service** — `pipeline.run`: Intent Parser → Hybrid Retriever (graph + vector) → IR Builder (validated) → Policy Injection → IR.

**Generation loop** (`api-gateway/generation.service.ts`): ai → compile → scan → if score < 90: fixer → recompile (max 3) → cost + STRIDE.

**Rule parity** — the same CIS/GDPR rules live in three places by design: Rego (authoritative, `packages/security-rules`),
Go (`opa_evaluator.go`, fast path), Python (`policy_injection.py`, auto-remediation). Change one → change all (tests cover each).

**Deployment** — EKS (private endpoint) + gVisor runtime class, RDS Multi-AZ, ArgoCD/Kustomize; CI = pytest, vitest, go test, opa test, Semgrep, Trivy.
