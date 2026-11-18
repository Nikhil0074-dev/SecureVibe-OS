import { Injectable, NotFoundException } from "@nestjs/common";
import { InjectRepository } from "@nestjs/typeorm";
import { Repository } from "typeorm";
import { Project } from "./project.entity";

@Injectable()
export class ProjectsService {
  constructor(@InjectRepository(Project) private repo: Repository<Project>) {}
  create(name: string) { return this.repo.save(this.repo.create({ name, ir: null, securityReport: null })); }
  list() { return this.repo.find({ order: { createdAt: "DESC" } }); }
  async get(id: string) { const p = await this.repo.findOneBy({ id }); if (!p) throw new NotFoundException(); return p; }
  async saveIr(id: string, ir: Record<string, unknown>, securityReport?: Record<string, unknown>) {
    const p = await this.get(id); p.ir = ir; if (securityReport) p.securityReport = securityReport; return this.repo.save(p);
  }
}
