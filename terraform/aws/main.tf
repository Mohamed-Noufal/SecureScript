terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.2.0"
}

provider "aws" {
  region = var.aws_region
}

# --- BACKEND (Lambda + API Gateway) ---

resource "aws_iam_role" "lambda_exec" {
  name = "securescript_lambda_role_${var.stage}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "api" {
  function_name    = "securescript-api-${var.stage}"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "server.handler" # Mangum handler
  runtime          = "python3.12"
  filename         = "../../backend/backend.zip" # Path to deployment package
  source_code_hash = filebase64sha256("../../backend/backend.zip")  # Force update on code change
  
  # Performance settings
  timeout     = 60   # 60 seconds for LLM API calls
  memory_size = 512  # 512 MB for better performance

  environment {
    variables = {
      GROQ_API_KEY             = var.groq_api_key
      CLERK_FRONTEND_API       = "" # Unset to skip JWKS fetch
      REQUIRE_JWT_VERIFICATION = "false" # Relaxed for Vercel+ClerkDev combination
      ALLOWED_ORIGINS          = "https://secure-script-alpha.vercel.app"
    }
  }
}

resource "aws_apigatewayv2_api" "lambda_api" {
  name          = "securescript-gw-${var.stage}"
  protocol_type = "HTTP"
  
  # CORS is handled by the Lambda function (FastAPI)

}

resource "aws_apigatewayv2_stage" "lambda_stage" {
  api_id      = aws_apigatewayv2_api.lambda_api.id
  name        = "$default"
  auto_deploy = true

  default_route_settings {
    throttling_burst_limit = 20
    throttling_rate_limit  = 10
  }
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id             = aws_apigatewayv2_api.lambda_api.id
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
  integration_uri    = aws_lambda_function.api.invoke_arn
}

resource "aws_apigatewayv2_route" "lambda_route" {
  api_id    = aws_apigatewayv2_api.lambda_api.id
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.lambda_api.execution_arn}/*/*"
}
