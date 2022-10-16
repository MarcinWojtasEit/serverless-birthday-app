variable "aws_region" {
  default = "eu-central-1"
}

variable "aws_profile_name" {
  description = "Name of your local AWS profile that will be used to run this module"
  default = "mwojtas-test-user"
}

variable "aws_env" {
  description = "AWS Environment where code is being executed (AWS_SAM_LOCAL or AWS)"
  default = "AWS"
}