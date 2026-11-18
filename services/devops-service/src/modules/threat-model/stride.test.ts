import { describe, it, expect } from "vitest";
import { strideModel } from "./stride.service";

describe("STRIDE threat model", () => {
  it("marks secure resources as mitigated", () => {
    const t = strideModel({ resources: [
      { id: "b", type: "AWS::S3", blockPublicAcls: true, encryption: "aws:kms", versioning: true },
      { id: "d", type: "AWS::RDS", private: true, encrypted: true, deletionProtection: true },
      { id: "v", type: "AWS::VPC", enableFlowLogs: true },
      { id: "e", type: "AWS::EC2", requireImdsV2: true, associatePublicIp: false },
    ] });
    expect(t.length).toBe(8);
    expect(t.every((x) => x.mitigated)).toBe(true);
  });
  it("flags insecure resources as unmitigated", () => {
    const t = strideModel({ resources: [{ id: "d", type: "AWS::RDS", private: false, encrypted: false, deletionProtection: false }] });
    expect(t.filter((x) => !x.mitigated).length).toBe(3);
  });
  it("covers the STRIDE categories used", () => {
    const cats = new Set(strideModel({ resources: [
      { id: "b", type: "AWS::S3" }, { id: "d", type: "AWS::RDS" }, { id: "v", type: "AWS::VPC" }, { id: "e", type: "AWS::EC2" } ] }).map((x) => x.category));
    expect(cats).toEqual(new Set(["Information Disclosure", "Tampering", "Denial of Service", "Repudiation", "Spoofing", "Elevation of Privilege"]));
  });
});
