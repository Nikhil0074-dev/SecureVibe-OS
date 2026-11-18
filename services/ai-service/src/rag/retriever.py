"""Hybrid retrieval: vector (Pinecone, optional) + graph. Returns a context bundle for the LLM."""
from .graph_store import get_dependencies, secure_defaults

DOC_SNIPPETS = {   # tiny offline corpus; production uses Pinecone with ~100k AWS-doc chunks
    "rds": "AWS Well-Architected SEC08: encrypt data at rest; place databases in private subnets.",
    "s3": "CIS 2.1.x: enable Block Public Access, default encryption and versioning.",
    "vpc": "CIS 3.9: enable VPC flow logs for all VPCs.",
    "ec2": "CIS 5.6: require IMDSv2 on all instances.",
}

def hybrid_search(resources: list[str]) -> dict:
    docs, deps, defaults = [], set(), {}
    for r in resources:
        if r in DOC_SNIPPETS: docs.append(DOC_SNIPPETS[r])
        deps.update(get_dependencies(r))
        defaults[r] = secure_defaults(r)
    return {"docs": docs, "required_dependencies": sorted(deps), "secure_defaults": defaults}

def as_prompt_context(bundle: dict) -> str:
    return "\n".join(bundle["docs"]) + f"\nRequired deps: {bundle['required_dependencies']}"
