provider "aws" {
  region = var.region
}

module "networking" {
  source = "./modules/networking"
  name   = var.name
  cidr   = var.vpc_cidr
}

module "eks" {
  source     = "./modules/eks"
  name       = var.name
  vpc_id     = module.networking.vpc_id
  subnet_ids = module.networking.private_subnet_ids
}

module "rds" {
  source     = "./modules/rds"
  name       = var.name
  vpc_id     = module.networking.vpc_id
  subnet_ids = module.networking.private_subnet_ids
}

module "s3_artifacts" {
  source = "./modules/s3-artifacts"
  name   = var.name
}
