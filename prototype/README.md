# Compliance Search System - Local Prototype

A working prototype of the GovCloud compliance search system that runs locally.

## What This Does

- Loads sample regulations (ITAR, EAR, State Dept policies) into a vector database
- Lets you ask compliance questions in natural language
- Searches relevant regulation sections using semantic search
- Generates answers with specific citations using GPT-4
- Provides both CLI and REST API interfaces

## Setup

### 1. Install Dependencies

```bash
cd prototype
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-...your-key-here
```

### 3. Ingest Documents

Load the sample regulations into the database:

```bash
python ingest_documents.py
```

You should see:
```
🚀 Starting document ingestion...
📄 Loading regulation files...
   Found 4 regulation files
✂️  Created 45 chunks
💾 Adding to vector database...
✅ Successfully ingested 45 chunks into ChromaDB
```

## Usage

### Option 1: Command Line Interface

```bash
python query_system.py
```

Then ask questions:
```
> Do I need a license to export thermal cameras to Mexico?
> Can I share GPS technical data with a Canadian engineer?
> What is the de minimis rule for Country B?
```

### Option 2: REST API

Start the server:

```bash
python api_server.py
```

The API runs at `http://localhost:8000`

Test with curl:

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Do I need a license to export thermal cameras to Mexico?"
  }'
```

Or visit the interactive docs: `http://localhost:8000/docs`

## Example Questions

Try these from `../sample-queries/example-questions.md`:

1. "Do I need a license to export thermal imaging cameras with 640x480 resolution to Mexico?"
2. "Can I hire a foreign national to work on aircraft navigation systems?"
3. "What are the requirements for exporting night vision equipment to NATO allies?"
4. "Is 256-bit AES encryption software subject to ITAR or EAR?"
5. "Do I need an end-use certificate for police equipment exports?"

## How It Works

1. **Ingestion**: Documents are split into chunks and embedded using OpenAI embeddings
2. **Storage**: Chunks stored in ChromaDB (local vector database)
3. **Search**: User question is embedded and similar chunks retrieved via k-NN search
4. **Generation**: GPT-4 analyzes retrieved chunks and generates answer with citations
5. **Response**: Answer returned with source documents and confidence level

## Architecture

```
User Question
     ↓
[Embedding Model] → Vector
     ↓
[ChromaDB Search] → Top 5 relevant chunks
     ↓
[GPT-4] → Answer with citations
     ↓
Response
```

## Differences from Production

This prototype uses:
- **OpenAI** instead of AWS Bedrock
- **ChromaDB** instead of OpenSearch
- **Local storage** instead of S3
- **No authentication** (production uses IAM)
- **No audit logging** (production logs everything)

But the core RAG logic is the same!

## Next Steps

Once you've tested the prototype:
1. Show it to Ann and her State Dept contact
2. Get feedback on answer quality
3. Add more regulations if needed
4. Deploy to GovCloud using the Terraform templates
