"""Agent 4 - Auto-fixer: takes scanner violations and patches the IR (deterministic first, LLM for exotic cases)."""
from ..policy_injection import inject, evaluate, ensure_dependencies

def fix_ir(ir: dict, violations: list[str]) -> dict:
    patched, fixes = inject(ir)
    fixes += ensure_dependencies(patched)
    return {"ir": patched, "fixes": fixes, "remaining": evaluate(patched)}
