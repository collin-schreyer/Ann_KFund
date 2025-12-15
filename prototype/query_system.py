#!/usr/bin/env python3
"""
Query the compliance search system.
Simple CLI interface for testing.
"""

import os
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def search_regulations(query, n_results=5):
    """Search for relevant regulation chunks."""
    # Initialize ChromaDB
    client = chromadb.PersistentClient(path="./chroma_db")
    
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    )
    
    collection = client.get_collection(
        name="compliance_regulations",
        embedding_function=openai_ef
    )
    
    # Perform search
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    
    return results

def generate_answer(question, context_chunks):
    """Generate answer using OpenAI."""
    # Build context from chunks
    context = "\n\n---\n\n".join([
        f"[Source: {meta['source']}]\n{content}"
        for content, meta in zip(context_chunks['documents'][0], context_chunks['metadatas'][0])
    ])
    
    # Create prompt
    system_prompt = """You are an expert export control compliance assistant for the U.S. State Department.

Your role is to help determine whether exports require licenses under ITAR (International Traffic in Arms Regulations) or EAR (Export Administration Regulations).

IMPORTANT INSTRUCTIONS:
1. Answer ONLY based on the provided regulation excerpts
2. Cite specific regulation sections (e.g., "ITAR § 121.1" or "EAR § 734.3")
3. If the regulations don't contain enough information, say so
4. Be precise about thresholds and specifications
5. Distinguish between ITAR and EAR jurisdiction clearly
6. Note when end-use certificates or other documentation is required

Format your response with:
- Direct answer to the question
- Relevant regulation citations
- Key considerations or caveats
- Confidence level (high/medium/low)"""

    user_prompt = f"""Based on the following regulation excerpts, please answer this compliance question:

QUESTION: {question}

REGULATION EXCERPTS:
{context}

Please provide a detailed answer with specific citations."""

    # Call OpenAI
    response = client_openai.chat.completions.create(
        model=os.getenv("LLM_MODEL", "gpt-4-turbo-preview"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3
    )
    
    return response.choices[0].message.content

def main():
    print("🔍 Compliance Search System - Prototype")
    print("=" * 60)
    print()
    
    while True:
        question = input("Enter your compliance question (or 'quit' to exit):\n> ")
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not question.strip():
            continue
        
        print("\n🔎 Searching regulations...")
        results = search_regulations(question, n_results=5)
        
        print(f"   Found {len(results['documents'][0])} relevant sections\n")
        
        print("🤖 Generating answer...\n")
        answer = generate_answer(question, results)
        
        print("=" * 60)
        print("ANSWER:")
        print("=" * 60)
        print(answer)
        print("\n" + "=" * 60)
        print("\nSOURCES:")
        for i, meta in enumerate(results['metadatas'][0], 1):
            print(f"  [{i}] {meta['source']} ({meta['regulation_type']})")
        print("=" * 60)
        print()

if __name__ == "__main__":
    main()
