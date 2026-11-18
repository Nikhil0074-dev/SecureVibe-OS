#!/usr/bin/env python3
"""End-to-end smoke test without Docker: prompt -> IR -> Terraform -> scan -> fix loop -> write project."""
import sys, json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
# Both services use a top-level `src` package, so import them one after the other.
sys.path.insert(0, str(root / "services" / "ai-service"))
from src.pipeline import run
from src.policy_injection import evaluate, score
for m in [m for m in sys.modules if m == "src" or m.startswith("src.")]: del sys.modules[m]
sys.path[0] = str(root / "services" / "compiler-service")
from src.compiler.terraform_compiler import compile_ir_to_terraform, write_project

def main(prompt: str):
    print(f"PROMPT: {prompt}\n")
    out = run(prompt=prompt)
    for t in out["trace"]: print("  -", t)
    ir = out["ir"]
    files = compile_ir_to_terraform(ir)
    sc = score(evaluate(ir), len(ir["resources"]))
    print(f"\nCompiled files: {list(files)}\nSecurity score: {sc}/100")
    dest = root / "generated" / "demo"
    write_project(files, str(dest))
    (dest / "ir.json").write_text(json.dumps(ir, indent=2))
    print(f"Written to {dest}")
    assert sc >= 90, "score below gate"

if __name__ == "__main__":
    main(" ".join(sys.argv[1:]) or "Create 3-tier app with private RDS, GDPR compliant")
