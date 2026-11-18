variable "name" {
  type = string
}

resource "aws_kms_key" "s3" {
  description         = "${var.name} artifacts"
  enable_key_rotation = true
}

resource "aws_s3_bucket" "this" {
  bucket_prefix = "${var.name}-artifacts-"
}

resource "aws_s3_bucket_public_access_block" "this" {
  bucket                  = aws_s3_bucket.this.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "this" {
  bucket = aws_s3_bucket.this.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "this" {
  bucket = aws_s3_bucket.this.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.arn
    }
  }
}

output "bucket" {
  value = aws_s3_bucket.this.bucket
}
