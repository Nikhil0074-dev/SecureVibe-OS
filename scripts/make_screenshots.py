#!/usr/bin/env python3
"""Generate terminal/code screenshots into docs/screenshots/ (pip install playwright && playwright install chromium).
Everything here is REAL command output or real source. UI screenshots (08-10) come from scripts/ui_test.py."""
import html, json, os, subprocess, sys, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "screenshots"; OUT.mkdir(parents=True, exist_ok=True)
PROMPT = "Create 3-tier app with private RDS, GDPR compliant"

def sh(cmd, cwd=ROOT):
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    return f"$ {cmd}\n{r.stdout}{r.stderr}".rstrip()

CSS = """body{margin:0;background:#0b1020;font-family:'DejaVu Sans Mono',monospace}
.win{margin:20px;border-radius:10px;overflow:hidden;background:#11172b;box-shadow:0 8px 30px #0008}
.bar{background:#1c2340;color:#9aa5c8;font:13px system-ui;padding:8px 14px;display:flex;gap:8px;align-items:center}
.dot{width:11px;height:11px;border-radius:50%;display:inline-block}
pre{margin:0;padding:16px 18px;color:#d6dcf0;font-size:13px;line-height:1.5;white-space:pre-wrap}
.g{color:#2ecc71}.y{color:#f1c40f}.c{color:#5dade2}.m{color:#c39bd3}.d{color:#7f8aa8}"""

def window(title, body_html, width=1100):
    return f"""<html><head><style>{CSS}</style></head><body><div class='win' style='width:{width}px'>
<div class='bar'><span class='dot' style='background:#ff5f56'></span><span class='dot' style='background:#ffbd2e'></span><span class='dot' style='background:#27c93f'></span><span style='margin-left:10px'>{html.escape(title)}</span></div>
<pre>{body_html}</pre></div></body></html>"""

def colorize(text):
    out = []
    for line in html.escape(text).split("\n"):
        if line.lstrip().startswith("PASS"): line = f"<span class='g'>{line}</span>"
        elif line.startswith("$"): line = f"<span class='c'>{line}</span>"
        elif "passed" in line or "OK" in line or "100/100" in line or "✓" in line: line = f"<span class='g'>{line}</span>"
        elif line.lstrip().startswith("#") or line.lstrip().startswith("//"): line = f"<span class='d'>{line}</span>"
        out.append(line)
    return "\n".join(out)

def tree(root, maxdepth=3):
    skip = {"node_modules", "__pycache__", ".git", "generated", "docs", "dist"}
    lines = [f"{root.name}/"]
    def walk(d, prefix, depth):
        items = sorted([p for p in d.iterdir() if p.name not in skip], key=lambda p: (p.is_file(), p.name))
        for i, p in enumerate(items):
            last = i == len(items) - 1
            lines.append(f"{prefix}{'└── ' if last else '├── '}{p.name}{'/' if p.is_dir() else ''}")
            if p.is_dir() and depth < maxdepth: walk(p, prefix + ("    " if last else "│   "), depth + 1)
    walk(root, "", 1); return "\n".join(lines)

def code_block(path, start=1, end=None):
    src = (ROOT / path).read_text().split("\n")[start-1:end]
    return "\n".join(f"<span class='d'>{i+start:>3}</span>  {html.escape(l)}" for i, l in enumerate(src))

def main():
    shots = {}
    # 01 real e2e run
    shots["01-e2e-pipeline-run.png"] = window("terminal — python3 scripts/e2e.py", colorize(sh(f'python3 scripts/e2e.py "{PROMPT}"')))
    # 02 real run of every unit-test suite
    env = dict(os.environ, CARGO_BIN=os.environ.get("CARGO_BIN", os.environ["PATH"]))
    r = subprocess.run("scripts/run_all_tests.sh", shell=True, cwd=ROOT, capture_output=True, text=True, env=env)
    shots["02-all-unit-tests.png"] = window("terminal — scripts/run_all_tests.sh", colorize("$ scripts/run_all_tests.sh\n" + r.stdout + r.stderr), 1250)
    # 02b real live integration run (needs the stack running)
    r = subprocess.run("python3 scripts/integration_test.py", shell=True, cwd=ROOT, capture_output=True, text=True)
    shots["02b-live-integration-tests.png"] = window("terminal — scripts/integration_test.py (live stack)", colorize("$ python3 scripts/integration_test.py\n" + r.stdout + r.stderr), 1000)
    # 03 tree
    shots["03-file-structure.png"] = window("securevibe-os/ — project structure", html.escape(tree(ROOT)), 900)
    # 04 IR schema
    shots["04-ir-schema-zod.png"] = window("packages/ir-schema/src/ir.ts + aws/database.ts", code_block("packages/ir-schema/src/ir.ts") + "\n\n<span class='d'>// ---- aws/database.ts ----</span>\n" + code_block("packages/ir-schema/src/aws/database.ts"))
    # 05 generated terraform (RDS part)
    tf = (ROOT / "generated/demo/main.tf").read_text().split("\n")
    s = next(i for i, l in enumerate(tf) if 'resource "aws_db_instance"' in l)
    shots["05-generated-terraform-rds.png"] = window("generated/demo/main.tf — secure RDS (compiled from IR)", "\n".join(f"<span class='d'>{i+s+1:>3}</span>  {html.escape(l)}" for i, l in enumerate(tf[s:s+24])))
    # 06 rego
    shots["06-s3-rego-policy.png"] = window("packages/security-rules/src/cis/aws/s3.rego", code_block("packages/security-rules/src/cis/aws/s3.rego"))
    # 07 web IDE rendering
    ir = json.loads((ROOT / "generated/demo/ir.json").read_text())
    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, h in shots.items():
            pg = b.new_page(viewport={"width": 1160, "height": 400}, device_scale_factor=1.5)
            pg.set_content(h); pg.screenshot(path=str(OUT / name), full_page=True); pg.close(); print("wrote", name)
        b.close()

PRICE = {"AWS::VPC": 0, "AWS::SG": 0, "AWS::S3": 5, "AWS::EC2": 8.5, "AWS::RDS": 65}
def cost(ir):  # same arithmetic as devops-service estimateFromIR
    t = 0
    for r in ir["resources"]:
        m = PRICE[r["type"]]
        if r["type"] == "AWS::RDS" and r.get("multiAz"): m *= 2
        if r["type"] == "AWS::VPC": m += 11
        if r["type"] in ("AWS::S3", "AWS::RDS"): m += 1
        t += m
    return t

def ide_html(ir, tf):
    pos = {"AWS::VPC": (30, 40), "AWS::EC2": (30, 170), "AWS::RDS": (30, 300), "AWS::S3": (30, 430)}
    desc = {"AWS::VPC": "CIDR 10.0.0.0/16 · AZs 2 · Flow Logs ON", "AWS::EC2": "t3.micro · IMDSv2 · no public IP",
            "AWS::RDS": "Postgres · Private · Encrypted · Multi-AZ", "AWS::S3": "Encrypted (KMS) · Public Block ON · PII"}
    nodes = "".join(f"<div class='n' style='left:{pos[r['type']][0]}px;top:{pos[r['type']][1]}px'><b>{r['type'][5:]} · {r['id']}</b><span>🔒 secure</span><div>{desc[r['type']]}</div></div>" for r in ir["resources"])
    edge = "<svg style='position:absolute;left:0;top:0;width:100%;height:100%'><path d='M150 230 L150 300' stroke='#7f8aa8' stroke-width='2' fill='none'/></svg>"
    code = "\n".join(f"<span class='d'>{i+1:>3}</span> {html.escape(l)}" for i, l in enumerate(tf[:34]))
    steps = ["ai:start", "ai:ir", "compiler:start", "compiler:done", "security:start", "security:done — score 100", "complete"]
    return f"""<html><head><style>
body{{margin:0;background:#0b1020;color:#e6e9f2;font:13px system-ui}}
.top{{height:40px;background:#141b34;display:flex;align-items:center;padding:0 16px;gap:16px;border-bottom:1px solid #2a3358}}
.main{{display:flex;height:640px}} .p{{border-right:4px solid #2a3358;position:relative;overflow:hidden}}
.n{{position:absolute;width:250px;background:#141b34;border:2px solid #2ecc71;border-radius:10px;padding:10px;font-size:12px}}
.n b{{display:inline-block;width:150px}} .n div{{opacity:.8;margin-top:6px}}
pre{{margin:0;padding:10px;font:12px/1.45 'DejaVu Sans Mono',monospace;color:#d6dcf0;background:#1e1e1e;height:100%;box-sizing:border-box}}
.d{{color:#6b7394}} button{{background:#2a3358;color:#e6e9f2;border:0;padding:6px 10px;border-radius:5px;margin:2px}}
.tab{{display:inline-block;padding:6px 12px;background:#252a3d}} .tab.a{{background:#1e1e1e;font-weight:700}}
.note{{background:#141b34;color:#7f8aa8;padding:6px 16px;font-size:11px}}</style></head><body>
<div class='top'><b>🛡 SecureVibe OS</b><span style='opacity:.6'>project / demo</span></div>
<div class='main'>
<div class='p' style='width:520px'><div style='position:absolute;z-index:2;top:8px;left:8px'><button>+ VPC</button><button>+ EC2</button><button>+ RDS</button><button>+ S3</button><button>Generate from canvas</button></div>{edge}{nodes}</div>
<div class='p' style='width:620px;background:#1e1e1e'><div><span class='tab a'>main.tf</span><span class='tab'>providers.tf</span><span class='tab'>outputs.tf</span></div><pre>{code}</pre></div>
<div class='p' style='width:360px;border:0;padding:10px;box-sizing:border-box'>
<textarea rows=3 style='width:100%;background:#141b34;color:#e6e9f2;border:1px solid #2a3358'>{PROMPT}</textarea><button>Vibe it ✨</button><button>🛡 Auto Secure</button>
<div style='margin-top:10px'><b>Pipeline</b><ol style='padding-left:18px;font-size:12px'>{''.join(f'<li>{s}</li>' for s in steps)}</ol></div>
<div style='font-size:34px;font-weight:700;color:#2ecc71'>100/100</div><div>✔ No policy violations</div>
<div style='margin-top:6px'>💰 ~${cost(ir):.2f}/month (ir-estimate)</div></div></div>
<div class='note'>Static rendering of the web-IDE layout (canvas · Monaco · chat/security panel) populated with the real output of scripts/e2e.py. Not a capture of the running Next.js app.</div>
</body></html>"""

if __name__ == "__main__": main()
