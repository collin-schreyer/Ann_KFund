#!/usr/bin/env python3
"""
Ingest sample regulations into ChromaDB vector database.
Run this first to load the documents.
"""

import os
import chromadb
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Initialize OpenAI client for embeddings
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embeddings(texts: list) -> list:
    """Get embeddings for a list of texts using OpenAI API."""
    response = openai_client.embeddings.create(
        model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        input=texts
    )
    return [item.embedding for item in response.data]

def load_regulation_files():
    """Load ONLY K Fund regulation markdown files."""
    # Try both paths (running from prototype/ or from root)
    regulations_dir = Path("../sample-regulations")
    if not regulations_dir.exists():
        regulations_dir = Path("sample-regulations")
    documents = []
    
    for file_path in regulations_dir.glob("*.md"):
        filename = file_path.stem
        
        # ONLY load K Fund related documents
        if 'K-Fund' not in filename and 'K_Fund' not in filename:
            print(f"   Skipping non-K-Fund file: {filename}")
            continue
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        documents.append({
            'content': content,
            'metadata': {
                'source': filename,
                'regulation_type': 'K_FUND',
                'file_path': str(file_path)
            }
        })
    
    return documents

def chunk_document(content, metadata, chunk_size=1000, overlap=200):
    """Split document into overlapping chunks."""
    chunks = []
    lines = content.split('\n')
    current_chunk = []
    current_size = 0
    
    for line in lines:
        line_size = len(line)
        
        if current_size + line_size > chunk_size and current_chunk:
            # Save current chunk
            chunk_text = '\n'.join(current_chunk)
            chunks.append({
                'content': chunk_text,
                'metadata': {**metadata, 'chunk_index': len(chunks)}
            })
            
            # Start new chunk with overlap
            overlap_lines = current_chunk[-3:] if len(current_chunk) > 3 else current_chunk
            current_chunk = overlap_lines + [line]
            current_size = sum(len(l) for l in current_chunk)
        else:
            current_chunk.append(line)
            current_size += line_size
    
    # Add final chunk
    if current_chunk:
        chunk_text = '\n'.join(current_chunk)
        chunks.append({
            'content': chunk_text,
            'metadata': {**metadata, 'chunk_index': len(chunks)}
        })
    
    return chunks

def main():
    print("🚀 Starting document ingestion...")
    
    # Initialize ChromaDB - use path relative to this script
    script_dir = Path(__file__).parent
    chroma_path = script_dir / "chroma_db"
    client = chromadb.PersistentClient(path=str(chroma_path))
    print(f"   Using ChromaDB at: {chroma_path}")
    
    # Get or create collection (no embedding function - we'll provide embeddings directly)
    try:
        client.delete_collection("compliance_regulations")
    except:
        pass
    
    collection = client.create_collection(
        name="compliance_regulations",
        metadata={"description": "K Fund guidelines and representational expense policies"}
    )
    
    # Load and process documents
    print("📄 Loading regulation files...")
    documents = load_regulation_files()
    print(f"   Found {len(documents)} regulation files")
    
    # Chunk and add to database
    all_chunks = []
    for doc in documents:
        chunks = chunk_document(doc['content'], doc['metadata'])
        all_chunks.extend(chunks)
    
    print(f"✂️  Created {len(all_chunks)} chunks")
    
    # Add to ChromaDB with embeddings
    print("💾 Adding to vector database...")
    
    # Get embeddings for all chunks
    print("🔢 Generating embeddings...")
    chunk_texts = [chunk['content'] for chunk in all_chunks]
    embeddings = get_embeddings(chunk_texts)
    
    collection.add(
        documents=chunk_texts,
        embeddings=embeddings,
        metadatas=[chunk['metadata'] for chunk in all_chunks],
        ids=[f"chunk_{i}" for i in range(len(all_chunks))]
    )
    
    print(f"✅ Successfully ingested {len(all_chunks)} chunks into ChromaDB")
    print(f"   Collection: {collection.name}")
    print(f"   Total items: {collection.count()}")

if __name__ == "__main__":
    main()
