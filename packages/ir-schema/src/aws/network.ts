import { z } from "zod";
import { BaseResourceSchema } from "../common";
export const VpcSchema = BaseResourceSchema.extend({
  type: z.literal("AWS::VPC"),
  cidr: z.string().regex(/^\d{1,3}(\.\d{1,3}){3}\/\d{1,2}$/).default("10.0.0.0/16"),
  maxAzs: z.number().int().min(1).max(6).default(2),
  enableFlowLogs: z.literal(true).default(true), // CIS 3.9 - cannot be disabled
  secure: z.literal(true).default(true),
});
export const SgSchema = BaseResourceSchema.extend({
  type: z.literal("AWS::SG"),
  vpc: z.string(),
  ingress: z.array(z.object({
    port: z.number().int().min(1).max(65535),
    cidr: z.string().refine(c => c !== "0.0.0.0/0", "open-to-world ingress is forbidden"),
  })).default([]),
});
