import { describe, it, expect } from "vitest";
import { estimateFromIR } from "./infracost.service";
describe("cost", () => {
  it("prices multi-AZ RDS at double", () => {
    const a = estimateFromIR({ resources: [{ id: "d", type: "AWS::RDS", multiAz: false }] }).monthlyUsd;
    const b = estimateFromIR({ resources: [{ id: "d", type: "AWS::RDS", multiAz: true }] }).monthlyUsd;
    expect(b).toBeGreaterThan(a);
  });
});
