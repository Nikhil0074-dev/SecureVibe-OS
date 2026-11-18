import { z } from "zod";
export const AWSTypeEnum = z.enum(["AWS::VPC", "AWS::SG", "AWS::EC2", "AWS::S3", "AWS::RDS"]);
export type AWSType = z.infer<typeof AWSTypeEnum>;
