variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "us-east-1"
}

variable "groq_api_key" {
  description = "API Key for Groq"
  type        = string
  sensitive   = true
}

variable "clerk_frontend_api" {
  description = "Clerk Frontend API URL"
  type        = string
}

variable "stage" {
  description = "Deployment stage (e.g. dev, prod)"
  type        = string
  default     = "prod"
}
