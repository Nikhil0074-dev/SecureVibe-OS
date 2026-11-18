import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.compiler.terraform_compiler import compile_ir_to_terraform, write_project, CompileError
from tests.test_compiler import IR

client = TestClient(app)

def test_compile_endpoint_terraform():
    r = client.post("/compile", json={"ir": IR})
    assert r.status_code == 200
    assert set(r.json()["files"]) == {"providers.tf", "main.tf", "outputs.tf"}

def test_compile_endpoint_cdk():
    r = client.post("/compile", json={"ir": IR, "target": "cdk"})
    assert r.status_code == 200 and "lib/securevibe-stack.ts" in r.json()["files"]

def test_rds_without_vpc_is_422():
    ir = {"metadata": {"region": "eu-west-1"}, "resources": [dict(IR["resources"][2], dependencies=[])]}
    assert client.post("/compile", json={"ir": ir}).status_code == 422

def test_write_project_blocks_path_traversal(tmp_path):
    with pytest.raises(CompileError):
        write_project({"../evil.tf": "x"}, str(tmp_path / "out"))

def test_every_resource_type_renders():
    ir = {"metadata": {"region": "eu-west-1"}, "resources": [
        IR["resources"][0], IR["resources"][1], IR["resources"][2],
        {"id": "sg_web", "type": "AWS::SG", "vpc": "vpc_main", "ingress": [{"port": 443, "cidr": "10.0.0.0/16"}], "tags": {}, "dependencies": []},
        {"id": "ec2_app", "type": "AWS::EC2", "instanceType": "t3.micro", "tags": {}, "dependencies": ["vpc_main"]}]}
    main = compile_ir_to_terraform(ir)["main.tf"]
    for needle in ['resource "aws_security_group" "sg_web"', 'http_tokens   = "required"', 'encrypted = true']:
        assert needle in main
