"""Layer 4 - Policy Injection. Python mirror of packages/security-rules (Rego).
`evaluate()` returns violations; `inject()` auto-remediates the IR (e.g. flips public S3 to blocked)."""
EU = {"eu-west-1", "eu-central-1", "eu-north-1", "eu-west-3"}

def evaluate(ir: dict) -> list[str]:
    v: list[str] = []
    comp = ir.get("metadata", {}).get("compliance", [])
    for r in ir["resources"]:
        t, i = r["type"], r["id"]
        if t == "AWS::S3":
            if r.get("blockPublicAcls") is not True: v.append(f"CIS-2.1.5: S3 '{i}' must set blockPublicAcls=true")
            if r.get("encryption") != "aws:kms": v.append(f"CIS-2.1.1: S3 '{i}' must use aws:kms encryption")
            if r.get("versioning") is not True: v.append(f"CIS-2.1.3: S3 '{i}' must enable versioning")
        if t == "AWS::RDS":
            if r.get("encrypted") is not True: v.append(f"CIS-2.3.1: RDS '{i}' must be encrypted")
            if r.get("private") is not True: v.append(f"CIS-2.3.3: RDS '{i}' must not be publicly accessible")
            if r.get("deletionProtection") is not True: v.append(f"RDS '{i}' must enable deletion protection")
        if t == "AWS::VPC" and r.get("enableFlowLogs") is not True:
            v.append(f"CIS-3.9: VPC '{i}' must enable flow logs")
        if t == "AWS::EC2":
            if r.get("associatePublicIp"): v.append(f"CIS-5.x: EC2 '{i}' must not associate a public IP")
            if r.get("requireImdsV2") is not True: v.append(f"CIS-5.6: EC2 '{i}' must require IMDSv2")
            if r.get("encryptedRoot") is not True: v.append(f"CIS-2.2.1: EC2 '{i}' root volume must be encrypted")
        if t == "AWS::SG":
            for ing in r.get("ingress", []):
                if ing.get("cidr") == "0.0.0.0/0": v.append(f"CIS-5.2: SG '{i}' allows 0.0.0.0/0 ingress on port {ing.get('port')}")
        if "GDPR" in comp and t == "AWS::S3" and r.get("containsPii") and r.get("blockPublicAcls") is not True:
            v.append(f"GDPR-Art32: PII bucket '{i}' must not be public")
        if "GDPR" in comp and t == "AWS::S3" and r.get("containsPii") and r.get("encryption") != "aws:kms":
            v.append(f"GDPR-Art32: PII bucket '{i}' must use KMS")
    if "GDPR" in comp and ir["metadata"].get("region") not in EU:
        v.append(f"GDPR-Ch5: region '{ir['metadata'].get('region')}' is outside the allowed EU list")
    return v

def inject(ir: dict) -> tuple[dict, list[str]]:
    """Return (patched IR, list of applied fixes)."""
    fixes: list[str] = []
    for r in ir["resources"]:
        t = r["type"]
        def setf(k, val):
            if r.get(k) != val: r[k] = val; fixes.append(f"{r['id']}.{k} -> {val}")
        if t == "AWS::S3": setf("blockPublicAcls", True); setf("encryption", "aws:kms"); setf("versioning", True)
        if t == "AWS::RDS": setf("encrypted", True); setf("private", True); setf("deletionProtection", True)
        if t == "AWS::VPC": setf("enableFlowLogs", True)
        if t == "AWS::EC2": setf("associatePublicIp", False); setf("requireImdsV2", True); setf("encryptedRoot", True)
        if t == "AWS::SG":
            before = len(r.get("ingress", []))
            r["ingress"] = [i for i in r.get("ingress", []) if i.get("cidr") != "0.0.0.0/0"]
            if len(r["ingress"]) != before: fixes.append(f"{r['id']}: removed 0.0.0.0/0 ingress")
    if "GDPR" in ir["metadata"].get("compliance", []) and ir["metadata"].get("region") not in EU:
        fixes.append(f"metadata.region {ir['metadata'].get('region')} -> eu-west-1"); ir["metadata"]["region"] = "eu-west-1"
    return ir, fixes

def score(violations: list[str], resource_count: int) -> int:
    return max(0, 100 - int(100 * len(violations) / max(1, resource_count * 3)))


NEEDS_VPC = {"AWS::RDS", "AWS::EC2", "AWS::SG"}

def ensure_dependencies(ir: dict) -> list[str]:
    """Imported/drawn IRs may reference networking that does not exist: add a secure VPC and wire dependencies."""
    fixes: list[str] = []
    res = ir["resources"]
    vpcs = [r["id"] for r in res if r["type"] == "AWS::VPC"]
    if not any(r["type"] in NEEDS_VPC for r in res):
        return fixes
    if not vpcs:
        ids = {r["id"] for r in res}
        vid = next(c for c in ["vpc_main"] + [f"vpc_main_{i}" for i in range(2, 99)] if c not in ids)
        res.insert(0, {"id": vid, "type": "AWS::VPC", "cidr": "10.0.0.0/16", "maxAzs": 2,
                       "enableFlowLogs": True, "secure": True, "tags": {}, "dependencies": []})
        vpcs.append(vid); fixes.append(f"added missing VPC '{vid}'")
    for r in res:
        if r["type"] in {"AWS::RDS", "AWS::EC2"} and not r.get("dependencies") and not r.get("vpc"):
            r["dependencies"] = [vpcs[0]]; fixes.append(f"{r['id']}.dependencies -> {vpcs[0]}")
        if r["type"] == "AWS::SG" and not r.get("vpc"):
            r["vpc"] = vpcs[0]; fixes.append(f"{r['id']}.vpc -> {vpcs[0]}")
    return fixes
