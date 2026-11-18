import { Body, Controller, Get, Param, Post, Put } from "@nestjs/common";
import { ProjectsService } from "./projects.service";
@Controller("projects")
export class ProjectsController {
  constructor(private s: ProjectsService) {}
  @Post() create(@Body("name") name: string) { return this.s.create(name ?? "Untitled"); }
  @Get() list() { return this.s.list(); }
  @Get(":id") get(@Param("id") id: string) { return this.s.get(id); }
  @Put(":id/ir") save(@Param("id") id: string, @Body() b: any) { return this.s.saveIr(id, b.ir, b.securityReport); }
}
