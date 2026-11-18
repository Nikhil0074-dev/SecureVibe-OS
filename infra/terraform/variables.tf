variable "region" {
  type    = string
  default = "eu-west-1"
}

variable "name" {
  type    = string
  default = "securevibe"
}

variable "vpc_cidr" {
  type    = string
  default = "10.20.0.0/16"
}
