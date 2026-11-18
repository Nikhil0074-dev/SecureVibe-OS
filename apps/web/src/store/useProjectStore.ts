import { create } from "zustand";
import type { Node, Edge } from "reactflow";

export interface SecurityReport { score: number; violations: string[]; passed?: boolean }
export interface Progress { stage: string; data?: any }
interface State {
  ir: any | null; nodes: Node[]; edges: Edge[]; code: Record<string, string>;
  securityReport: SecurityReport | null; cost: any | null; threats: any[]; progress: Progress[]; busy: boolean;
  activeFile: string;
  setIR: (ir: any) => void; setNodes: (n: Node[]) => void; setEdges: (e: Edge[]) => void;
  setCode: (c: Record<string, string>) => void; setReport: (r: SecurityReport | null) => void;
  pushProgress: (p: Progress) => void; reset: () => void; setBusy: (b: boolean) => void;
  setCost: (c: any) => void; setThreats: (t: any[]) => void; setActiveFile: (f: string) => void;
}
export const useProjectStore = create<State>((set) => ({
  ir: null, nodes: [], edges: [], code: {}, securityReport: null, cost: null, threats: [], progress: [], busy: false, activeFile: "main.tf",
  setIR: (ir) => set({ ir }), setNodes: (nodes) => set({ nodes }), setEdges: (edges) => set({ edges }),
  setCode: (code) => set({ code }), setReport: (securityReport) => set({ securityReport }),
  pushProgress: (p) => set((s) => ({ progress: [...s.progress, p] })), reset: () => set({ progress: [], securityReport: null }),
  setBusy: (busy) => set({ busy }), setCost: (cost) => set({ cost }), setThreats: (threats) => set({ threats }),
  setActiveFile: (activeFile) => set({ activeFile }),
}));
