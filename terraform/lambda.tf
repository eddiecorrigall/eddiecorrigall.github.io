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

# Create Lambda Function

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
  name = "WebsiteLambdaRole"
  assume_role_policy = data.aws_iam_policy_document.lambda_exec_policy.json
}

resource "aws_iam_role_policy_attachment" "basic" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_exec_role.name
}

resource "null_resource" "lambda_requirements" {
  # https://docs.aws.amazon.com/lambda/latest/dg/python-package.html#python-package-dependencies
  triggers = {
    # requirements = filesha1("${path.module}/../chatbot/requirements.txt")
    always = "${timestamp()}"
  }
  provisioner "local-exec" {
    command = <<EOT
      cd ${path.module}/../chatbot/
      pip3 install -r ${path.module}/../chatbot/requirements.txt -t .
    EOT
  }
}

data "archive_file" "lambda_chatbot_artifact" {
  type        = "zip"
  source_dir  = "${path.module}/../chatbot"
  output_path = "${path.module}/artifacts/lambda_function_payload.zip"
  excludes    = [
    "venv"
  ]

  depends_on = [null_resource.lambda_requirements]
}

resource "aws_lambda_function" "lambda_chatbot" {
  function_name = "WebsiteChatbot"

  filename         = data.archive_file.lambda_chatbot_artifact.output_path
  source_code_hash = data.archive_file.lambda_chatbot_artifact.output_base64sha256

  handler       = "lambda.lambda_handler"
  runtime       = "python3.11"

  role = aws_iam_role.lambda_exec_role.arn

  environment {
    variables = {
      foo = "bar"
    }
  }
}

# Create public URL

resource "aws_lambda_function_url" "lambda_chatbot_url" {
  function_name      = aws_lambda_function.lambda_chatbot.function_name
  authorization_type = "NONE"
}
