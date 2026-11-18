#!/usr/bin/env python3
"""Live integration test. Requires the full stack running (docker compose up, or the services started locally).
Exercises: gateway SSE pipeline, validation, Postgres persistence, reverse parser, security + devops services."""
import json, sys, urllib.request, urllib.error

GW, REV, SEC = "http://localhost:4000", "http://localhost:8004", "http://localhost:8003"
passed = failed = 0

def check(name, cond, detail=""):
    global passed, failed
    if cond: passed += 1; print(f"  PASS  {name}")
    else: failed += 1; print(f"  FAIL  {name} {detail}")

def post(url, body, raw=False):
    req = urllib.request.Request(url, json.dumps(body).encode(), {"content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r: return r.status, (r.read().decode() if raw else json.loads(r.read()))
    except urllib.error.HTTPError as e: return e.code, e.read().decode()

def sse(body):
    st, txt = post(f"{GW}/generate/stream", body, raw=True)
    return st, [json.loads(l[6:]) for l in txt.split("\n\n") if l.startswith("data: ")]

print("1) Prompt -> secure Terraform via gateway SSE")
st, ev = sse({"prompt": "Create 3-tier app with private RDS, GDPR compliant"})
stages = [e["stage"] for e in ev]
check("stream returns 200", st == 200)
check("stages in order", stages[:3] == ["ai:start", "ai:ir", "compiler:start"] and stages[-1] == "complete", stages)
done = ev[-1]["data"]
check("security score >= 90", done["securityReport"]["score"] >= 90, done["securityReport"])
check("no violations", done["securityReport"]["violations"] == [])
check("3 terraform files", sorted(done["files"]) == ["main.tf", "outputs.tf", "providers.tf"])
check("RDS private+encrypted in code", "publicly_accessible                 = false" in done["files"]["main.tf"] and "storage_encrypted                   = true" in done["files"]["main.tf"])
check("cost estimated", done["cost"]["monthlyUsd"] > 0, done["cost"])
check("STRIDE threats all mitigated", len(done["threatModel"]) > 0 and all(t["mitigated"] for t in done["threatModel"]))

print("2) Insecure canvas IR is auto-secured")
bad = {"version": "v2.0", "metadata": {"compliance": ["GDPR"], "env": "prod", "region": "us-east-1"},
       "resources": [{"id": "vpc_main", "type": "AWS::VPC", "cidr": "10.0.0.0/16", "maxAzs": 2, "enableFlowLogs": False, "secure": False, "tags": {}, "dependencies": []},
                     {"id": "rds_main", "type": "AWS::RDS", "private": False, "encrypted": False, "deletionProtection": False, "multiAz": False, "engine": "postgres", "instanceClass": "db.t3.medium", "tags": {}, "dependencies": ["vpc_main"]}]}
st, ev = sse({"canvasIr": bad})
d = ev[-1]["data"]
check("ends in complete", ev[-1]["stage"] == "complete", ev[-1])
check("region forced to EU", d["ir"]["metadata"]["region"] == "eu-west-1")
check("RDS fixed", d["ir"]["resources"][1]["private"] is True and d["ir"]["resources"][1]["encrypted"] is True)
check("score 100", d["securityReport"]["score"] == 100)

print("3) Validation & errors")
st, _ = post(f"{GW}/generate/stream", {})
check("empty body -> 400", st == 400, st)
st, ev = sse({"canvasIr": {"version": "v2.0", "metadata": {}, "resources": [{"id": "d", "type": "AWS::RDS", "dependencies": ["ghost"]}]}})
check("dangling dependency surfaces as error event", ev[-1]["stage"] == "error", ev[-1])

print("4) Security service directly")
st, r = post(f"{SEC}/scan", {"ir": bad})
check("insecure IR fails gate", st == 200 and r["passed"] is False and len(r["violations"]) >= 5, r)

print("5) Reverse parser (HCL -> IR) then re-secure")
hcl = 'resource "aws_db_instance" "legacy" {\n  publicly_accessible = true\n  storage_encrypted = false\n}\nresource "aws_s3_bucket" "logs" {\n  bucket = "x"\n}\n'
st, r = post(f"{REV}/parse", {"hcl": hcl})
check("parse ok", st == 200 and len(r["ir"]["resources"]) == 2, r)
ir = r["ir"]
ir["resources"][0]["dependencies"] = []
st, ev = sse({"canvasIr": ir})
check("imported insecure IR secured end-to-end", ev[-1]["stage"] == "complete" and ev[-1]["data"]["securityReport"]["score"] >= 90, ev[-1] if ev else "")
st, r = post(f"{REV}/parse", {"hcl": "resource {{{ nope"})
check("invalid HCL -> 422", st == 422, st)

print("6) Projects API + Postgres persistence")
st, p = post(f"{GW}/projects", {"name": "integration"})
check("project created", st in (200, 201) and p["id"])
req = urllib.request.Request(f"{GW}/projects/{p['id']}/ir", json.dumps({"ir": done["ir"], "securityReport": done["securityReport"]}).encode(), {"content-type": "application/json"}, method="PUT")
urllib.request.urlopen(req)
got = json.loads(urllib.request.urlopen(f"{GW}/projects/{p['id']}").read())
check("IR round-trips through JSONB", got["ir"]["version"] == "v2.0" and got["securityReport"]["score"] >= 90)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
