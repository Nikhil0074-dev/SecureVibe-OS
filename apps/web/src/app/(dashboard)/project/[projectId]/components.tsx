"use client";
import { useState } from "react";
import { useProjectStore } from "@/store/useProjectStore";
import { useGenerationStream } from "@/components/canvas/hooks/useGenerationStream";

export function GenerationProgress() {
  const { progress, busy } = useProjectStore();
  return (
    <div style={{ fontSize: 12, padding: 8 }}>
      <b>Pipeline {busy ? "⏳" : ""}</b>
      <ol style={{ paddingLeft: 18 }}>{progress.map((p, i) => <li key={i}>{p.stage}{p.data?.score !== undefined ? ` — score ${p.data.score}` : ""}</li>)}</ol>
    </div>
  );
}

export function SecurityPanel() {
  const { securityReport: r, cost, threats } = useProjectStore();
  if (!r) return null;
  return (
    <div style={{ padding: 8, fontSize: 12 }}>
      <div style={{ fontSize: 28, fontWeight: 700, color: r.score >= 90 ? "#2ecc71" : "#e67e22" }}>{r.score}/100</div>
      {r.violations.length === 0 ? <div>✔ No policy violations</div> : <ul>{r.violations.map((v) => <li key={v}>{v}</li>)}</ul>}
      {cost && <div>💰 ~${cost.monthlyUsd}/month ({cost.source})</div>}
      <details><summary>STRIDE threat model ({threats.length})</summary>
        <ul>{threats.map((t, i) => <li key={i}>{t.mitigated ? "✅" : "❌"} {t.category}: {t.threat}</li>)}</ul></details>
    </div>
  );
}

export function VibeChat() {
  const [text, setText] = useState("Create 3-tier app with private RDS, GDPR compliant");
  const { busy } = useProjectStore();
  const generate = useGenerationStream();
  return (
    <div style={{ padding: 8 }}>
      <textarea value={text} onChange={(e) => setText(e.target.value)} rows={4} style={{ width: "100%" }} />
      <button disabled={busy} onClick={() => generate({ prompt: text })}>Vibe it ✨</button>
    </div>
  );
}
