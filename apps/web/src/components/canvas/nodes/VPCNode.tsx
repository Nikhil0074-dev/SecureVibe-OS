"use client";
import { BaseAWSNode } from "./BaseAWSNode";
export function VPCNode({ data }: any) {
  return <BaseAWSNode title={`VPC · ${data.id}`} secure>CIDR {data.cidr ?? "10.0.0.0/16"}<br />AZs {data.maxAzs ?? 2} · Flow Logs ON</BaseAWSNode>;
}
