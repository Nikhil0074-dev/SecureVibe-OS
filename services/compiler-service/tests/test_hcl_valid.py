import sys, pathlib, io
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import hcl2
from src.compiler.terraform_compiler import compile_ir_to_terraform
from tests.test_compiler import IR

FULL = {"metadata": {"region": "eu-west-1"}, "resources": IR["resources"] + [
    {"id": "sg_web", "type": "AWS::SG", "vpc": "vpc_main", "ingress": [{"port": 443, "cidr": "10.0.0.0/16"}], "tags": {}, "dependencies": []},
    {"id": "ec2_app", "type": "AWS::EC2", "instanceType": "t3.micro", "tags": {}, "dependencies": ["vpc_main"]}]}

def test_all_generated_files_are_valid_hcl():
    for name, content in compile_ir_to_terraform(FULL).items():
        parsed = hcl2.load(io.StringIO(content))     # raises on any syntax error
        assert parsed, name

def test_expected_resource_blocks_present():
    main = hcl2.load(io.StringIO(compile_ir_to_terraform(FULL)["main.tf"]))
    kinds = {k.strip(chr(34)) for blk in main["resource"] for k in blk}
    assert {"aws_vpc", "aws_flow_log", "aws_s3_bucket", "aws_db_instance", "aws_instance", "aws_security_group"} <= kinds
