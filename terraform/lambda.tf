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

########
# Lambda
########

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

resource "aws_lambda_function" "chatbot" {
  function_name = "WebsiteChatbot"

  filename         = data.archive_file.lambda_chatbot_artifact.output_path
  source_code_hash = data.archive_file.lambda_chatbot_artifact.output_base64sha256

  handler       = "lambda.lambda_handler"
  runtime       = "python3.11"

  role = aws_iam_role.lambda_exec_role.arn

  environment {
    variables = {
      foo = "bar"
      URL_PREFIX = "/live/chatbot"
    }
  }

  depends_on = [aws_dynamodb_table.chatbot_messages_table]
}

################
# API Gateway V2
################

resource "aws_apigatewayv2_api" "chatbot" {
  # https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/apigatewayv2_api

  name          = "chatpot_api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_headers = ["content-type"]
    allow_methods = ["GET", "POST", "OPTIONS"]
    allow_origins = ["*"]
    max_age = 300
  }
}

resource "aws_apigatewayv2_integration" "chatbot" {
  # https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/apigatewayv2_integration

  api_id = aws_apigatewayv2_api.chatbot.id

  integration_uri    = aws_lambda_function.chatbot.invoke_arn
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "chatbot_message" {
  # https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/apigatewayv2_route

  api_id = aws_apigatewayv2_api.chatbot.id

  route_key = "ANY /chatbot/{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.chatbot.id}"
}

resource "aws_apigatewayv2_stage" "chatbot_live" {
  # https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/apigatewayv2_stage#throttling_burst_limit
  # https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-throttling.html

  api_id = aws_apigatewayv2_api.chatbot.id
  name   = "live"

  auto_deploy = true

  default_route_settings {
    detailed_metrics_enabled = true

    # The burst limit defines the number of requests your API can handle concurrently
    # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-stage-routesettings.html#cfn-apigatewayv2-stage-routesettings-throttlingburstlimit
    throttling_burst_limit = 3

    # The rate limit defines the number of allowed requests per second
    # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-stage-routesettings.html#cfn-apigatewayv2-stage-routesettings-throttlingratelimit
    throttling_rate_limit = 0.1
  }
}

# Lambda Invoke Permissions

resource "aws_lambda_permission" "chatbot" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.chatbot.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.chatbot.execution_arn}/*/*"
}

##########
# DYNAMODB
##########

resource "aws_dynamodb_table" "chatbot_messages_table" {
  name           = "ChatbotMessages"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "ConversationID"
  range_key      = "CreatedAt"

  deletion_protection_enabled = true

  attribute {
    name = "ConversationID"
    type = "S"
  }

  attribute {
    name = "CreatedAt"
    type = "N"
  }

  server_side_encryption {
    enabled = true
  }

  table_class = "STANDARD"

  ttl {
    attribute_name = "ExpiresAt"
    enabled        = true
  }
}