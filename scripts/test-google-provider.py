#!/usr/bin/env python3
"""
Quick test script for Google Gemini provider.
Tests single-turn and multi-turn conversations.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from model_providers import get_provider, Message

def test_google_provider():
    """Test Google Gemini provider with sample messages."""
    
    print("Testing Google Gemini Provider")
    print("="*80)
    
    # Get provider
    provider = get_provider("google")
    if not provider:
        print("ERROR: Google provider not found")
        return False
    
    print(f"✓ Provider loaded: {provider.label}")
    
    # Check if API key is set
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("\n⚠ GOOGLE_API_KEY not set in environment")
        print("  Set it with: export GOOGLE_API_KEY='your-key-here'")
        return False
    
    credentials = {"api_key": api_key}
    print(f"✓ API key found (length: {len(api_key)})")
    
    # Test 1: Single turn
    print("\n" + "-"*80)
    print("Test 1: Single-turn conversation")
    print("-"*80)
    
    try:
        messages = [
            Message(role="system", content="You are a helpful assistant. Answer briefly."),
            Message(role="user", content="What is 2+2? Answer in one sentence.")
        ]
        
        response = provider.chat(
            credentials=credentials,
            model="gemini-1.5-flash-latest",  # Use faster model for testing
            messages=messages,
            temperature=0.3,
            max_tokens=100
        )
        
        print(f"✓ Response received ({len(response.content)} chars)")
        print(f"  Content: {response.content[:200]}")
        print(f"  Model: {response.model}")
        if response.usage:
            print(f"  Tokens: {response.usage}")
        
    except Exception as e:
        print(f"✗ Test 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Multi-turn
    print("\n" + "-"*80)
    print("Test 2: Multi-turn conversation")
    print("-"*80)
    
    try:
        messages = [
            Message(role="system", content="You are a helpful assistant. Answer briefly."),
            Message(role="user", content="What is the capital of France?"),
            Message(role="assistant", content="The capital of France is Paris."),
            Message(role="user", content="What is its population?")
        ]
        
        response = provider.chat(
            credentials=credentials,
            model="gemini-1.5-flash-latest",
            messages=messages,
            temperature=0.3,
            max_tokens=100
        )
        
        print(f"✓ Response received ({len(response.content)} chars)")
        print(f"  Content: {response.content[:200]}")
        
    except Exception as e:
        print(f"✗ Test 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Long context (RAG-like)
    print("\n" + "-"*80)
    print("Test 3: RAG-style context")
    print("-"*80)
    
    try:
        context = """
        [1] Smith et al. (2020) found that machine learning models perform better with larger datasets.
        [2] Johnson (2021) showed that proper validation is crucial for model evaluation.
        [3] Lee and Park (2022) demonstrated improved accuracy using ensemble methods.
        """
        
        messages = [
            Message(role="system", content="You are an academic research assistant. Answer based on the provided context and cite sources using [N] format."),
            Message(role="user", content=f"Based on the following research:\n{context}\n\nQuestion: What improves model performance?")
        ]
        
        response = provider.chat(
            credentials=credentials,
            model="gemini-1.5-flash-latest",
            messages=messages,
            temperature=0.3,
            max_tokens=200
        )
        
        print(f"✓ Response received ({len(response.content)} chars)")
        print(f"  Content: {response.content}")
        
        # Check if it's actually an answer and not just returning the context
        if len(response.content) < 50:
            print(f"⚠ WARNING: Response seems too short, might be returning snippets")
        elif context[:100] in response.content:
            print(f"⚠ WARNING: Response contains raw context, might be echoing instead of answering")
        else:
            print(f"✓ Response appears to be a proper synthesis")
        
    except Exception as e:
        print(f"✗ Test 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "="*80)
    print("All tests passed! ✓")
    print("="*80)
    return True

if __name__ == "__main__":
    success = test_google_provider()
    sys.exit(0 if success else 1)
