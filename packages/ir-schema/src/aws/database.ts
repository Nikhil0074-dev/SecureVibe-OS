import { z } from "zod";
import { BaseResourceSchema } from "../common";
export const RdsSchema = BaseResourceSchema.extend({
  type: z.literal("AWS::RDS"),
  engine: z.enum(["postgres", "mysql"]).default("postgres"),
  instanceClass: z.string().default("db.t3.medium"),
  private: z.literal(true),
  encrypted: z.literal(true),
  multiAz: z.boolean().default(false),
  subnetGroup: z.enum(["private"]).default("private"),
  deletionProtection: z.literal(true).default(true),
  vpc: z.string().optional(),
});
