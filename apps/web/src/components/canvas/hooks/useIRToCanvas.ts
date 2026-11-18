import type { Node, Edge } from "reactflow";

const COLUMN: Record<string, number> = { "AWS::VPC": 0, "AWS::EC2": 1, "AWS::RDS": 2, "AWS::S3": 2, "AWS::SG": 1 };

/** Inverse of convertReactFlowToIR: render any IR (from a prompt or an imported repo) onto the canvas. */
export function convertIRToReactFlow(ir: any): { nodes: Node[]; edges: Edge[] } {
  const rowInCol: Record<number, number> = {};
  const nodes: Node[] = (ir?.resources ?? []).map((r: any) => {
    const col = COLUMN[r.type] ?? 1;
    const row = (rowInCol[col] = (rowInCol[col] ?? -1) + 1);
    return { id: r.id, type: r.type, position: { x: 30 + col * 260, y: 70 + row * 130 }, data: { ...r } };
  });
  const edges: Edge[] = (ir?.connections ?? []).map((c: any, i: number) => ({ id: `e${i}`, source: c.from, target: c.to, label: c.port ? `:${c.port}` : undefined }));
  return { nodes, edges };
}
