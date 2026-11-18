from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..compiler.terraform_compiler import compile_ir_to_terraform, CompileError
from ..compiler.cdk_compiler import compile_ir_to_cdk

router = APIRouter()


class CompileRequest(BaseModel):
    ir: dict
    target: str = "terraform"   # terraform | cdk


@router.post("/compile")
def compile_ir(req: CompileRequest):
    try:
        files = compile_ir_to_terraform(req.ir) if req.target == "terraform" else compile_ir_to_cdk(req.ir)
    except CompileError as e:
        raise HTTPException(422, str(e))
    return {"target": req.target, "files": files}
