output "vpc_main_id" { value = aws_vpc.vpc_main.id }
output "vpc_main_private_subnet_ids" { value = aws_subnet.vpc_main_private[*].id }

output "s3_app_bucket" { value = aws_s3_bucket.s3_app.bucket }
