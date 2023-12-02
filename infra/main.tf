provider "aws" {
  access_key                  = "mock_access_key"
  secret_key                  = "mock_secret_key"
  region                      = "us-east-1"
  s3_use_path_style           = true
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  endpoints {
    lambda         = "http://localhost:4566"
    s3             = "http://s3.localhost.localstack.cloud:4566"
  }
}

resource "aws_iam_role" "lambda_exec" {
  name = "lambda_execution_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        },
      },
    ],
  })
}

resource "aws_s3_bucket" "test-bucket" {
  bucket = "my-bucket"
}

resource "aws_s3_object" "lambda_zip" {
  bucket = aws_s3_bucket.test-bucket.bucket
  key    = "mylambda.zip"
  source = "../.serverless/metaboatrace-crawlers.zip"
}

resource "aws_lambda_function" "crawlRacerProfile" {
  function_name = "crawlRacerProfile"
  handler       = "metaboatrace.handlers.racer.crawl_racer_profile_handler"
  runtime       = "python3.11"
  s3_bucket     = aws_s3_bucket.test-bucket.bucket
  s3_key        = aws_s3_object.lambda_zip.key
  role          = aws_iam_role.lambda_exec.arn
}

resource "aws_lambda_function" "crawlMonthlySchedule" {
  function_name = "crawlMonthlySchedule"
  handler       = "metaboatrace.handlers.stadium.crawl_monthly_schedule_handler"
  runtime       = "python3.11"
  s3_bucket     = aws_s3_bucket.test-bucket.bucket
  s3_key        = aws_s3_object.lambda_zip.key
  role          = aws_iam_role.lambda_exec.arn
}

resource "aws_lambda_function" "crawlPreInspectionInformation" {
  function_name = "crawlPreInspectionInformation"
  handler       = "metaboatrace.handlers.stadium.crawl_pre_inspection_information_handler"
  runtime       = "python3.11"
  s3_bucket     = aws_s3_bucket.test-bucket.bucket
  s3_key        = aws_s3_object.lambda_zip.key
  role          = aws_iam_role.lambda_exec.arn
}

resource "aws_lambda_function" "crawlRaceInformation" {
  function_name = "crawlRaceInformation"
  handler       = "metaboatrace.handlers.race.crawl_race_information_handler"
  runtime       = "python3.11"
  s3_bucket     = aws_s3_bucket.test-bucket.bucket
  s3_key        = aws_s3_object.lambda_zip.key
  role          = aws_iam_role.lambda_exec.arn
}

resource "aws_lambda_function" "crawlRaceBeforeInformation" {
  function_name = "crawlRaceBeforeInformation"
  handler       = "metaboatrace.handlers.race.crawl_race_before_information_handler"
  runtime       = "python3.11"
  s3_bucket     = aws_s3_bucket.test-bucket.bucket
  s3_key        = aws_s3_object.lambda_zip.key
  role          = aws_iam_role.lambda_exec.arn
}

resource "aws_lambda_function" "crawlOdds" {
  function_name = "crawlOdds"
  handler       = "metaboatrace.handlers.race.crawl_odds_handler"
  runtime       = "python3.11"
  s3_bucket     = aws_s3_bucket.test-bucket.bucket
  s3_key        = aws_s3_object.lambda_zip.key
  role          = aws_iam_role.lambda_exec.arn
}

resource "aws_lambda_function" "crawlRaceResult" {
  function_name = "crawlRaceResult"
  handler       = "metaboatrace.handlers.race.crawl_race_result_handler"
  runtime       = "python3.11"
  s3_bucket     = aws_s3_bucket.test-bucket.bucket
  s3_key        = aws_s3_object.lambda_zip.key
  role          = aws_iam_role.lambda_exec.arn
}
