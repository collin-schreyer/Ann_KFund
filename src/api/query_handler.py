"""
API Gateway Lambda handler for query endpoint.
"""

import json
import os
from datetime import datetime

def lambda_handler(event, context):
    """
    POST /api/v1/query
    Submit compliance question and get answer with citations.
    """
    
    # Parse request
    try:
        body = json.loads(event.get('body', '{}'))
        question = body.get('question')
        
        if not question:
            return error_response(400, 'Question is required')
        
        # Log query for audit
        log_query(question, event)
        
        # Process query (would call RAG pipeline)
        result = process_query(question)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        return error_response(500, str(e))

def process_query(question: str) -> dict:
    """Process compliance query through RAG pipeline."""
    # This would call the RAG search function
    # For now, return example response
    return {
        'answer': 'Based on the regulations...',
        'citations': [],
        'confidence': 'medium',
        'timestamp': datetime.utcnow().isoformat()
    }

def log_query(question: str, event: dict):
    """Log query for audit trail."""
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'question': question,
        'user': event.get('requestContext', {}).get('identity', {}).get('userArn'),
        'source_ip': event.get('requestContext', {}).get('identity', {}).get('sourceIp')
    }
    print(json.dumps(log_entry))

def error_response(status_code: int, message: str) -> dict:
    """Return error response."""
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'error': message})
    }
