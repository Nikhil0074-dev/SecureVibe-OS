"""Agent 3 - Intent + context -> validated IR with SECURE DEFAULTS FORCED (Python mirror of the Zod schema)."""
from ..schemas import Intent

class IRValidationError(ValueError): pass

def build_ir(intent: Intent, bundle: dict) -> dict:
    res: list[dict] = []
    want = list(dict.fromkeys(intent.resources + bundle.get("required_dependencies", [])))
    if "vpc" in want:
        res.append({"id": "vpc_main", "type": "AWS::VPC", "cidr": "10.0.0.0/16", "maxAzs": 2,
                    "enableFlowLogs": True, "secure": True, "tags": {}, "dependencies": []})
    dep = ["vpc_main"] if "vpc" in want else []
    if "s3" in want:
        res.append({"id": "s3_app", "type": "AWS::S3", "blockPublicAcls": True, "encryption": "aws:kms",
                    "versioning": True, "containsPii": intent.pii,
                    "dataClassification": "PII" if intent.pii else "INTERNAL", "tags": {}, "dependencies": []})
    if "ec2" in want:
        res.append({"id": "ec2_app", "type": "AWS::EC2", "instanceType": "t3.micro", "subnetGroup": "private",
                    "requireImdsV2": True, "encryptedRoot": True, "associatePublicIp": False,
                    "tags": {}, "dependencies": dep})
    if "rds" in want:
        res.append({"id": "rds_main", "type": "AWS::RDS", "engine": "postgres", "instanceClass": "db.t3.medium",
                    "private": True, "encrypted": True, "multiAz": intent.env == "prod",
                    "subnetGroup": "private", "deletionProtection": True, "tags": {}, "dependencies": dep})
    conns = []
    if any(r["id"] == "ec2_app" for r in res) and any(r["id"] == "rds_main" for r in res):
        conns.append({"from": "ec2_app", "to": "rds_main", "port": 5432, "encrypted": True})
    ir = {"version": "v2.0",
          "metadata": {"compliance": intent.compliance, "env": intent.env, "region": intent.region},
          "resources": res, "connections": conns}
    validate_ir(ir)
    return ir

def validate_ir(ir: dict) -> None:
    ids = [r["id"] for r in ir.get("resources", [])]
    if not ids: raise IRValidationError("IR has no resources")
    if len(ids) != len(set(ids)): raise IRValidationError("duplicate ids")
    for r in ir["resources"]:
        for d in r.get("dependencies", []):
            if d not in ids: raise IRValidationError(f"{r['id']} depends on unknown {d}")
    for c in ir.get("connections", []):
        if c["from"] not in ids or c["to"] not in ids: raise IRValidationError("bad connection")
