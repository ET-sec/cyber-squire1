provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      project = "cd-security-plane"
      env     = "prd"
      managed = "terraform"
    }
  }
}
