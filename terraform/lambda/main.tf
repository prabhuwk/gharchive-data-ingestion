provider "aws" {
  region = "eu-west-1"
}

terraform {
  backend "s3" {
    bucket = "aaj-terraform-backend-s3"
    key    = "terraform-state/gharchive-data-ingestion/lambda.tfstate"
    region = "eu-west-1"
  }
}

resource "aws_lambda_function" "gharchive_lambda" {
  filename      = "gharchive_data_ingestion.zip"
  function_name = "gharchive-data-ingestion-lambda-terraform"
  role          = var.s3_iam_role_arn
  handler       = "lambda_function.lambda_handler"

  runtime = "python3.10"
  timeout = 90
  memory_size = 512

  environment {
    variables = {
      BASE_FILE_NAME="2023-07-16-0.json.gz"
      BUCKET_NAME="gharchive-data-ingestion-s3-bucket"
      PATH_PREFIX="gharchive"
      BOOKMARK_FILE="bookmark.txt"
    }
  }
}
