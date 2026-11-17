# SecureVibe OS

SecureVibe OS is an AI-assisted infrastructure-as-code workspace for describing, drawing, or importing cloud infrastructure and producing Terraform with security checks, cost estimates, and a STRIDE threat model. It combines a browser-based editor with services for intent parsing, intermediate-representation (IR) validation, Terraform compilation, policy scanning, and DevOps analysis.

> **Security note:** Generated infrastructure and policy results are starting points, not a guarantee of security, regulatory compliance, or production readiness. Review generated code, provider versions, IAM permissions, networking, costs, and organizational requirements before applying changes. Never commit API keys, passwords, or other secrets.



## Capabilities

- **Describe infrastructure:** Enter a natural-language request, for example, `Create a 3-tier application with private RDS and GDPR requirements`.
- **Draw infrastructure:** Add resources to the React Flow canvas and generate code from the canvas IR.
- **Import HCL:** Submit Terraform HCL to the reverse-parser service to convert supported resources into IR.
- **Generate Terraform:** Compile supported AWS resources using Jinja2 templates.
- **Scan and score:** Evaluate IR policies and, when installed and configured, scan generated files with Checkov.
- **Repair and recompile:** The gateway can ask the AI service to repair IR when the security score is below its configured threshold, with a bounded retry loop.
- **Review estimates and threats:** The DevOps service returns a cost estimate and STRIDE threat model.
- **Persist projects:** The API gateway stores project data in PostgreSQL, including JSONB IR and security-report fields.

## Architecture and request flow

The normal generation flow is:

1. The web application sends a prompt or canvas IR to the NestJS API gateway.
2. The gateway requests validated IR from the AI service. Without an Anthropic key, the AI service can use its deterministic fallback.
3. The compiler renders Terraform files from the IR and secure-by-default templates.
4. The security service evaluates IR policies and optionally scans generated files. The gateway can request fixes and recompile when the score is below its gate.
5. The DevOps service calculates a cost estimate and STRIDE threats.
6. The gateway streams progress events and the result to the web application using server-sent events (SSE).

The reverse-parser service is a separate HCL-to-IR endpoint. PostgreSQL is used by the gateway for project persistence. Redis, Neo4j, and LocalStack are included in the Compose stack for integrations and local development; their presence does not mean every feature is fully implemented or active.

### Services and local ports

| Component | Local port | Role |
|---|---:|---|
| Web application | 3000 | Next.js editor, canvas, and code view |
| API gateway | 4000 | NestJS API, SSE orchestration, project persistence |
| AI service | 8001 | Prompt parsing, IR generation, and repair |
| Compiler service | 8002 | IR-to-Terraform compilation |
| Security service | 8003 | Policy evaluation and optional Checkov scan |
| Reverse-parser service | 8004 | HCL-to-IR parsing |
| DevOps service | 8005 | Cost estimate, STRIDE analysis, GitOps endpoint |
| PostgreSQL | 5432 | Gateway project database |
| Redis | 6379 | Local supporting service |
| Neo4j | 7474, 7687 | Browser and Bolt endpoints |
| LocalStack | 4566 | Local AWS-compatible endpoint |

## Repository layout

```text
apps/
  api-gateway/             NestJS API and orchestration gateway
  web/                     Next.js frontend with React Flow and Monaco
packages/
  ir-schema/               Shared TypeScript/Zod IR package and tests
  security-rules/          OPA/Rego policies and tests
  tf-secure-templates/     Jinja2 templates for generated Terraform
services/
  ai-service/              FastAPI prompt, IR, and repair service
  compiler-service/        FastAPI Terraform compiler
  devops-service/          TypeScript cost, STRIDE, and GitOps endpoints
  reverse-parser-service/  Rust HCL parser and IR converter
  security-service/        Go policy and Checkov scanning service
infra/
  terraform/               Terraform for platform infrastructure
  kubernetes/              Kubernetes base manifests and overlays
generated/demo/            Output written by the local E2E script
scripts/                   E2E, integration, UI, and test-runner scripts
docs/screenshots/          Project screenshots
```

## Requirements

### For the local E2E pipeline

- Python 3.12 or newer is recommended.
- Install the Python dependencies used by the two Python services and tests:

```powershell
python -m pip install -r services/compiler-service/requirements.txt -r services/ai-service/requirements.txt pytest python-hcl2
```

### For the full stack or all repository tests

Install the relevant toolchains for the components you want to run:

- Docker Desktop or Docker Engine with the Compose plugin, for the containerized stack.
- Node.js and Corepack/pnpm for the web app, API gateway, IR schema, and DevOps service.
- Python and the service requirements for the AI and compiler services.
- Go for the security service.
- Rust/Cargo for the reverse-parser service.
- OPA CLI for Rego tests.
- Playwright with its Chromium browser for the browser UI test.

The JavaScript workspace declares pnpm as its package manager. From the repository root, enable Corepack if needed and install workspace dependencies:

```powershell
corepack enable
corepack pnpm install
```

## Quick start: local pipeline

These scripts live in the **repository root**, not in `apps/web`. From `apps/web`, run the following PowerShell commands:

```powershell
Set-Location ..\\..
python scripts\\e2e.py "Create a 3-tier app with private RDS, GDPR compliant"
python -m pytest -q

Set-Location services\\compiler-service
python -m pytest -q tests
```

The root pytest command runs the AI service tests; compiler tests run separately because both services import a package named `src`. The `apps/web` directory has no Python tests, so pytest there reports `no tests ran`.

The E2E script prints its pipeline trace and writes Terraform files plus `ir.json` under `generated/demo/`. This generated directory is ignored by Git. Review the generated files before using them.

The repository also includes `scripts/run_all_tests.sh` for the broader cross-language unit-test set; run it in a Bash-compatible shell after installing the needed language toolchains and dependencies.

## Run the full stack with Docker Compose

1. Create a local environment file from the example:

```powershell
Copy-Item .env.example .env
```

2. Edit `.env` for your environment. Set an Anthropic key only if you want to use the hosted model path; the deterministic AI fallback does not require one. Replace development credentials before exposing services beyond your machine.
3. Start the stack from the repository root:

```powershell
docker compose up --pull always --build
```

The Compose configuration overrides `DATABASE_URL` inside the gateway to use the Compose service hostname `postgres`; the localhost URL in `.env` is for running services directly on the host. Set `POSTGRES_PASSWORD` in `.env` to a private development value before starting the stack. The same value is used by PostgreSQL and the gateway's container connection string.

The web application is served at `http://localhost:3000` and the API gateway at `http://localhost:4000`. Service health endpoints are available at `/health` on the individual backend services.

Stop the stack with `Ctrl+C`, or run:

```powershell
docker compose down
```

The PostgreSQL data volume is named `pgdata` and remains after `docker compose down`. To remove it as well, use `docker compose down --volumes`; this deletes the local database data.

## Run services locally

Local process startup requires the dependencies for the selected services and a PostgreSQL instance accessible to the gateway. Configure `.env` first.

The repository provides a Bash startup helper:

```bash
scripts/start_local_stack.sh
```

It builds the Go security service and NestJS gateway, starts the Python and Node services in the background, and probes service health endpoints. The helper expects the reverse-parser binary to have been built already; build it from its service directory before starting the helper:

```bash
cd services/reverse-parser-service
cargo build
cd ../..
scripts/start_local_stack.sh
```

Start the web app separately after installing its dependencies and building it:

```bash
cd apps/web
npm install
npm run build
npm start
```

The local-stack helper is a Bash script; use Git Bash, WSL, or another compatible shell on Windows. For Windows-only Python development, run the E2E pipeline and pytest commands directly in PowerShell.

## Configuration

`.env.example` lists the environment variables used or reserved for integrations. Copy it to `.env` and change values as appropriate. The Compose file also defines local development defaults for several services and data stores; inspect `docker-compose.yml` before relying on `.env` values to override those defaults.

| Variable | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | Optional key for the hosted AI model path; empty uses the deterministic fallback where supported. |
| `LLM_MODEL` | Model identifier used by the AI integration. |
| `AI_SERVICE_URL` | AI service base URL. |
| `COMPILER_SERVICE_URL` | Compiler service base URL. |
| `SECURITY_SERVICE_URL` | Security service base URL. |
| `REVERSE_PARSER_URL` | Reverse-parser service base URL. |
| `DEVOPS_SERVICE_URL` | DevOps service base URL. |
| `DATABASE_URL` | PostgreSQL connection string used by the API gateway. |
| `REDIS_URL` | Redis connection string for integrations. |
| `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` | Neo4j connection settings. |
| `PINECONE_API_KEY` | Reserved for the Pinecone integration. |
| `GITHUB_TOKEN` | Token for the GitHub push integration. |
| `JWT_SECRET` | Reserved for authentication-related configuration. |

Supply secrets at runtime or through a protected local environment file. Do not add real credentials to a Dockerfile, source file, committed Compose file, or image layer. The example values are for local development only and should not be treated as production secrets.

## Tests and validation

### Python

The root pytest command runs the AI service tests. Run compiler tests separately from their service directory because both Python services use a top-level package named `src`; collecting both test suites in one pytest process can cause an import collision.

```powershell
python -m pytest -q
Set-Location services\\compiler-service
python -m pytest -q tests
```

The live integration and browser scripts require a running stack and are not collected as unit tests:

```powershell
python scripts/integration_test.py
python scripts/ui_test.py
```

### JavaScript and TypeScript

From the repository root, install dependencies first. Then run workspace tasks:

```powershell
corepack pnpm test
corepack pnpm build
```

Individual package scripts are declared in their `package.json` files. For example, the IR schema and DevOps service expose Vitest tests; the web app and API gateway expose build scripts.

### Go, Rust, and Rego

```powershell
cd services/security-service
go vet ./...
go test ./...

cd ../reverse-parser-service
cargo test

cd ../../packages/security-rules
opa test src tests -v
```

Run each command from the indicated directory and install the corresponding toolchain first. `scripts/run_all_tests.sh` combines these checks with the JavaScript, Python, and local E2E suites in a Bash environment.

### Live application checks

Start the complete stack before running `scripts/integration_test.py` or `scripts/ui_test.py`. The integration script exercises HTTP endpoints and persistence; the UI script uses Playwright and saves screenshots under `docs/screenshots/`. These are runtime checks, not offline unit tests.

## Generated files and screenshots

- `generated/demo/` contains output from `scripts/e2e.py`; it is generated locally and ignored by Git.
- `docs/screenshots/` contains example captures of the interface, generated infrastructure, policies, and test runs. The UI test may refresh its live screenshots when run.

## Current boundaries

The repository contains active services as well as integrations and features that may be partial or stubbed. Check the implementation and test coverage before depending on a capability in production. In particular:

- Hosted-model behavior requires credentials and was not verified by the deterministic local E2E path.
- Checkov scanning depends on the external Checkov executable being available; without it, the scanner's behavior is limited.
- Terraform syntax parsing does not replace `terraform validate`, provider-schema checks, a plan, or a security review.
- Terraform and Kubernetes infrastructure should be validated against the target cloud and cluster before deployment; do not apply the manifests blindly.
- Redis, Neo4j, LocalStack, Pinecone, GitHub integration, authentication/JWT, and additional infrastructure templates may be unused, incomplete, or environment-dependent.
- Passing unit tests does not demonstrate the full containerized stack, live integrations, or cloud deployment unless those checks were run in the target environment.

## Troubleshooting

- **Python service import errors:** Run `python -m pytest -q` from the repository root for AI tests and run `python -m pytest -q tests` from `services/compiler-service` for compiler tests; avoid collecting both `src`-based suites in one process.
- **Connection refused from integration/UI tests:** Start the full stack first and verify the services are listening on the ports listed above.
- **Missing `src` or Python module errors:** Install the relevant requirements and run commands from the intended service directory.
- **Missing pnpm:** Run `corepack enable`, then use `corepack pnpm` from the repository root.
- **npm registry timeouts:** Check network/proxy access to the configured package registry, then retry dependency installation before running JavaScript tests.
- **Missing Go, Rust, or OPA commands:** Install the corresponding toolchain/CLI and confirm it is available in the shell's PATH.
- **Docker build or startup errors:** Validate Compose with `docker compose config`, then inspect service logs with `docker compose logs <service>`.
- **Database connection errors:** Confirm PostgreSQL is running, the configured database and credentials match, and the gateway can reach the database host from its runtime environment.

## Screenshots

Selected examples in `docs/screenshots/` include:

- `01-e2e-pipeline-run.png` — prompt-to-infrastructure pipeline.
- `02-all-unit-tests.png` and `02b-live-integration-tests.png` — test and integration captures.
- `04-ir-schema-zod.png` — IR schema example.
- `05-generated-terraform-rds.png` — generated RDS Terraform.
- `06-s3-rego-policy.png` — S3 policy example.
- `08-live-web-initial.png` — web editor.
- `09-live-vibe-generation.png` — prompt-driven generation.
- `10-live-canvas-generation.png` — canvas-driven generation.
