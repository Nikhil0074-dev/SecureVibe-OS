import { Injectable } from "@nestjs/common";

const URL = {
  ai: process.env.AI_SERVICE_URL ?? "http://localhost:8001",
  compiler: process.env.COMPILER_SERVICE_URL ?? "http://localhost:8002",
  security: process.env.SECURITY_SERVICE_URL ?? "http://localhost:8003",
  devops: process.env.DEVOPS_SERVICE_URL ?? "http://localhost:8005",
};
const post = async (url: string, body: unknown) => {
  const r = await fetch(url, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
  if (!r.ok) throw new Error(`${url} -> ${r.status} ${await r.text()}`);
  return r.json();
};

export interface GenEvent { stage: string; data?: unknown }
const MAX_FIX_LOOPS = 3, SCORE_GATE = 90;

@Injectable()
export class GenerationService {
  /** Prompt|CanvasIR -> IR -> HCL -> scan -> (fix loop while score<90) -> cost + threat model. Yields progress events for SSE. */
  async *generate(input: { prompt?: string; canvasIr?: unknown }): AsyncGenerator<GenEvent> {
    yield { stage: "ai:start" };
    let { ir } = await post(`${URL.ai}/generate-ir`, { prompt: input.prompt, canvas_ir: input.canvasIr });
    yield { stage: "ai:ir", data: ir };

    let files: Record<string, string> = {}, scan: any = null;
    for (let attempt = 0; attempt <= MAX_FIX_LOOPS; attempt++) {
      yield { stage: "compiler:start", data: { attempt } };
      files = (await post(`${URL.compiler}/compile`, { ir, target: "terraform" })).files;
      yield { stage: "compiler:done", data: { files: Object.keys(files) } };

      yield { stage: "security:start" };
      scan = await post(`${URL.security}/scan`, { ir, files });
      yield { stage: "security:done", data: { score: scan.score, violations: scan.violations } };
      if (scan.score >= SCORE_GATE) break;

      yield { stage: "fixer:start" };
      const fixed = await post(`${URL.ai}/fix-ir`, { ir, violations: scan.violations });
      ir = fixed.ir;
      yield { stage: "fixer:done", data: { fixes: fixed.fixes } };
    }
    const [cost, threat] = await Promise.all([
      post(`${URL.devops}/cost`, { ir }), post(`${URL.devops}/threat-model`, { ir }),
    ]);
    yield { stage: "complete", data: { ir, files, securityReport: scan, cost, threatModel: threat.threats } };
  }
}
