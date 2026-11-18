import { z } from "zod";
import { BaseResourceSchema } from "../common";
import { DataClassification } from "../security";
export const S3Schema = BaseResourceSchema.extend({
  type: z.literal("AWS::S3"),
  blockPublicAcls: z.literal(true).default(true),
  encryption: z.enum(["aws:kms"]).default("aws:kms"),
  versioning: z.literal(true).default(true),
  containsPii: z.boolean().default(false),
  dataClassification: DataClassification.default("INTERNAL"),
});
