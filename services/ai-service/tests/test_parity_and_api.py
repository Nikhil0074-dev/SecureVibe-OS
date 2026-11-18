import json, pathlib, shutil, subprocess, sys
import pytest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from src.main import app
from src.policy_injection import evaluate

RULES = pathlib.Path(__file__).resolve().parents[3] / "packages" / "security-rules" / "src"
client = TestClient(app)

INSECURE = {"version": "v2.0", "metadata": {"compliance": ["GDPR"], "env": "prod", "region": "us-east-1"},
  "resources": [
   {"id": "b", "type": "AWS::S3", "blockPublicAcls": False, "encryption": "none", "versioning": False, "containsPii": True},
   {"id": "d", "type": "AWS::RDS", "private": False, "encrypted": False, "deletionProtection": False},
   {"id": "v", "type": "AWS::VPC", "enableFlowLogs": False},
   {"id": "e", "type": "AWS::EC2", "associatePublicIp": True, "requireImdsV2": False, "encryptedRoot": False},
   {"id": "s", "type": "AWS::SG", "vpc": "v", "ingress": [{"port": 22, "cidr": "0.0.0.0/0"}]}]}

@pytest.mark.skipif(shutil.which("opa") is None, reason="opa not installed")
def test_python_engine_matches_rego():
    out = subprocess.run(["opa", "eval", "-f", "json", "-d", str(RULES), "--stdin-input", "data.securevibe.deny"],
                         input=json.dumps(INSECURE), capture_output=True, text=True, check=True).stdout
    rego = sorted(json.loads(out)["result"][0]["expressions"][0]["value"])
    assert sorted(evaluate(INSECURE)) == rego

def test_health():
    assert client.get("/health").json() == {"status": "ok", "service": "ai"}

def test_generate_ir_from_prompt():
    r = client.post("/generate-ir", json={"prompt": "3-tier app with private RDS, GDPR compliant"})
    assert r.status_code == 200
    body = r.json()
    assert body["violations"] == []
    types = {x["type"] for x in body["ir"]["resources"]}
    assert {"AWS::VPC", "AWS::RDS", "AWS::EC2", "AWS::S3"} <= types

def test_generate_ir_requires_input():
    assert client.post("/generate-ir", json={}).status_code == 400

def test_canvas_ir_is_secured():
    r = client.post("/generate-ir", json={"canvas_ir": INSECURE})
    assert r.status_code == 200 and r.json()["violations"] == [] and r.json()["fixes"]

def test_canvas_ir_with_dangling_dependency_rejected():
    bad = {"version": "v2.0", "metadata": {"compliance": [], "region": "eu-west-1"},
           "resources": [{"id": "d", "type": "AWS::RDS", "dependencies": ["ghost"]}]}
    assert client.post("/generate-ir", json={"canvas_ir": bad}).status_code == 422

def test_fix_endpoint():
    r = client.post("/fix-ir", json={"ir": INSECURE, "violations": []})
    assert r.status_code == 200 and r.json()["remaining"] == []
