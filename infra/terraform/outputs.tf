output "cluster_name" {
  value = module.eks.cluster_name
}

output "artifact_bucket" {
  value = module.s3_artifacts.bucket
}
