type Threat = { category: string; resource: string; threat: string; mitigation: string; mitigated: boolean };

export function strideModel(ir: any): Threat[] {
  const out: Threat[] = [];
  for (const r of ir.resources) {
    if (r.type === "AWS::S3") {
      out.push({ category: "Information Disclosure", resource: r.id, threat: "Public exposure of bucket data",
        mitigation: "Block Public Access + KMS encryption", mitigated: r.blockPublicAcls === true && r.encryption === "aws:kms" });
      out.push({ category: "Tampering", resource: r.id, threat: "Object overwritten or deleted",
        mitigation: "Versioning enabled", mitigated: r.versioning === true });
    }
    if (r.type === "AWS::RDS") {
      out.push({ category: "Information Disclosure", resource: r.id, threat: "Database reachable from the internet",
        mitigation: "Private subnets, publicly_accessible=false", mitigated: r.private === true });
      out.push({ category: "Information Disclosure", resource: r.id, threat: "Data at rest readable from snapshots",
        mitigation: "KMS storage encryption", mitigated: r.encrypted === true });
      out.push({ category: "Denial of Service", resource: r.id, threat: "Accidental deletion of database",
        mitigation: "Deletion protection + backups", mitigated: r.deletionProtection === true });
    }
    if (r.type === "AWS::VPC")
      out.push({ category: "Repudiation", resource: r.id, threat: "No record of network activity",
        mitigation: "VPC flow logs to encrypted CloudWatch", mitigated: r.enableFlowLogs === true });
    if (r.type === "AWS::EC2") {
      out.push({ category: "Spoofing", resource: r.id, threat: "SSRF steals instance credentials via IMDSv1",
        mitigation: "IMDSv2 required", mitigated: r.requireImdsV2 === true });
      out.push({ category: "Elevation of Privilege", resource: r.id, threat: "Direct internet exposure",
        mitigation: "No public IP, private subnet", mitigated: r.associatePublicIp === false });
    }
  }
  return out;
}
