import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { mkdtemp, writeFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, normalize } from "node:path";
const run = promisify(execFile);

// Fallback monthly price list (USD, eu-west-1, approximate) used when `infracost` is not installed.
const PRICE: Record<string, number> = {
  "AWS::VPC": 0, "AWS::SG": 0, "AWS::S3": 5, "AWS::EC2": 8.5, "AWS::RDS": 65,
};
const FLOW_LOGS = 10, KMS_KEY = 1;

export function estimateFromIR(ir: any) {
  const lines = ir.resources.map((r: any) => {
    let m = PRICE[r.type] ?? 0;
    if (r.type === "AWS::RDS" && r.multiAz) m *= 2;
    if (r.type === "AWS::VPC") m += FLOW_LOGS + KMS_KEY;
    if (r.type === "AWS::S3" || r.type === "AWS::RDS") m += KMS_KEY;
    return { id: r.id, type: r.type, monthlyUsd: +m.toFixed(2) };
  });
  return { source: "ir-estimate", monthlyUsd: +lines.reduce((s: number, l: any) => s + l.monthlyUsd, 0).toFixed(2), lines };
}

export async function estimate(ir: any, files?: Record<string, string>) {
  if (files && process.env.INFRACOST_API_KEY) {
    const dir = await mkdtemp(join(tmpdir(), "sv-cost-"));
    try {
      for (const [name, content] of Object.entries(files)) {
        if (normalize(name).startsWith("..")) throw new Error("unsafe path");
        await writeFile(join(dir, name), content);
      }
      const { stdout } = await run("infracost", ["breakdown", "--path", dir, "--format", "json"]);
      const j = JSON.parse(stdout);
      return { source: "infracost", monthlyUsd: parseFloat(j.totalMonthlyCost ?? "0") };
    } catch { /* fall through to estimate */ } finally { await rm(dir, { recursive: true, force: true }); }
  }
  return estimateFromIR(ir);
}
