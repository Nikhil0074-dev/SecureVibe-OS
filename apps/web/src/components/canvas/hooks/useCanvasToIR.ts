import type { Node, Edge } from "reactflow";

/** Convert the drawn React Flow graph into the platform IR. Secure defaults are applied server-side too. */
export function convertReactFlowToIR(nodes: Node[], edges: Edge[], compliance: string[] = ["CIS-1.5"]) {
  const vpc = nodes.find((n) => n.type === "AWS::VPC");
  const resources = nodes.map((n) => {
    const d: any = n.data ?? {};
    const id = d.id ?? n.id;
    const base = { id, type: n.type, tags: {}, dependencies: vpc && n.type !== "AWS::VPC" && n.type !== "AWS::S3" ? [vpc.data.id ?? vpc.id] : [] };
    switch (n.type) {
      case "AWS::VPC": return { ...base, cidr: d.cidr ?? "10.0.0.0/16", maxAzs: d.maxAzs ?? 2, enableFlowLogs: true, secure: true };
      case "AWS::S3": return { ...base, blockPublicAcls: true, encryption: "aws:kms", versioning: true, containsPii: !!d.containsPii, dataClassification: d.containsPii ? "PII" : "INTERNAL" };
      case "AWS::RDS": return { ...base, engine: "postgres", instanceClass: "db.t3.medium", private: true, encrypted: true, multiAz: !!d.multiAz, subnetGroup: "private", deletionProtection: true };
      case "AWS::EC2": return { ...base, instanceType: d.instanceType ?? "t3.micro", subnetGroup: "private", requireImdsV2: true, encryptedRoot: true, associatePublicIp: false };
      default: return base;
    }
  });
  const connections = edges.map((e) => ({ from: e.source, to: e.target, port: 5432, encrypted: true }));
  return { version: "v2.0", metadata: { compliance, env: "prod", region: compliance.includes("GDPR") ? "eu-west-1" : "us-east-1" }, resources, connections };
}
