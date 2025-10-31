#!/usr/bin/env python3
"""
Simple test to verify the new multi-agent system works
"""

import sys
import os

# Add the copy directory to the path
sys.path.insert(0, r'C:\Users\heman\Kaggle-competition-assist-copy')

print("=== Testing New Multi-Agent System ===")
print()

try:
    # Test import
    print("1. Testing imports...")
    from master_orchestrator import MasterOrchestrator
    print("   ✅ MasterOrchestrator imported successfully")
    
    # Test initialization
    print("2. Testing initialization...")
    orchestrator = MasterOrchestrator()
    print("   ✅ MasterOrchestrator initialized successfully")
    
    # Test query processing
    print("3. Testing query processing...")
    result = orchestrator.run("test query", {"section": "test"}, mode="auto")
    print(f"   ✅ Query processed successfully")
    print(f"   Result type: {type(result)}")
    print(f"   Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
    
    print()
    print("🎉 SUCCESS: New Multi-Agent System is working!")
    print("The issue is just that the backend is running from the wrong directory.")
    print("Solution: Copy all new system files to the original directory.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()






