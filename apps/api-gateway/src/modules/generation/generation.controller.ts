import { Body, Controller, Post, Res } from "@nestjs/common";
import type { Response } from "express";
import { z } from "zod";
import { GenerationService } from "./generation.service";

const Body_ = z.object({ prompt: z.string().min(3).max(4000).optional(), canvasIr: z.record(z.any()).optional() })
  .refine(b => b.prompt || b.canvasIr, "prompt or canvasIr required");

@Controller("generate")
export class GenerationController {
  constructor(private readonly svc: GenerationService) {}

  @Post("stream")                       // Server-Sent Events
  async stream(@Body() raw: unknown, @Res() res: Response) {
    const parsed = Body_.safeParse(raw);
    if (!parsed.success) { res.status(400).json(parsed.error.flatten()); return; }
    res.status(200).set({ "Content-Type": "text/event-stream", "Cache-Control": "no-cache", Connection: "keep-alive" });
    res.flushHeaders();
    try {
      for await (const ev of this.svc.generate(parsed.data)) res.write(`data: ${JSON.stringify(ev)}\n\n`);
    } catch (e: any) {
      res.write(`data: ${JSON.stringify({ stage: "error", data: { message: e.message } })}\n\n`);
    }
    res.end();
  }
}
