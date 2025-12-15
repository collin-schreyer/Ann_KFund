"""
RAG query handler for compliance questions.
Performs vector search and generates answers using Bedrock.
"""

import json
import boto3
from typing import List, Dict

bedrock_client = boto3.client('bedrock-runtime', region_name='us-gov-west-1')
opensearch_client = boto3.client('opensearchserverless')

def lambda_handler(event, context):
    """
    Handle compliance query via API Gateway.
    """
    body = json.loads(event['body'])
    question = body['question']
    
    # Generate embedding for question
    question_embedding = generate_embedding(question)
    
    # Search OpenSearch for relevant chunks
    relevant_chunks = vector_search(question_embedding, top_k=10)
    
    # Build context from chunks
    context = build_context(relevant_chunks)
    
    # Generate answer using Claude
    answer = generate_answer(question, context)
    
    # Format response with citations
    response = {
        'answer': answer['text'],
        'citations': format_citations(relevant_chunks),
        'confidence': answer.get('confidence', 'medium')
    }
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(response)
    }

def generate_embedding(text: str) -> List[float]:
    """Generate embedding using Bedrock Titan."""
    response = bedrock_client.invoke_model(
        modelId='amazon.titan-embed-text-v1',
        body=json.dumps({'inputText': text})
    )
    
    result = json.loads(response['body'].read())
    return result['embedding']

def vector_search(embedding: List[float], top_k: int = 10) -> List[Dict]:
    """Search OpenSearch using k-NN."""
    # Simplified - actual implementation would use opensearch-py
    query = {
        'size': top_k,
        'query': {
            'knn': {
                'embedding': {
                    'vector': embedding,
                    'k': top_k
                }
            }
        }
    }
    
    # Return mock results for example
    return []

def build_context(chunks: List[Dict]) -> str:
    """Build context string from retrieved chunks."""
    context_parts = []
    
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[Source {i}] {chunk['regulation_type']} - "
            f"{chunk.get('regulation_section', 'N/A')}\n"
            f"{chunk['content']}\n"
        )
    
    return '\n'.join(context_parts)
