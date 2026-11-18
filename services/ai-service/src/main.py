from fastapi import FastAPI, HTTPException
from .schemas import GenerateRequest, FixRequest
from .pipeline import run
from .agents.fixer_agent import fix_ir
from .agents.ir_builder_agent import IRValidationError

app = FastAPI(title="SecureVibe AI Service", version="2.0.0")

@app.post("/generate-ir")
def generate_ir(req: GenerateRequest):
    if not req.prompt and not req.canvas_ir:
        raise HTTPException(400, "prompt or canvas_ir required")
    try:
        return run(req.prompt, req.canvas_ir)
    except IRValidationError as e:
        raise HTTPException(422, str(e))

@app.post("/fix-ir")
def fix(req: FixRequest):
    return fix_ir(req.ir, req.violations)

@app.get("/health")
def health():
    return {"status": "ok", "service": "ai"}
