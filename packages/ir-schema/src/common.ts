import { z } from "zod";
import { AWSTypeEnum } from "./enums";
export const TagSchema = z.record(z.string());
export const BaseResourceSchema = z.object({
  id: z.string().regex(/^[a-z][a-z0-9_]{1,62}$/, "id must be snake_case"),
  type: AWSTypeEnum,
  tags: TagSchema.default({}),
  dependencies: z.array(z.string()).default([]),
});
