terraform {
  backend "s3" {
    bucket         = "securevibe-tfstate" # create once, out-of-band
    key            = "platform/terraform.tfstate"
    region         = "eu-west-1"
    dynamodb_table = "securevibe-tflock"
    encrypt        = true
  }
}
