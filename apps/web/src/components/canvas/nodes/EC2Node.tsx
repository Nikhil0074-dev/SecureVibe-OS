"use client";
import { BaseAWSNode } from "./BaseAWSNode";
export function EC2Node({ data }: any) {
  return <BaseAWSNode title={`EC2 · ${data.id}`} secure>{data.instanceType ?? "t3.micro"} · IMDSv2 · no public IP</BaseAWSNode>;
}
