variable "aws_region" {
  type = string
}

provider "aws" {
  region = "${var.aws_region}"
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.26.0"
    }
  }

  backend "s3" {
    bucket = "terraform-state-eddiecorrigall"
    key    = "eddiecorrigall.github.io.tfstate"
    region = "us-west-2"
  }

  required_version = ">= 1.2.0"
}

locals {
  tags = {
    Repo   = "https://github.com/eddiecorrigall/eddiecorrigall.github.io"
  }
}

data "aws_iam_policy_document" "lambda_exec_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda_chatbot_role"
  assume_role_policy = data.aws_iam_policy_document.lambda_exec_policy.json
}

data "archive_file" "lambda" {
  type        = "zip"
  source_dir  = "${path.module}/../chatbot"
  output_path = "${path.module}/artifacts/lambda_function_payload.zip"
  excludes    = [
    "venv"
  ]
}

resource "aws_lambda_function" "lambda_chatbot" {
  function_name = "ChatBotFunction"
  filename      = "${path.module}/artifact/lambda_function_payload.zip"

  handler       = "lambda.handler"
  runtime       = "python3.6"

  role = aws_iam_role.lambda_exec_role.arn

  environment {
    variables = {
      foo = "bar"
    }
  }
}
