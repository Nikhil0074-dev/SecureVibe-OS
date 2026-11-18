"use client";
import { BaseAWSNode } from "./BaseAWSNode";
export function S3Node({ data }: any) {
  return <BaseAWSNode title={`S3 · ${data.id}`} secure>Encrypted (KMS) · Public Block ON{data.containsPii ? <><br />PII</> : null}</BaseAWSNode>;
}
