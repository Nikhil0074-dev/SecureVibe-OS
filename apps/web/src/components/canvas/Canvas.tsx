"use client";
import { useCallback, useMemo } from "react";
import ReactFlow, { addEdge, applyEdgeChanges, applyNodeChanges, Background, Controls, type Connection } from "reactflow";
import "reactflow/dist/style.css";
import { useProjectStore } from "@/store/useProjectStore";
import { VPCNode } from "./nodes/VPCNode";
import { S3Node } from "./nodes/S3Node";
import { RDSNode } from "./nodes/RDSNode";
import { EC2Node } from "./nodes/EC2Node";
import { convertReactFlowToIR } from "./hooks/useCanvasToIR";
import { useGenerationStream } from "./hooks/useGenerationStream";

const PALETTE = [
  { type: "AWS::VPC", label: "+ VPC" }, { type: "AWS::EC2", label: "+ EC2" },
  { type: "AWS::RDS", label: "+ RDS" }, { type: "AWS::S3", label: "+ S3" },
];

export function Canvas() {
  const { nodes, edges, setNodes, setEdges, busy } = useProjectStore();
  const generate = useGenerationStream();
  const nodeTypes = useMemo(() => ({ "AWS::VPC": VPCNode, "AWS::S3": S3Node, "AWS::RDS": RDSNode, "AWS::EC2": EC2Node }), []);
  const onNodesChange = useCallback((c: any) => setNodes(applyNodeChanges(c, nodes)), [nodes, setNodes]);
  const onEdgesChange = useCallback((c: any) => setEdges(applyEdgeChanges(c, edges)), [edges, setEdges]);
  const onConnect = useCallback((c: Connection) => setEdges(addEdge(c, edges)), [edges, setEdges]);

  const add = (type: string) => {
    const n = nodes.filter((x) => x.type === type).length + 1;
    const id = `${type.split("::")[1].toLowerCase()}_${n}`;
    setNodes([...nodes, { id, type, position: { x: 60 + nodes.length * 40, y: 60 + nodes.length * 60 }, data: { id } }]);
  };
  return (
    <div style={{ height: "100%", position: "relative" }}>
      <div style={{ position: "absolute", zIndex: 5, top: 8, left: 8, display: "flex", gap: 6 }}>
        {PALETTE.map((p) => <button key={p.type} onClick={() => add(p.type)}>{p.label}</button>)}
        <button disabled={busy || nodes.length === 0} onClick={() => generate({ canvasIr: convertReactFlowToIR(nodes, edges) })}>Generate from canvas</button>
      </div>
      <ReactFlow nodes={nodes} edges={edges} nodeTypes={nodeTypes} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} onConnect={onConnect} fitView>
        <Background /><Controls />
      </ReactFlow>
    </div>
  );
}
