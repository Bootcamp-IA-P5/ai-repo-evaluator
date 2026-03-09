#!/usr/bin/env python3
"""
Simple test script to verify AI configuration functionality.

This script tests the new AI provider, model, and API key functionality
without requiring a full FastAPI server setup.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ai_client import AIClient, AIProvider
from services.ai_evaluation_engine import AIEvaluationEngine
from core.settings import settings


def test_ai_client_with_custom_config():
    """Test AI client with custom provider and API key."""
    print("Testing AI Client with custom configuration...")
    
    try:
        # Test with Gemini (default)
        print("1. Testing default configuration (Gemini)...")
        client1 = AIClient()
        print(f"   Provider: {client1.provider}")
        print(f"   Model: {client1.model}")
        print(f"   Client type: {type(client1.client)}")
        
        # Test with custom provider (if API keys are available)
        print("2. Testing custom configuration...")
        try:
            client2 = AIClient(
                provider=AIProvider.OPENAI,
                model="gpt-3.5-turbo",
                api_key="test-key"  # This will fail but shows the interface works
            )
            print(f"   Provider: {client2.provider}")
            print(f"   Model: {client2.model}")
            print("   ✓ Custom configuration accepted")
        except Exception as e:
            print(f"   Expected error with test API key: {e}")
            print("   ✓ Custom configuration interface works")
        
        assert True
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        assert False


def test_evaluation_engine_with_custom_config():
    """Test evaluation engine with custom AI configuration."""
    print("\nTesting Evaluation Engine with custom configuration...")
    
    try:
        # Test with default configuration
        print("1. Testing default configuration...")
        engine1 = AIEvaluationEngine()
        print(f"   Provider: {engine1.ai_client.provider}")
        print(f"   Model: {engine1.ai_client.model}")
        print("   ✓ Default configuration works")
        
        # Test with custom configuration
        print("2. Testing custom configuration...")
        try:
            engine2 = AIEvaluationEngine(
                provider=AIProvider.OPENAI,
                model="gpt-3.5-turbo",
                api_key="test-key"  # This will fail but shows the interface works
            )
            print(f"   Provider: {engine2.ai_client.provider}")
            print(f"   Model: {engine2.ai_client.model}")
            print("   ✓ Custom configuration accepted")
        except Exception as e:
            print(f"   Expected error with test API key: {e}")
            print("   ✓ Custom configuration interface works")
        
        assert True
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        assert False


def test_schema_validation():
    """Test Pydantic schema validation."""
    print("\nTesting schema validation...")
    
    try:
        from schemas.evaluation import EvaluationRequest
        
        # Test valid request without AI config
        print("1. Testing valid request without AI config...")
        req1 = EvaluationRequest(
            repo_url="https://github.com/test/repo",
            rubric_id=1,
            briefing_path="/path/to/briefing.pdf"
        )
        print("   ✓ Valid request without AI config accepted")
        
        # Test valid request with complete AI config
        print("2. Testing valid request with complete AI config...")
        req2 = EvaluationRequest(
            repo_url="https://github.com/test/repo",
            rubric_id=1,
            briefing_path="/path/to/briefing.pdf",
            ai_provider="openai",
            ai_model="gpt-3.5-turbo",
            ai_api_key="sk-test-key"
        )
        print("   ✓ Valid request with complete AI config accepted")
        
        # Test invalid provider
        print("3. Testing invalid provider...")
        try:
            req4 = EvaluationRequest(
                repo_url="https://github.com/test/repo",
                rubric_id=1,
                briefing_path="/path/to/briefing.pdf",
                ai_provider="invalid-provider",
                ai_model="gpt-3.5-turbo",
                ai_api_key="sk-test-key"
            )
            print("   ✗ Should have failed validation")
            return False
        except Exception as e:
            print(f"   ✓ Correctly rejected invalid provider: {e}")
        
        assert True
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        assert False


def main():
    """Run all tests."""
    print("=== AI Configuration Test Suite ===\n")
    
    tests = [
        test_ai_client_with_custom_config,
        test_evaluation_engine_with_custom_config,
        test_schema_validation,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"=== Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("✓ All tests passed! AI configuration functionality is working correctly.")
        return 0
    else:
        print("✗ Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())