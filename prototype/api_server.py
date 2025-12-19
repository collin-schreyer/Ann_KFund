#!/usr/bin/env python3
"""
FastAPI server for K Fund event allocation and guidelines search.
Provides REST API for querying K Fund regulations.
"""

import os
import secrets
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import chromadb
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

# Basic Auth
security = HTTPBasic()
AUTH_USER = os.getenv("AUTH_USER", "admin")
AUTH_PASS = os.getenv("AUTH_PASS", "BAdos2025!")


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify basic auth credentials."""
    correct_user = secrets.compare_digest(credentials.username, AUTH_USER)
    correct_pass = secrets.compare_digest(credentials.password, AUTH_PASS)
    if not (correct_user and correct_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Initialize clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ChromaDB path - use /tmp for Render (ephemeral storage)
chroma_path = os.getenv("CHROMA_PATH", "./chroma_db")
chroma_client = chromadb.PersistentClient(path=chroma_path)


def get_embeddings_batch(texts: list) -> list:
    """Get embeddings for a list of texts using OpenAI API."""
    response = openai_client.embeddings.create(
        model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        input=texts
    )
    return [item.embedding for item in response.data]


def auto_ingest_if_empty():
    """Auto-ingest K Fund documents if the collection is empty or doesn't exist."""
    try:
        collection = chroma_client.get_collection("compliance_regulations")
        if collection.count() > 0:
            print(f"✅ ChromaDB already has {collection.count()} documents")
            return
    except Exception:
        pass  # Collection doesn't exist, will create it
    
    print("🚀 Auto-ingesting K Fund documents...")
    
    # Find regulations directory
    script_dir = Path(__file__).parent
    regulations_dir = script_dir.parent / "sample-regulations"
    if not regulations_dir.exists():
        regulations_dir = script_dir / "sample-regulations"
    if not regulations_dir.exists():
        print("⚠️ No sample-regulations directory found")
        return
    
    # Load K Fund documents
    documents = []
    for file_path in regulations_dir.glob("*.md"):
        filename = file_path.stem
        if 'K-Fund' not in filename and 'K_Fund' not in filename:
            continue
        with open(file_path, 'r') as f:
            content = f.read()
        documents.append({
            'content': content,
            'metadata': {'source': filename, 'regulation_type': 'K_FUND'}
        })
    
    if not documents:
        print("⚠️ No K Fund documents found")
        return
    
    # Chunk documents
    all_chunks = []
    for doc in documents:
        lines = doc['content'].split('\n')
        current_chunk = []
        current_size = 0
        for line in lines:
            if current_size + len(line) > 1000 and current_chunk:
                chunk_text = '\n'.join(current_chunk)
                all_chunks.append({
                    'content': chunk_text,
                    'metadata': {**doc['metadata'], 'chunk_index': len(all_chunks)}
                })
                current_chunk = current_chunk[-3:] if len(current_chunk) > 3 else current_chunk
                current_size = sum(len(l) for l in current_chunk)
            current_chunk.append(line)
            current_size += len(line)
        if current_chunk:
            all_chunks.append({
                'content': '\n'.join(current_chunk),
                'metadata': {**doc['metadata'], 'chunk_index': len(all_chunks)}
            })
    
    # Create collection and add documents
    try:
        chroma_client.delete_collection("compliance_regulations")
    except Exception:
        pass
    
    collection = chroma_client.create_collection(
        name="compliance_regulations",
        metadata={"description": "K Fund guidelines"}
    )
    
    # Get embeddings and add to collection
    chunk_texts = [c['content'] for c in all_chunks]
    embeddings = get_embeddings_batch(chunk_texts)
    
    collection.add(
        documents=chunk_texts,
        embeddings=embeddings,
        metadatas=[c['metadata'] for c in all_chunks],
        ids=[f"chunk_{i}" for i in range(len(all_chunks))]
    )
    
    print(f"✅ Ingested {len(all_chunks)} chunks from {len(documents)} K Fund documents")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    auto_ingest_if_empty()
    yield


app = FastAPI(title="K Fund Allocation API", version="1.0.0", lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str
    n_results: int = 5

class Citation(BaseModel):
    source: str
    regulation_type: str
    relevance_score: float
    summary: str = ""  # AI-generated summary of why this was matched
    matched_text: str = ""  # Original text (hidden by default in UI)

class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
    confidence: str

@app.get("/")
def root(username: str = Depends(verify_credentials)):
    """Serve the main index.html page."""
    index_path = Path(__file__).parent / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {
        "service": "K Fund Allocation API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/api")
def api_info():
    return {
        "service": "K Fund Allocation API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": [
            "/api/v1/query - POST - Query K Fund guidelines",
            "/api/v1/health - GET - Health check"
        ]
    }

def get_embedding(text: str) -> List[float]:
    """Get embedding using OpenAI API."""
    response = openai_client.embeddings.create(
        model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        input=text
    )
    return response.data[0].embedding

@app.post("/api/v1/query", response_model=QueryResponse)
def query_compliance(request: QueryRequest):
    """
    Submit a compliance question and get an answer with citations.
    """
    try:
        # Get embedding for the question
        query_embedding = get_embedding(request.question)
        
        # Search regulations
        collection = chroma_client.get_collection(name="compliance_regulations")
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=request.n_results
        )
        
        # Build context
        context = "\n\n---\n\n".join([
            f"[Source: {meta['source']}]\n{content}"
            for content, meta in zip(results['documents'][0], results['metadatas'][0])
        ])
        
        # Generate answer
        system_prompt = """You are an expert K Fund (EDCS) compliance assistant for the U.S. Department of State.
Answer questions about K Fund allowability for representational expenses based ONLY on the provided guidelines.
Cite specific authorities (22 U.S.C. § 2671, 22 U.S.C. § 2694, GAO guidance, etc.).
End with a confidence level: HIGH, MEDIUM, or LOW."""

        response = openai_client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-5.2-chat-latest"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Question: {request.question}\n\nRegulations:\n{context}"}
            ],
            max_completion_tokens=2000
        )
        
        answer_text = response.choices[0].message.content
        
        # Extract confidence (simple heuristic)
        confidence = "medium"
        if "HIGH" in answer_text.upper():
            confidence = "high"
        elif "LOW" in answer_text.upper():
            confidence = "low"
        
        # Format citations with matched text chunks
        citations = [
            Citation(
                source=meta['source'],
                regulation_type=meta['regulation_type'],
                relevance_score=1.0 - (i * 0.1),
                matched_text=content
            )
            for i, (meta, content) in enumerate(zip(results['metadatas'][0], results['documents'][0]))
        ]
        
        return QueryResponse(
            answer=answer_text,
            citations=citations,
            confidence=confidence
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class LineItemRequest(BaseModel):
    item: str
    cost: float
    foreign_guests: int = 0
    total_guests: int = 0

class ClassificationResponse(BaseModel):
    item: str
    cost: float
    classification: str  # K_FUND_ALLOWABLE, NOT_ALLOWABLE, LEGAL_REVIEW
    k_fund_amount: float
    authority: str
    rationale: str
    regulation_text: str
    confidence: str
    prorated: bool
    questions: List[str] = []
    sources_consulted: List[str] = []
    payer: str = "Operating Funds"
    flagged: bool = False
    flag_reason: str = ""
    per_person_cost: float = 0.0

class BatchClassifyRequest(BaseModel):
    line_items: List[LineItemRequest]
    event_name: str = ""
    foreign_guests: int = 0
    total_guests: int = 0

class BatchClassifyResponse(BaseModel):
    event_name: str
    foreign_guests: int
    total_guests: int
    foreign_percentage: float
    line_items: List[ClassificationResponse]
    totals: Dict[str, float]

@app.post("/api/v1/classify", response_model=ClassificationResponse)
def classify_line_item(request: LineItemRequest):
    """
    Classify a single line item for K Fund allowability using RAG.
    
    RAG Pipeline:
    1. Generate multiple search queries for better retrieval
    2. Search ChromaDB vector database for relevant K Fund guidelines
    3. Build context from retrieved chunks with source citations
    4. Send to GPT-4 for classification with grounded reasoning
    """
    try:
        # Get relevant K Fund guidelines from vector DB
        collection = chroma_client.get_collection(name="compliance_regulations")
        
        # Generate multiple search queries for better retrieval coverage
        search_queries = [
            f"Is {request.item} allowable under K Fund EDCS representational expenses?",
            f"K Fund classification rules for {request.item}",
            f"22 U.S.C. 2671 allowable expenses {request.item}",
            "K Fund always allowable never allowable items list"
        ]
        
        # Retrieve chunks for each query and deduplicate
        all_chunks = {}
        for query in search_queries:
            query_embedding = get_embedding(query)
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=4
            )
            if results['documents'] and results['documents'][0]:
                for content, meta in zip(results['documents'][0], results['metadatas'][0]):
                    key = hash(content[:100])
                    is_kfund = 'K-Fund' in meta.get('source', '') or 'K_Fund' in meta.get('source', '')
                    if key not in all_chunks or is_kfund:
                        all_chunks[key] = {"content": content, "source": meta['source'], "is_kfund": is_kfund}
        
        # Build rich context with source citations
        # Sort to prioritize K Fund docs first
        sorted_chunks = sorted(all_chunks.values(), key=lambda x: (not x.get('is_kfund', False), x['source']))
        
        context_parts = []
        sources_used = set()
        for chunk in sorted_chunks[:6]:  # Top 6 unique chunks, K Fund first
            context_parts.append(f"[Source: {chunk['source']}]\n{chunk['content']}")
            sources_used.add(chunk['source'])
        
        context = "\n\n---\n\n".join(context_parts)
        
        print(f"RAG: Retrieved {len(context_parts)} chunks from {len(sources_used)} sources for '{request.item}'")
        
        # Calculate proration
        foreign_pct = request.foreign_guests / request.total_guests if request.total_guests > 0 else 1.0
        
        # Use AI to classify
        system_prompt = """You are a K Fund (EDCS) classification expert for the U.S. Department of State.
Classify the line item as one of:
- K_FUND_ALLOWABLE: Representational expense for foreign officials (gifts, hospitality, courtesies)
- NOT_ALLOWABLE: Operational, capital, personnel, or transportation expense
- LEGAL_REVIEW: Unclear - needs Legal Adviser determination

Respond in this exact JSON format:
{
    "classification": "K_FUND_ALLOWABLE" or "NOT_ALLOWABLE" or "LEGAL_REVIEW",
    "authority": "specific statute like 22 U.S.C. § 2671 or 22 U.S.C. § 2694",
    "rationale": "one sentence explanation",
    "regulation_text": "relevant quote from regulations",
    "confidence": "high" or "medium" or "low",
    "needs_proration": true or false,
    "questions": ["question1", "question2"] (only if LEGAL_REVIEW)
}"""

        response = openai_client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-5.2-chat-latest"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Line item: {request.item}\nCost: ${request.cost}\nForeign guests: {request.foreign_guests}/{request.total_guests}\n\nK Fund Guidelines:\n{context}"}
            ],
            max_completion_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        
        # Calculate K Fund amount
        needs_proration = result.get("needs_proration", False)
        if result["classification"] == "K_FUND_ALLOWABLE":
            k_fund_amount = request.cost * foreign_pct if needs_proration else request.cost
        else:
            k_fund_amount = 0

        # Calculate Per-Person Cost
        per_person = request.cost / request.total_guests if request.total_guests > 0 else 0
        
        # Determine Payer and Check Flags
        payer = "Operating Funds"
        flagged = False
        flag_reason = ""
        
        item_lower = request.item.lower()
        
        # 1. Check Prohibited Items (Personal)
        prohibited_keywords = ['yacht', 'casino', 'gambling', 'spouse', 'family', 'vacation', 'personal']
        if any(bad in item_lower for bad in prohibited_keywords):
            payer = "Personal Funds"
            flagged = True
            flag_reason = "Prohibited item detected (e.g., personal/lavish)"
            result["classification"] = "NOT_ALLOWABLE" # Override AI if it missed it
            k_fund_amount = 0
            
        # 2. Check Allowability for Payer
        elif result["classification"] == "K_FUND_ALLOWABLE":
            if needs_proration:
                payer = "K Fund / Operating (Split)"
            else:
                payer = "K Fund (EDCS)"
        elif result["classification"] == "LEGAL_REVIEW":
            payer = "Pending Review"
            
        # 3. Check Cost Caps (Soft Cap: $150/pp for food/event)
        if not flagged and per_person > 150:
            flagged = True
            flag_reason = f"High per-person cost (${per_person:.2f}). Justification required."
            if payer == "K Fund (EDCS)":
                payer = "K Fund (Requires Memo)"
        
        return ClassificationResponse(
            item=request.item,
            cost=request.cost,
            classification=result["classification"],
            k_fund_amount=k_fund_amount,
            authority=result.get("authority", ""),
            rationale=result.get("rationale", ""),
            regulation_text=result.get("regulation_text", ""),
            confidence=result.get("confidence", "medium"),
            prorated=needs_proration and result["classification"] == "K_FUND_ALLOWABLE",
            questions=result.get("questions", []),
            sources_consulted=list(sources_used),
            payer=payer,
            flagged=flagged,
            flag_reason=flag_reason,
            per_person_cost=per_person
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/classify-batch", response_model=BatchClassifyResponse)
def classify_batch(request: BatchClassifyRequest):
    """
    Classify multiple line items for K Fund allowability.
    """
    results = []
    for item in request.line_items:
        item.foreign_guests = request.foreign_guests
        item.total_guests = request.total_guests
        result = classify_line_item(item)
        results.append(result)
    
    # Calculate totals
    k_fund_total = sum(r.k_fund_amount for r in results if r.classification == "K_FUND_ALLOWABLE")
    not_allowable_total = sum(r.cost for r in results if r.classification == "NOT_ALLOWABLE")
    legal_review_total = sum(r.cost for r in results if r.classification == "LEGAL_REVIEW")
    
    foreign_pct = (request.foreign_guests / request.total_guests * 100) if request.total_guests > 0 else 0
    
    return BatchClassifyResponse(
        event_name=request.event_name,
        foreign_guests=request.foreign_guests,
        total_guests=request.total_guests,
        foreign_percentage=foreign_pct,
        line_items=results,
        totals={
            "k_fund": k_fund_total,
            "not_allowable": not_allowable_total,
            "legal_review": legal_review_total,
            "total": k_fund_total + not_allowable_total + legal_review_total
        }
    )

@app.get("/api/v1/health")
def health_check():
    """Health check endpoint."""
    try:
        collection = chroma_client.get_collection("compliance_regulations")
        doc_count = collection.count()
        return {
            "status": "healthy",
            "database": "connected",
            "document_count": doc_count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# Serve static files (HTML, CSS, JS)
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Serve HTML pages (protected)
@app.get("/index.html")
def serve_index(username: str = Depends(verify_credentials)):
    return FileResponse(Path(__file__).parent / "index.html")

@app.get("/search.html")
def serve_search(username: str = Depends(verify_credentials)):
    return FileResponse(Path(__file__).parent / "search.html")

@app.get("/allocation.html")
def serve_allocation(username: str = Depends(verify_credentials)):
    return FileResponse(Path(__file__).parent / "allocation.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
