"""
Test Google provider dynamic model discovery.

This test verifies that the Google provider can dynamically discover
available models using the genai.list_models() API.
"""

import pytest
from backend.model_providers import get_provider
from backend.model_providers.base import ModelInfo
import os


@pytest.mark.skipif(
    not os.getenv("GOOGLE_API_KEY"),
    reason="GOOGLE_API_KEY environment variable not set"
)
def test_google_dynamic_discovery():
    """Test that Google provider can dynamically discover models."""
    # Get Google provider
    provider = get_provider("google")
    assert provider is not None
    assert provider.id == "google"
    
    # Get API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    credentials = {"api_key": api_key}
    
    # Test dynamic discovery
    result = provider.validate_credentials_and_list_models(credentials)
    
    # Verify result structure
    assert "valid" in result
    assert "models" in result
    assert "message" in result
    
    # Should be valid
    assert result["valid"] is True, f"Validation failed: {result.get('error', 'Unknown error')}"
    
    # Should have models
    assert len(result["models"]) > 0, "No models discovered"
    
    # Print discovered models for debugging
    print(f"\n✓ Discovered {len(result['models'])} models:")
    for model in result["models"]:
        print(f"  - {model.id}: {model.name}")
        print(f"    Context: {model.context_length:,} tokens")
        print(f"    Description: {model.description}")
        assert isinstance(model, ModelInfo)
        assert model.id
        assert model.name
        assert model.context_length > 0
    
    # Verify common models are present (at least one of these should exist)
    model_ids = [m.id for m in result["models"]]
    common_models = [
        "gemini-1.5-pro-latest",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-2.0-flash-exp"
    ]
    
    found_common = any(model_id in model_ids for model_id in common_models)
    assert found_common, f"No common Gemini models found. Available: {model_ids}"
    
    print(f"\n✓ Test passed! Dynamic discovery working correctly.")


def test_google_fallback_without_credentials():
    """Test that Google provider falls back to static list without credentials."""
    provider = get_provider("google")
    assert provider is not None
    
    # Call list_models without credentials
    models = provider.list_models({})
    
    # Should return static fallback list
    assert len(models) > 0
    assert any(m.id == "gemini-1.5-pro-latest" for m in models)
    
    print(f"\n✓ Fallback works: {len(models)} static models available")


@pytest.mark.skipif(
    not os.getenv("GOOGLE_API_KEY"),
    reason="GOOGLE_API_KEY environment variable not set"
)
def test_google_list_models_with_credentials():
    """Test that list_models uses dynamic discovery when credentials provided."""
    provider = get_provider("google")
    api_key = os.getenv("GOOGLE_API_KEY")
    credentials = {"api_key": api_key}
    
    # Should use dynamic discovery
    models = provider.list_models(credentials)
    
    # Should have models
    assert len(models) > 0
    
    print(f"\n✓ list_models() returned {len(models)} dynamic models")
    for model in models[:3]:  # Show first 3
        print(f"  - {model.id}: {model.name}")


def test_google_invalid_api_key():
    """Test that invalid API key is handled gracefully."""
    provider = get_provider("google")
    credentials = {"api_key": "invalid-key-12345"}
    
    result = provider.validate_credentials_and_list_models(credentials)
    
    # Should be invalid
    assert result["valid"] is False
    assert "error" in result
    assert len(result["models"]) == 0
    
    print(f"\n✓ Invalid key handled correctly: {result['error']}")


if __name__ == "__main__":
    """Run tests manually for quick verification."""
    print("=" * 80)
    print("Google Provider Dynamic Discovery Tests")
    print("=" * 80)
    
    if os.getenv("GOOGLE_API_KEY"):
        print("\n1. Testing dynamic discovery with valid credentials...")
        try:
            test_google_dynamic_discovery()
        except Exception as e:
            print(f"✗ Failed: {e}")
        
        print("\n2. Testing list_models with credentials...")
        try:
            test_google_list_models_with_credentials()
        except Exception as e:
            print(f"✗ Failed: {e}")
    else:
        print("\n⚠ GOOGLE_API_KEY not set, skipping live tests")
    
    print("\n3. Testing fallback without credentials...")
    try:
        test_google_fallback_without_credentials()
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    print("\n4. Testing invalid API key handling...")
    try:
        test_google_invalid_api_key()
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    print("\n" + "=" * 80)
    print("All tests completed!")
    print("=" * 80)
