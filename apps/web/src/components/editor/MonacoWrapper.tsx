"use client";
import "./monacoSetup";
import Editor, { type OnMount } from "@monaco-editor/react";
import { useRef } from "react";
import { useProjectStore } from "@/store/useProjectStore";
import { applySecurityMarkers } from "./SecurityLens";

export function MonacoWrapper() {
  const { code, activeFile, setActiveFile, securityReport } = useProjectStore();
  const mon = useRef<{ editor: any; monaco: any } | null>(null);
  const onMount: OnMount = (editor, monaco) => {
    mon.current = { editor, monaco };
    monaco.languages.register({ id: "hcl" });
    monaco.languages.setMonarchTokensProvider("hcl", {
      tokenizer: { root: [[/#.*$/, "comment"], [/\b(resource|data|variable|output|provider|terraform)\b/, "keyword"], [/"[^"]*"/, "string"], [/\b(true|false)\b/, "constant"]] },
    });
    applySecurityMarkers(monaco, editor.getModel(), securityReport?.violations ?? [], code[activeFile] ?? "");
  };
  const files = Object.keys(code);
  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <div style={{ display: "flex", gap: 4, padding: 4 }}>{files.map((f) => <button key={f} onClick={() => setActiveFile(f)} style={{ fontWeight: f === activeFile ? 700 : 400 }}>{f}</button>)}</div>
      <Editor height="100%" theme="vs-dark" language="hcl" path={activeFile} value={code[activeFile] ?? "# Generate infrastructure to see code here"} onMount={onMount} options={{ readOnly: false, minimap: { enabled: false } }} />
    </div>
  );
}
