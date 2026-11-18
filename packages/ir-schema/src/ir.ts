import { z } from "zod";
import { VpcSchema, SgSchema, Ec2Schema, S3Schema, RdsSchema } from "./aws";
import { ComplianceEnum } from "./security";

export const ResourceSchema = z.discriminatedUnion("type", [VpcSchema, SgSchema, Ec2Schema, S3Schema, RdsSchema]);
export const ConnectionSchema = z.object({
  from: z.string(), to: z.string(),
  port: z.number().int().min(1).max(65535).optional(),
  encrypted: z.literal(true).default(true),
});
export const IRSchema = z.object({
  version: z.literal("v2.0"),
  metadata: z.object({
    compliance: z.array(ComplianceEnum).default(["CIS-1.5"]),
    env: z.enum(["dev", "staging", "prod"]).default("prod"),
    region: z.string().default("eu-west-1"),
  }),
  resources: z.array(ResourceSchema).min(1),
  connections: z.array(ConnectionSchema).default([]),
}).superRefine((ir, ctx) => {
  const ids = new Set(ir.resources.map(r => r.id));
  if (ids.size !== ir.resources.length) ctx.addIssue({ code: "custom", message: "duplicate resource ids" });
  for (const r of ir.resources) for (const d of r.dependencies)
    if (!ids.has(d)) ctx.addIssue({ code: "custom", message: `${r.id} depends on unknown ${d}` });
  for (const c of ir.connections)
    if (!ids.has(c.from) || !ids.has(c.to)) ctx.addIssue({ code: "custom", message: `bad connection ${c.from}->${c.to}` });
});
export type IR = z.infer<typeof IRSchema>;
export type Resource = z.infer<typeof ResourceSchema>;
