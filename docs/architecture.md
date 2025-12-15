# GovCloud Compliance Search System - Architecture

## Overview

A Retrieval-Augmented Generation (RAG) system for searching export control regulations and determining compliance scenarios, deployed on AWS GovCloud.

## High-Level Architecture

```
┌─────────────────┐
│  State Dept     │
│  User           │
└────────┬────────┘
         │
         │ HTTPS
         ▼
┌─────────────────────────────────────────────────────┐
│              AWS GovCloud                            │
│                                                      │
│  ┌──────────────┐         ┌──────────────┐         │
│  │  API Gateway │────────▶│   Lambda     │         │
│  │  (REST API)  │         │  (API Layer) │         │
│  └──────────────┘         └──────┬───────┘         │
│                                   │                  │
│                                   ▼                  │
│                          ┌──────────────┐           │
│                          │   Bedrock    │           │
│                          │   (Claude)   │           │
│                          └──────┬───────┘           │
│                                 │                    │
│                                 ▼                    │
│  ┌──────────────┐      ┌──────────────┐            │
│  │  OpenSearch  │◀─────│   Lambda     │            │
│  │  (Vector DB) │      │  (Search)    │            │
│  └──────────────┘      └──────┬───────┘            │
│         ▲                      │                     │
│         │                      ▼                     │
│         │              ┌──────────────┐             │
│  ┌──────┴───────┐     │   Lambda     │             │
│  │   Lambda     │     │  (Ingestion) │             │
│  │  (Embedding) │     └──────┬───────┘             │
│  └──────────────┘            │                      │
│                               ▼                      │
│                       ┌──────────────┐              │
│                       │      S3      │              │
│                       │  (Documents) │              │
│                       └──────────────┘              │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │         CloudWatch Logs & CloudTrail         │  │
│  │              (Audit & Monitoring)            │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## Components

### 1. Document Storage (S3)

**Purpose:** Store source regulatory documents

**Buckets:**
- `compliance-docs-source` - Original documents (PDF, DOCX, MD)
- `compliance-docs-processed` - Processed/chunked documents
- `compliance-docs-embeddings` - Cached embeddings

**Security:**
- Server-side encryption (SSE-KMS)
- Versioning enabled
- Access logging
- Bucket policies restricting access to Lambda roles

### 2. Document Ingestion Pipeline (Lambda)

**Purpose:** Process and chunk documents for search

**Functions:**
- `ingest-document` - Triggered by S3 upload
- `chunk-document` - Split documents into searchable chunks
- `generate-embeddings` - Create vector embeddings

**Process:**
1. Document uploaded to S3
2. Lambda extracts text
3. Document chunked (500-1000 tokens per chunk)
4. Metadata extracted (regulation number, section, date)
5. Embeddings generated via Bedrock
6. Stored in OpenSearch

### 3. Vector Database (OpenSearch)

**Purpose:** Store and search document embeddings

**Index Structure:**
```json
{
  "chunk_id": "string",
  "regulation_type": "ITAR|EAR|STATE_POLICY",
  "regulation_section": "string",
  "content": "string",
  "embedding": [float array],
  "metadata": {
    "source_document": "string",
    "page_number": "integer",
    "last_updated": "date"
  }
}
```

**Search Methods:**
- Vector similarity search (k-NN)
- Hybrid search (vector + keyword)
- Filtered search by regulation type

### 4. LLM Service (Bedrock)

**Purpose:** Generate embeddings and answer queries

**Models:**
- **Embeddings:** Amazon Titan Embeddings
- **Generation:** Claude 3 (Sonnet or Opus)

**Why Bedrock:**
- FedRAMP authorized
- No data leaves AWS
- Pay-per-use pricing
- Multiple model options

### 5. API Layer (Lambda + API Gateway)

**Endpoints:**

```
POST /api/v1/query
- Submit compliance question
- Returns answer with citations

GET /api/v1/regulations/{type}
- List available regulations
- Returns metadata

POST /api/v1/documents/upload
- Upload new regulation document
- Triggers ingestion pipeline

GET /api/v1/search
- Direct search without LLM
- Returns matching chunks
```

**Authentication:**
- IAM authentication
- API keys for service accounts
- Integration with State Dept SSO (future)

### 6. Audit & Monitoring

**CloudWatch:**
- API request logs
- Lambda execution logs
- Error tracking and alerts

**CloudTrail:**
- All API calls logged
- S3 access logs
- IAM activity

**Metrics:**
- Query response time
- Search accuracy
- Token usage
- Error rates

## RAG Workflow

### Query Processing

1. **User submits question** via API
   ```
   "Do I need a license to export thermal cameras to Mexico?"
   ```

2. **Query embedding generated**
   - Question converted to vector embedding
   - Bedrock Titan Embeddings used

3. **Vector search performed**
   - OpenSearch finds top 10 relevant chunks
   - Hybrid search combines vector + keyword matching

4. **Context assembled**
   ```
   Retrieved chunks:
   - ITAR § 121.1 (relevance: 0.89)
   - ITAR Category XII (relevance: 0.85)
   - State Dept Mexico Policy (relevance: 0.82)
   ```

5. **LLM prompt constructed**
   ```
   System: You are an export control compliance assistant...
   
   Context: [Retrieved regulation chunks]
   
   Question: Do I need a license to export thermal cameras to Mexico?
   
   Instructions: Answer based only on provided context. Cite specific regulations.
   ```

6. **Response generated**
   - Claude analyzes context
   - Generates answer with citations
   - Includes confidence level

7. **Response returned to user**
   ```json
   {
     "answer": "Yes, thermal imaging cameras are controlled under ITAR Category XII...",
     "citations": [
       {
         "regulation": "ITAR",
         "section": "§ 121.1, Category XII",
         "relevance": 0.89
       }
     ],
     "confidence": "high"
   }
   ```

## Security Architecture

### Network Security

- VPC with private subnets
- No public internet access for Lambda
- VPC endpoints for AWS services
- Security groups restricting traffic

### Data Security

- Encryption at rest (KMS)
- Encryption in transit (TLS 1.2+)
- No data leaves GovCloud boundary
- Regular key rotation

### Access Control

- IAM roles with least privilege
- Service-to-service authentication
- No long-term credentials
- MFA for administrative access

### Compliance

- FedRAMP Moderate baseline
- FIPS 140-2 encryption
- Audit logging (5 year retention)
- Regular security assessments

## Scalability

### Current Design

- Lambda: Auto-scales to demand
- OpenSearch: 3-node cluster
- API Gateway: Handles 10,000 req/sec
- S3: Unlimited storage

### Future Scaling

- OpenSearch cluster expansion
- Multi-region deployment
- Caching layer (ElastiCache)
- CDN for static content

## Cost Estimate (Monthly)

- OpenSearch (3 nodes): $500
- Lambda (10K queries): $50
- Bedrock (10K queries): $200
- S3 Storage (100GB): $10
- API Gateway: $35
- CloudWatch/CloudTrail: $50

**Total: ~$845/month** for moderate usage

## Deployment

Infrastructure as Code using:
- Terraform or CloudFormation
- Automated CI/CD pipeline
- Blue/green deployments
- Automated testing

## Future Enhancements

1. **Multi-modal search** - Search images/diagrams in regulations
2. **Feedback loop** - Learn from user corrections
3. **Batch processing** - Analyze multiple scenarios
4. **Integration** - Connect to license application systems
5. **Advanced analytics** - Trend analysis, common queries
