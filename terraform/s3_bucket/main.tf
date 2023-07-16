provider "aws" {
  region = "eu-west-1"
}

terraform {
  backend "s3" {
    bucket = "aaj-terraform-backend-s3"
    key    = "terraform-state/gharchive-data-ingestion/s3_bucket.tfstate"
    region = "eu-west-1"
  }
}

resource "aws_s3_bucket" "gharchive" {
  bucket = "gharchive-data-ingestion-s3-bucket"
}
