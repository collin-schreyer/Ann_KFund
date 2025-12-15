#!/usr/bin/env python3
"""
Test the system with example queries.
"""

import os
from query_system import search_regulations, generate_answer
from dotenv import load_dotenv

load_dotenv()

# Test questions from sample-queries
TEST_QUESTIONS = [
    "Do I need a license to export thermal imaging cameras to Mexico?",
    "Can I share technical data with a Canadian engineer?",
    "What is the de minimis rule?",
    "Are GPS receivers for commercial drones subject to ITAR?",
    "Do I need an end-use certificate for night vision equipment?"
]

def run_tests():
    print("🧪 Running test queries...\n")
    
    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}: {question}")
        print('='*70)
        
        try:
            results = search_regulations(question, n_results=3)
            print(f"\n📚 Found {len(results['documents'][0])} relevant sections:")
            for meta in results['metadatas'][0]:
                print(f"   - {meta['source']} ({meta['regulation_type']})")
            
            print("\n🤖 Generating answer...")
            answer = generate_answer(question, results)
            print(f"\n{answer}\n")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n✅ Test complete!")

if __name__ == "__main__":
    run_tests()
