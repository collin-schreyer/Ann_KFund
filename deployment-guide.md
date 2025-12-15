# Deployment Guide - GovCloud Compliance Search System

## Prerequisites

1. **AWS GovCloud Account**
   - Account must be provisioned through AWS GovCloud process
   - IAM user with AdministratorAccess or equivalent permissions
   - MFA enabled for all users

2. **Tools Required**
   - Terraform >= 1.0
   - AWS CLI configured for GovCloud
   - Python 3.11+
   - Docker (for Lambda packaging)

3. **Security Requirements**
   - VPN or Direct Connect to GovCloud (recommended)
   - CAC/PIV authentication (if required by your agency)
   - Approved security baseline configuration

## Step 1: Configure AWS CLI for GovCloud

```bash
aws configure --profile govcloud
# AWS Access Key ID: [Use IAM role, not hardcoded keys]
# AWS Secret Access Key: [Use IAM role]
# Default region name: us-gov-west-1
# Default output format: json
```

## Step 2: Initialize Terraform

```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Review planned changes
terraform plan -out=tfplan

# Apply infrastructure
terraform apply tfplan
```

## Step 3: Upload Sample Regulations

```bash
# Get bucket name from Terraform output
BUCKET=$(terraform output -raw source_bucket)

# Upload sample regulations
aws s3 cp sample-regulations/ s3://$BUCKET/regulations/ --recursive --profile govcloud
```

## Step 4: Verify Deployment

```bash
# Get API endpoint
API_ENDPOINT=$(terraform output -raw api_endpoint)

# Test query endpoint
curl -X POST $API_ENDPOINT/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Do I need a license to export thermal cameras?"}'
```

## Step 5: Configure Monitoring

1. Set up CloudWatch alarms
2. Configure SNS notifications
3. Enable CloudTrail logging
4. Set up log retention policies

## Security Checklist

- [ ] All S3 buckets have encryption enabled
- [ ] VPC endpoints configured for AWS services
- [ ] Security groups follow least privilege
- [ ] IAM roles use least privilege policies
- [ ] CloudTrail enabled and logging to secure bucket
- [ ] MFA required for administrative actions
- [ ] No hardcoded credentials in code
- [ ] Secrets stored in AWS Secrets Manager
- [ ] Regular security assessments scheduled

## Troubleshooting

### Lambda can't access OpenSearch
- Check security group rules
- Verify VPC endpoint configuration
- Check IAM role permissions

### Documents not being processed
- Check S3 event notifications
- Review Lambda logs in CloudWatch
- Verify Lambda has S3 read permissions

### API returns 403 errors
- Check API Gateway authorization
- Verify IAM authentication
- Review CloudWatch API Gateway logs
