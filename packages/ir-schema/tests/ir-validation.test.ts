import { describe, it, expect } from "vitest";
import { IRSchema } from "../src";
const base = { version: "v2.0", metadata: { compliance: ["GDPR"], env: "prod" } };
describe("IR security invariants", () => {
  it("accepts a secure IR and applies secure defaults", () => {
    const r = IRSchema.parse({ ...base, resources: [{ id: "vpc_main", type: "AWS::VPC" }, { id: "s3_app", type: "AWS::S3" }] });
    expect((r.resources[0] as any).enableFlowLogs).toBe(true);
    expect((r.resources[1] as any).blockPublicAcls).toBe(true);
  });
  it("rejects an unencrypted RDS", () => {
    expect(IRSchema.safeParse({ ...base, resources: [{ id: "db", type: "AWS::RDS", private: true, encrypted: false }] }).success).toBe(false);
  });
  it("rejects a public RDS", () => {
    expect(IRSchema.safeParse({ ...base, resources: [{ id: "db", type: "AWS::RDS", private: false, encrypted: true }] }).success).toBe(false);
  });
  it("rejects 0.0.0.0/0 ingress", () => {
    expect(IRSchema.safeParse({ ...base, resources: [{ id: "sg", type: "AWS::SG", vpc: "v", ingress: [{ port: 22, cidr: "0.0.0.0/0" }] }] }).success).toBe(false);
  });
  it("rejects dangling dependency", () => {
    expect(IRSchema.safeParse({ ...base, resources: [{ id: "db", type: "AWS::RDS", private: true, encrypted: true, dependencies: ["ghost"] }] }).success).toBe(false);
  });
});
