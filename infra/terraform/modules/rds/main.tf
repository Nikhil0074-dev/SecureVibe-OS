variable "name" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}

resource "aws_kms_key" "db" {
  description         = "${var.name} rds"
  enable_key_rotation = true
}

resource "aws_db_subnet_group" "this" {
  name       = var.name
  subnet_ids = var.subnet_ids
}

resource "aws_db_instance" "this" {
  identifier                          = var.name
  engine                              = "postgres"
  engine_version                      = "15"
  instance_class                      = "db.t3.medium"
  allocated_storage                   = 50
  db_name                             = "securevibe"
  username                            = "svadmin"
  manage_master_user_password         = true
  storage_encrypted                   = true
  kms_key_id                          = aws_kms_key.db.arn
  multi_az                            = true
  publicly_accessible                 = false
  deletion_protection                 = true
  backup_retention_period             = 14
  db_subnet_group_name                = aws_db_subnet_group.this.name
  iam_database_authentication_enabled = true
  enabled_cloudwatch_logs_exports     = ["postgresql"]
  final_snapshot_identifier           = "${var.name}-final"
}
