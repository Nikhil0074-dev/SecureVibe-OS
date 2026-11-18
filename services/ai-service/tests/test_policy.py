import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from src.policy_injection import evaluate, inject, score
from src.agents.intent_parser_agent import rule_based_parse

BAD = {"version": "v2.0", "metadata": {"compliance": ["GDPR"], "env": "prod", "region": "us-east-1"},
  "resources": [
   {"id": "s3_app", "type": "AWS::S3", "blockPublicAcls": False, "encryption": "none", "versioning": False, "containsPii": True},
   {"id": "rds_main", "type": "AWS::RDS", "private": False, "encrypted": False, "deletionProtection": False},
   {"id": "sg_web", "type": "AWS::SG", "vpc": "v", "ingress": [{"port": 22, "cidr": "0.0.0.0/0"}]}]}

def test_violations_detected_then_fixed():
    assert len(evaluate(BAD)) >= 8
    fixed, fixes = inject(BAD)
    assert fixes and evaluate(fixed) == []
    assert fixed["metadata"]["region"] == "eu-west-1"
    assert score(evaluate(fixed), 3) == 100

def test_intent_parser_gdpr_3tier():
    i = rule_based_parse("Create 3-tier app with private RDS, GDPR compliant")
    assert {"vpc", "rds", "ec2"} <= set(i.resources) and "GDPR" in i.compliance and i.region.startswith("eu-")

from src.policy_injection import ensure_dependencies
from src.pipeline import run

def test_missing_vpc_is_added_and_wired():
    ir = {"version": "v2.0", "metadata": {"compliance": [], "region": "eu-west-1"},
          "resources": [{"id": "legacy", "type": "AWS::RDS", "private": True, "encrypted": True, "deletionProtection": True, "dependencies": []}]}
    fixes = ensure_dependencies(ir)
    assert ir["resources"][0]["type"] == "AWS::VPC" and ir["resources"][1]["dependencies"] == [ir["resources"][0]["id"]]
    assert len(fixes) == 2

def test_existing_vpc_not_duplicated():
    ir = {"metadata": {}, "resources": [{"id": "v", "type": "AWS::VPC"}, {"id": "e", "type": "AWS::EC2", "dependencies": []}]}
    ensure_dependencies(ir)
    assert [r["type"] for r in ir["resources"]].count("AWS::VPC") == 1 and ir["resources"][1]["dependencies"] == ["v"]

def test_pipeline_repairs_imported_ir_without_vpc():
    ir = {"version": "v2.0", "metadata": {"compliance": ["CIS-1.5"], "env": "prod", "region": "eu-west-1"},
          "resources": [{"id": "legacy", "type": "AWS::RDS", "private": False, "encrypted": False, "dependencies": []}]}
    out = run(canvas_ir=ir)
    assert out["violations"] == [] and any(r["type"] == "AWS::VPC" for r in out["ir"]["resources"])
