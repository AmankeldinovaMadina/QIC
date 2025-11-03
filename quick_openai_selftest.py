#!/usr/bin/env python3
"""Quick OpenAI self-test to verify Responses API works."""

import asyncio
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os

async def main():
    # Load environment
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return
    
    print(f"✅ Found OpenAI API key: {api_key[:20]}...")
    
    try:
        client = AsyncOpenAI(api_key=api_key)
        
        schema = {
            "type": "object", 
            "properties": {"ok": {"type": "boolean"}}, 
            "required": ["ok"], 
            "additionalProperties": False
        }
        
        print("🚀 Testing OpenAI Chat Completions with JSON Schema...")
        
        completion = await client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "Ping",
                    "schema": schema,
                    "strict": True
                }
            },
            messages=[{"role": "user", "content": "Return {\"ok\": true} exactly."}]
        )
        
        result = completion.choices[0].message.content
        print(f"✅ OpenAI Chat Completions API works! Result: {result}")
        
        # Parse to verify it's valid JSON
        parsed = json.loads(result)
        if parsed.get("ok") is True:
            print("✅ JSON schema validation passed")
        else:
            print(f"⚠️  Unexpected result: {parsed}")
            
    except Exception as e:
        print(f"❌ OpenAI Chat Completions API failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())