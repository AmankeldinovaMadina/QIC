"""Simple test to verify the application works."""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app
from app.core.settings import settings

async def test_basic_import():
    """Test that we can import the main app."""
    print("✅ FastAPI app imported successfully")
    print(f"✅ App name: {settings.app_name}")
    print(f"✅ App version: {settings.app_version}")
    print(f"✅ Debug mode: {settings.debug}")
    
    # Test that we can access the API router
    routes = [route.path for route in app.routes]
    print(f"✅ Available routes: {routes}")
    
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_basic_import())
        if result:
            print("\n🎉 Basic application test passed!")
        else:
            print("\n❌ Basic application test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)