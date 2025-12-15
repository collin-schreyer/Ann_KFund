# S3 Buckets for Compliance Search System

# KMS Key for S3 encryption
resource "aws_kms_key" "s3" {
  description             = "KMS key for S3 bucket encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true
}

resource "aws_kms_alias" "s3" {
  name          = "alias/${var.project_name}-s3"
  target_key_id = aws_kms_key.s3.key_id
}

# Source documents bucket
resource "aws_s3_bucket" "source" {
  bucket = "${var.project_name}-source-${var.environment}"
}

resource "aws_s3_bucket_versioning" "source" {
  bucket = aws_s3_bucket.source.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "source" {
  bucket = aws_s3_bucket.source.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.s3.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "source" {
  bucket = aws_s3_bucket.source.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Processed documents bucket
resource "aws_s3_bucket" "processed" {
  bucket = "${var.project_name}-processed-${var.environment}"
}

# Outputs
output "source_bucket_name" {
  value = aws_s3_bucket.source.id
}

output "source_bucket_arn" {
  value = aws_s3_bucket.source.arn
}
