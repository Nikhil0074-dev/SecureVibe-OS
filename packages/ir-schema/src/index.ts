export * from "./enums";
export * from "./security";
export * from "./common";
export * from "./aws";
export * from "./ir";
import { zodToJsonSchema } from "zod-to-json-schema";
import { IRSchema } from "./ir";
/** JSON-Schema form used by the LLM function-calling tool `generate_ir_schema`. */
export const irJsonSchema = () => zodToJsonSchema(IRSchema as any, "IR");
