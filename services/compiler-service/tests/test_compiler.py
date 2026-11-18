import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from src.compiler.terraform_compiler import compile_ir_to_terraform

IR = {"version": "v2.0", "metadata": {"compliance": ["GDPR"], "env": "prod", "region": "eu-west-1"},
 "resources": [
  {"id": "vpc_main", "type": "AWS::VPC", "cidr": "10.0.0.0/16", "maxAzs": 2, "enableFlowLogs": True, "secure": True, "tags": {}, "dependencies": []},
  {"id": "s3_app", "type": "AWS::S3", "blockPublicAcls": True, "encryption": "aws:kms", "versioning": True, "containsPii": True, "dataClassification": "PII", "tags": {}, "dependencies": []},
  {"id": "rds_main", "type": "AWS::RDS", "engine": "postgres", "instanceClass": "db.t3.medium", "private": True, "encrypted": True, "multiAz": False, "deletionProtection": True, "tags": {}, "dependencies": ["vpc_main"]}]}

def test_compile_contains_secure_settings():
    f = compile_ir_to_terraform(IR)
    assert "aws_flow_log" in f["main.tf"]
    assert "block_public_acls       = true" in f["main.tf"]
    assert "publicly_accessible                 = false" in f["main.tf"]
    assert "storage_encrypted                   = true" in f["main.tf"]
