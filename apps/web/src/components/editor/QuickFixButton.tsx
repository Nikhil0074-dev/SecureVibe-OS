"use client";
import { useProjectStore } from "@/store/useProjectStore";
import { useGenerationStream } from "../canvas/hooks/useGenerationStream";

/** "Auto Secure": re-runs the pipeline on the current IR; the gateway's fixer loop patches violations. */
export function QuickFixButton() {
  const { ir, busy } = useProjectStore();
  const generate = useGenerationStream();
  return <button disabled={!ir || busy} onClick={() => generate({ canvasIr: ir })}>🛡 Auto Secure</button>;
}
