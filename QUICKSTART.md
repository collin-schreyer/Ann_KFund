# Quick Start Guide

Get the compliance search prototype running in 5 minutes.

## Prerequisites

- Python 3.8 or higher
- OpenAI API key (get one at https://platform.openai.com/api-keys)

## Steps

### 1. Install Dependencies

```bash
cd prototype
pip install -r requirements.txt
```

### 2. Set Up API Key

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

### 3. Load the Regulations

```bash
python ingest_documents.py
```

This loads the sample ITAR, EAR, and State Dept regulations into the database.

### 4. Try It Out

**Option A - Command Line:**

```bash
python query_system.py
```

Then ask: "Do I need a license to export thermal cameras to Mexico?"

**Option B - Web Interface:**

```bash
# Terminal 1: Start the API server
python api_server.py

# Terminal 2: Open the web interface
open web_interface.html
```

The web interface provides a nice UI for asking questions.

## Example Questions

- "Do I need a license to export thermal imaging cameras to Mexico?"
- "Can I share GPS technical data with a Canadian engineer?"
- "What is the de minimis rule?"
- "Are night vision devices subject to ITAR?"
- "Do I need an end-use certificate for police equipment?"

## What You'll See

The system will:
1. Search the regulations for relevant sections
2. Show which documents it found (ITAR, EAR, State Policy)
3. Generate an answer with specific citations
4. Indicate confidence level (high/medium/low)

## Troubleshooting

**"No module named 'chromadb'"**
- Run: `pip install -r requirements.txt`

**"OpenAI API key not found"**
- Make sure you created `.env` file with your API key

**"Collection not found"**
- Run `python ingest_documents.py` first to load the regulations

## Cost

Using OpenAI API:
- Embeddings: ~$0.0001 per query
- GPT-4: ~$0.03 per query
- Total: About $0.03 per question

Very cheap for testing!
