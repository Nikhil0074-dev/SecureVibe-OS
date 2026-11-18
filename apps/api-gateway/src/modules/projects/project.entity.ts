import { Column, CreateDateColumn, Entity, PrimaryGeneratedColumn } from "typeorm";
@Entity("projects")
export class Project {
  @PrimaryGeneratedColumn("uuid") id: string;
  @Column() name: string;
  @Column({ type: "jsonb", nullable: true }) ir: Record<string, unknown> | null;   // IR stored as JSONB
  @Column({ type: "jsonb", nullable: true }) securityReport: Record<string, unknown> | null;
  @CreateDateColumn() createdAt: Date;
}
