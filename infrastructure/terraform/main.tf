terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    # Configure for GovCloud
    bucket = "compliance-search-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "us-gov-west-1"
    encrypt = true
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "ComplianceSearch"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Variables
variable "aws_region" {
  description = "AWS GovCloud region"
  type        = string
  default     = "us-gov-west-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "compliance-search"
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"
  
  project_name = var.project_name
  environment  = var.environment
  vpc_cidr     = "10.0.0.0/16"
}

# S3 Buckets
module "storage" {
  source = "./modules/s3"
  
  project_name = var.project_name
  environment  = var.environment
}

# OpenSearch
module "opensearch" {
  source = "./modules/opensearch"
  
  project_name     = var.project_name
  environment      = var.environment
  vpc_id           = module.vpc.vpc_id
  subnet_ids       = module.vpc.private_subnet_ids
  security_group_ids = [module.vpc.opensearch_sg_id]
}

# Lambda Functions
module "lambda" {
  source = "./modules/lambda"
  
  project_name          = var.project_name
  environment           = var.environment
  vpc_id                = module.vpc.vpc_id
  subnet_ids            = module.vpc.private_subnet_ids
  security_group_ids    = [module.vpc.lambda_sg_id]
  source_bucket_name    = module.storage.source_bucket_name
  opensearch_endpoint   = module.opensearch.endpoint
}

# API Gateway
module "api_gateway" {
  source = "./modules/api_gateway"
  
  project_name       = var.project_name
  environment        = var.environment
  lambda_invoke_arns = module.lambda.invoke_arns
}

# CloudWatch & Monitoring
module "monitoring" {
  source = "./modules/monitoring"
  
  project_name = var.project_name
  environment  = var.environment
}

# Outputs
output "api_endpoint" {
  description = "API Gateway endpoint URL"
  value       = module.api_gateway.api_endpoint
}

output "source_bucket" {
  description = "S3 bucket for source documents"
  value       = module.storage.source_bucket_name
}

output "opensearch_endpoint" {
  description = "OpenSearch cluster endpoint"
  value       = module.opensearch.endpoint
  sensitive   = true
}
