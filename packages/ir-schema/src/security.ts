import { z } from "zod";
export const ComplianceEnum = z.enum(["CIS-1.5", "GDPR", "HIPAA", "PCI-DSS", "SOC2"]);
export type Compliance = z.infer<typeof ComplianceEnum>;
export const DataClassification = z.enum(["PUBLIC", "INTERNAL", "PII", "PHI", "PCI"]);
export const SecurityRequirementSchema = z.object({
  compliance: z.array(ComplianceEnum).default(["CIS-1.5"]),
  allowedRegions: z.array(z.string()).default(["eu-west-1", "eu-central-1", "us-east-1"]),
});
