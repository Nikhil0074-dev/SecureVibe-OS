from pydantic import BaseModel, Field
from typing import Any

class Intent(BaseModel):
    app_type: str = "generic"
    resources: list[str] = Field(default_factory=list)
    compliance: list[str] = Field(default_factory=lambda: ["CIS-1.5"])
    env: str = "prod"
    region: str = "eu-west-1"
    pii: bool = False

class GenerateRequest(BaseModel):
    prompt: str | None = None
    canvas_ir: dict | None = None      # Draw path: IR already built by the browser

class FixRequest(BaseModel):
    ir: dict
    violations: list[str]

SECURE_FIELDS = {"enableFlowLogs", "blockPublicAcls", "encrypted", "private"}
IRDict = dict[str, Any]
