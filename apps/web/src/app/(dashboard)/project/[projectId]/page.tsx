"use client";
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";
import { Canvas } from "@/components/canvas/Canvas";
import dynamic from "next/dynamic";
import { QuickFixButton } from "@/components/editor/QuickFixButton";
const MonacoWrapper = dynamic(() => import("@/components/editor/MonacoWrapper").then((m) => m.MonacoWrapper), { ssr: false });
import { GenerationProgress, SecurityPanel, VibeChat } from "./components";

export default function ProjectPage() {
  const handle = <PanelResizeHandle style={{ width: 4, background: "#2a3358" }} />;
  return (
    <div style={{ height: "100vh" }}>
      <PanelGroup direction="horizontal">
        <Panel defaultSize={35}><Canvas /></Panel>{handle}
        <Panel defaultSize={40}><MonacoWrapper /></Panel>{handle}
        <Panel defaultSize={25}><VibeChat /><QuickFixButton /><GenerationProgress /><SecurityPanel /></Panel>
      </PanelGroup>
    </div>
  );
}
