"""Knowledge graph of AWS service dependencies. In-memory by default; Neo4j when NEO4J_URI is set.
Cypher equivalent:  MATCH (r:Service {name:$t})-[:REQUIRES]->(d) RETURN d.name"""
import os

EDGES = {   # resource -> services it REQUIRES
    "rds": ["vpc"], "ec2": ["vpc"], "sg": ["vpc"], "s3": [], "vpc": [],
}
SECURE_DEFAULTS = {
    "rds": ["encrypted=true (KMS)", "publicly_accessible=false", "deletion_protection=true"],
    "s3": ["block_public_acls=true", "SSE-KMS", "versioning"],
    "vpc": ["flow logs", "private subnets", "default SG locked"],
    "ec2": ["IMDSv2 required", "encrypted root volume", "no public IP"],
    "sg": ["no 0.0.0.0/0 ingress"],
}

def get_dependencies(resource_type: str) -> list[str]:
    uri = os.environ.get("NEO4J_URI")
    if uri:
        try:
            from neo4j import GraphDatabase
            drv = GraphDatabase.driver(uri, auth=(os.environ.get("NEO4J_USER", "neo4j"), os.environ.get("NEO4J_PASSWORD", "")))
            with drv.session() as s:
                rows = s.run("MATCH (r:Service {name:$t})-[:REQUIRES]->(d) RETURN d.name AS n", t=resource_type)
                return [r["n"] for r in rows]
        except Exception:
            pass
    return EDGES.get(resource_type, [])

def secure_defaults(resource_type: str) -> list[str]:
    return SECURE_DEFAULTS.get(resource_type, [])
