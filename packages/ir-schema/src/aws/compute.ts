import { z } from "zod";
import { BaseResourceSchema } from "../common";
export const Ec2Schema = BaseResourceSchema.extend({
  type: z.literal("AWS::EC2"),
  instanceType: z.string().default("t3.micro"),
  subnetGroup: z.enum(["private"]).default("private"),
  requireImdsV2: z.literal(true).default(true),
  encryptedRoot: z.literal(true).default(true),
  associatePublicIp: z.literal(false).default(false),
  vpc: z.string().optional(),
});
