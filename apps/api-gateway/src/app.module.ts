import { Module } from "@nestjs/common";
import { ThrottlerModule, ThrottlerGuard } from "@nestjs/throttler";
import { APP_GUARD } from "@nestjs/core";
import { TypeOrmModule } from "@nestjs/typeorm";
import { GenerationModule } from "./modules/generation/generation.module";
import { ProjectsModule } from "./modules/projects/projects.module";
import { Project } from "./modules/projects/project.entity";

@Module({
  imports: [
    ThrottlerModule.forRoot([{ ttl: 60_000, limit: 30 }]),          // rate limit: 30 req/min/IP
    TypeOrmModule.forRoot({ type: "postgres", url: process.env.DATABASE_URL, entities: [Project], synchronize: process.env.NODE_ENV !== "production" }),
    GenerationModule, ProjectsModule,
  ],
  providers: [{ provide: APP_GUARD, useClass: ThrottlerGuard }],
})
export class AppModule {}
