"""LangGraph-style pipeline: Intent -> Retrieve -> Build IR -> Policy Injection (-> Compile handled by gateway)."""
from .agents.intent_parser_agent import parse_intent
from .agents.ir_builder_agent import build_ir, validate_ir
from .rag.retriever import hybrid_search, as_prompt_context
from .policy_injection import inject, evaluate, ensure_dependencies

def run(prompt: str | None = None, canvas_ir: dict | None = None) -> dict:
    trace = []
    if canvas_ir:
        validate_ir(canvas_ir); ir = canvas_ir; trace.append("canvas IR accepted")
    else:
        intent = parse_intent(prompt or "")
        trace.append(f"intent: {intent.model_dump()}")
        bundle = hybrid_search(intent.resources)
        trace.append(f"retrieved: {len(bundle['docs'])} docs, deps={bundle['required_dependencies']}")
        ir = build_ir(intent, bundle)
        trace.append(f"IR built with {len(ir['resources'])} resources")
    ir, fixes = inject(ir)
    fixes += ensure_dependencies(ir)
    trace.append(f"policy injection applied {len(fixes)} fixes")
    return {"ir": ir, "fixes": fixes, "violations": evaluate(ir), "trace": trace}
