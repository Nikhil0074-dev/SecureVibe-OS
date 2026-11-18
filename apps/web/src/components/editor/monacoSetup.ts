"use client";
// Bundle Monaco locally (no CDN): works offline, passes strict CSP, and no third-party script runs in a security product.
import * as monaco from "monaco-editor";
import { loader } from "@monaco-editor/react";

(self as any).MonacoEnvironment = {
  getWorker: () => new Worker(new URL("monaco-editor/esm/vs/editor/editor.worker.js", import.meta.url)),
};
loader.config({ monaco });
export default monaco;
