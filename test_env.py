#!/usr/bin/env python3
"""Test script to verify .env loading and OpenAI key availability."""

import os
from dotenv import load_dotenv

print("=== Environment Variable Test ===")

# Test 1: Direct .env loading
print("\n1. Testing direct .env loading:")
load_dotenv()
openai_key_direct = os.getenv("OPENAI_API_KEY")
print(f"   Direct os.getenv: {openai_key_direct[:20] if openai_key_direct else 'None'}...")

# Test 2: Pydantic Settings
print("\n2. Testing pydantic settings:")
try:
    from app.core.settings import settings
    openai_key_settings = settings.OPENAI_API_KEY
    print(f"   Via settings.OPENAI_API_KEY: {openai_key_settings[:20] if openai_key_settings else 'None'}...")
    print(f"   Settings object type: {type(settings)}")
    
    # Test other keys too
    print(f"   SERPAPI_KEY: {settings.SERPAPI_KEY[:20] if settings.SERPAPI_KEY else 'None'}...")
    
except Exception as e:
    print(f"   Error loading settings: {e}")

# Test 3: OpenAI Client initialization
print("\n3. Testing OpenAI client:")
try:
    from openai import AsyncOpenAI
    if openai_key_settings:
        client = AsyncOpenAI(api_key=openai_key_settings)
        print(f"   OpenAI client created successfully")
    else:
        print(f"   Cannot create OpenAI client - no API key")
except Exception as e:
    print(f"   Error creating OpenAI client: {e}")

print("\n=== Test Complete ===")