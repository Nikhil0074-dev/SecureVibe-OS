"use client";
import { useProjectStore } from "@/store/useProjectStore";
import { convertIRToReactFlow } from "./useIRToCanvas";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:4000";

/** Streams generation progress from the gateway over SSE (POST + ReadableStream; EventSource can't POST). */
export function useGenerationStream() {
  const s = useProjectStore();
  return async (body: { prompt?: string; canvasIr?: unknown }) => {
    s.reset(); s.setBusy(true);
    try {
      const res = await fetch(`${API}/generate/stream`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
      if (!res.body) throw new Error("no stream");
      const reader = res.body.getReader(); const dec = new TextDecoder(); let buf = "";
      for (;;) {
        const { done, value } = await reader.read(); if (done) break;
        buf += dec.decode(value, { stream: true });
        const parts = buf.split("\n\n"); buf = parts.pop() ?? "";
        for (const p of parts) {
          if (!p.startsWith("data: ")) continue;
          const ev = JSON.parse(p.slice(6)); s.pushProgress(ev);
          if (ev.stage === "ai:ir") s.setIR(ev.data);
          if (ev.stage === "complete") {
            const g = convertIRToReactFlow(ev.data.ir); s.setNodes(g.nodes); s.setEdges(g.edges);
            s.setIR(ev.data.ir); s.setCode(ev.data.files); s.setReport(ev.data.securityReport);
            s.setCost(ev.data.cost); s.setThreats(ev.data.threatModel);
          }
        }
      }
    } finally { s.setBusy(false); }
  };
}
