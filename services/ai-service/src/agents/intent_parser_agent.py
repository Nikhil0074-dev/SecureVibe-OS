"""Agent 1 - natural language -> Intent. Uses Claude when ANTHROPIC_API_KEY is set,
otherwise a deterministic rule-based parser (so the platform works offline / in CI)."""
import json, os, re
from pathlib import Path
from ..schemas import Intent

SYSTEM = (Path(__file__).parents[1] / "prompts" / "system_v2.txt").read_text()

KEYWORDS = {
    "rds": r"\b(rds|database|postgres|mysql|db)\b",
    "s3": r"\b(s3|bucket|storage|assets|uploads|files)\b",
    "ec2": r"\b(ec2|server|vm|instance|app tier|3-?tier|web app|backend)\b",
}
COMPLIANCE = {"GDPR": r"gdpr", "HIPAA": r"hipaa", "PCI-DSS": r"pci", "SOC2": r"soc ?2"}

def rule_based_parse(prompt: str) -> Intent:
    p = prompt.lower()
    resources = ["vpc"]
    for res, rx in KEYWORDS.items():
        if re.search(rx, p):
            resources.append(res)
    if re.search(r"3-?tier|three.?tier", p):
        resources = list(dict.fromkeys(resources + ["ec2", "rds", "s3"]))
    if len(resources) == 1:                      # nothing recognised -> sensible default
        resources += ["s3"]
    compliance = ["CIS-1.5"] + [c for c, rx in COMPLIANCE.items() if re.search(rx, p)]
    pii = bool(re.search(r"pii|personal|customer data|gdpr|hipaa|user data", p))
    env = "dev" if re.search(r"\b(dev|test|sandbox)\b", p) else "prod"
    region = "eu-west-1" if "GDPR" in compliance else "us-east-1"
    m = re.search(r"\b(us|eu|ap|sa|ca)-[a-z]+-\d\b", p)
    if m: region = m.group(0)
    app = "3-tier" if "3-tier" in p or "3 tier" in p else "generic"
    return Intent(app_type=app, resources=resources, compliance=compliance, env=env, region=region, pii=pii)

def parse_intent(prompt: str, context: str = "") -> Intent:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return rule_based_parse(prompt)
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=key)
        msg = client.messages.create(
            model=os.environ.get("LLM_MODEL", "claude-sonnet-4-5"), max_tokens=800,
            system=SYSTEM + ("\n\nRetrieved context:\n" + context if context else ""),
            messages=[{"role": "user", "content": prompt}])
        raw = re.sub(r"^```(?:json)?|```$", "", msg.content[0].text.strip(), flags=re.M).strip()
        return Intent(**json.loads(raw))
    except Exception:
        return rule_based_parse(prompt)            # graceful degradation
