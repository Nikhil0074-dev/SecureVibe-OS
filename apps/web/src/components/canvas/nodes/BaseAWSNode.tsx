"use client";
import { Handle, Position } from "reactflow";
import type { ReactNode } from "react";

export function BaseAWSNode({ title, secure, children }: { title: string; secure: boolean; children?: ReactNode }) {
  return (
    <div style={{ background: "#141b34", border: `2px solid ${secure ? "#2ecc71" : "#e74c3c"}`, borderRadius: 10, padding: 10, minWidth: 170, fontSize: 12 }}>
      <Handle type="target" position={Position.Left} />
      <div style={{ display: "flex", justifyContent: "space-between", fontWeight: 600 }}>
        <span>{title}</span><span>{secure ? "🔒 secure" : "⚠ insecure"}</span>
      </div>
      <div style={{ opacity: 0.8, marginTop: 6 }}>{children}</div>
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
