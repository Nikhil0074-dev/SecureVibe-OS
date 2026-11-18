"use client";
import { BaseAWSNode } from "./BaseAWSNode";
export function RDSNode({ data }: any) {
  return <BaseAWSNode title={`RDS · ${data.id}`} secure>Postgres · Private · Encrypted{data.multiAz ? " · Multi-AZ" : ""}</BaseAWSNode>;
}
