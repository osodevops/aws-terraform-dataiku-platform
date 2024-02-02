module "s3_bucket_staging" {
  count = var.s3_create_instance_bucket ? 1 : 0
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "~> 4.1"

  bucket = var.s3_instance_bucket_name
  # acl    = "private"

  # Bucket policies
  attach_policy = false

  attach_require_latest_tls_policy = true

  # S3 bucket-level Public Access Block configuration
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

  versioning = {
    status     = true
    mfa_delete = false
  }

  server_side_encryption_configuration = {
    rule = {
      bucket_key_enabled = true
      apply_server_side_encryption_by_default = {
        sse_algorithm = "AES256"
      }
    }
  }
}