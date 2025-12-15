# GovCloud Compliance Search System

A RAG-based system for searching State Department regulations and determining compliance scenarios.

## Project Structure

```
├── sample-regulations/          # Example regulatory documents
├── sample-queries/              # Example compliance questions
├── infrastructure/              # AWS GovCloud infrastructure code
├── src/                        # Application code
│   ├── ingestion/              # Document processing pipeline
│   ├── search/                 # Search and RAG logic
│   └── api/                    # API endpoints
└── docs/                       # Design documentation
```

## Quick Start

1. Review sample regulations in `sample-regulations/`
2. Check example queries in `sample-queries/`
3. Review architecture in `docs/architecture.md`
4. Deploy infrastructure using `infrastructure/` templates

## Security Note

This system is designed for AWS GovCloud with FedRAMP compliance in mind. All credentials use IAM roles - never hardcode access keys.
