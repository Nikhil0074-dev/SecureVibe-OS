import express from "express";
import { estimate } from "./modules/cost/infracost.service";
import { strideModel } from "./modules/threat-model/stride.service";
import { pushToGithub } from "./modules/gitops/github.service";

const app = express();
app.use(express.json({ limit: "5mb" }));

app.get("/health", (_q, r) => r.json({ status: "ok", service: "devops" }));
app.post("/cost", async (q, r) => r.json(await estimate(q.body.ir, q.body.files)));
app.post("/threat-model", (q, r) => r.json({ threats: strideModel(q.body.ir) }));
app.post("/gitops/push", async (q, r) => {
  try { r.json(await pushToGithub(q.body.repo, q.body.files)); }
  catch (e: any) { r.status(400).json({ error: e.message }); }
});
app.listen(8005, () => console.log("devops-service on :8005"));
