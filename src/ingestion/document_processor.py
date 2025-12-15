"""
Document ingestion and processing for compliance search system.
Extracts text, chunks documents, and generates embeddings.
"""

import json
import boto3
from typing import List, Dict
import hashlib

s3_client = boto3.client('s3')
bedrock_client = boto3.client('bedrock-runtime', region_name='us-gov-west-1')

def lambda_handler(event, context):
    """
    Triggered by S3 upload. Processes document and stores in OpenSearch.
    """
    # Get bucket and key from S3 event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # Download document
    response = s3_client.get_object(Bucket=bucket, Key=key)
    content = response['Body'].read().decode('utf-8')
    
    # Extract metadata from filename/path
    metadata = extract_metadata(key)
    
    # Chunk document
    chunks = chunk_document(content, metadata)
    
    # Generate embeddings and store
    for chunk in chunks:
        embedding = generate_embedding(chunk['content'])
        chunk['embedding'] = embedding
        store_in_opensearch(chunk)
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Processed {len(chunks)} chunks from {key}')
    }

def extract_metadata(key: str) -> Dict:
    """Extract regulation type and metadata from file path."""
    parts = key.split('/')
    filename = parts[-1]
    
    metadata = {
        'source_document': filename,
        'regulation_type': 'UNKNOWN'
    }
    
    if 'ITAR' in filename:
        metadata['regulation_type'] = 'ITAR'
    elif 'EAR' in filename:
        metadata['regulation_type'] = 'EAR'
    elif 'State' in filename or 'Policy' in filename:
        metadata['regulation_type'] = 'STATE_POLICY'
    
    return metadata

def chunk_document(content: str, metadata: Dict, chunk_size: int = 800) -> List[Dict]:
    """Split document into chunks with overlap."""
    chunks = []
    words = content.split()
    overlap = 100
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        chunk_text = ' '.join(chunk_words)
        
        chunk_id = hashlib.md5(chunk_text.encode()).hexdigest()
        
        chunks.append({
            'chunk_id': chunk_id,
            'content': chunk_text,
            'regulation_type': metadata['regulation_type'],
            'source_document': metadata['source_document'],
            'chunk_index': len(chunks)
        })
    
    return chunks
