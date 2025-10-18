#!/usr/bin/env python3
"""
Fast test for multi-agent orchestration - ensure NO fallback responses
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

# Test queries that trigger multi-agent orchestration
ORCHESTRATION_TESTS = [
    {
        "name": "Ideas (IdeaInitiatorAgent)",
        "query": "Give me some starter ideas for this competition",
        "expected_agents": ["idea_initiator", "IdeaInitiatorAgent"],
        "min_chars": 300
    },
    {
        "name": "Timeline (TimelineCoachAgent)",
        "query": "Help me create a timeline for this competition",
        "expected_agents": ["timeline_coach", "TimelineCoachAgent"],
        "min_chars": 300
    },
    {
        "name": "Progress Check (ProgressMonitorAgent)",
        "query": "How am I doing in this competition?",
        "expected_agents": ["progress_monitor", "ProgressMonitorAgent"],
        "min_chars": 200
    },
    {
        "name": "Multi-hop Reasoning",
        "query": "I'm stuck at 0.75 score, what should I try next?",
        "expected_agents": ["multihop", "MultiHopReasoningAgent", "idea_initiator"],
        "min_chars": 300
    }
]

def test_query(test_case):
    """Test a single query"""
    print(f"\n{'='*60}")
    print(f"🧪 TEST: {test_case['name']}")
    print(f"Query: {test_case['query']}")
    print(f"{'='*60}")
    
    data = {
        "query": test_case["query"],
        "competition_id": "titanic"
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/component-orchestrator/query",
            json=data,
            timeout=60
        )
        elapsed = time.time() - start_time
        
        result = response.json()
        
        # Extract fields
        agents_used = result.get('agents_used', [])
        confidence = result.get('confidence', 0)
        system = result.get('system', 'unknown')
        response_text = result.get('final_response', result.get('response', ''))
        
        print(f"\n✅ RESPONSE RECEIVED ({elapsed:.1f}s)")
        print(f"  Agents: {agents_used}")
        print(f"  Confidence: {confidence}")
        print(f"  System: {system}")
        print(f"  Length: {len(response_text)} chars")
        
        # Check for issues
        issues = []
        
        # Check 1: Not fallback
        if "fallback" in str(agents_used).lower():
            issues.append("❌ FALLBACK AGENT DETECTED!")
        
        # Check 2: Minimum length
        if len(response_text) < test_case['min_chars']:
            issues.append(f"⚠️ Response too short (< {test_case['min_chars']} chars)")
        
        # Check 3: Confidence
        if confidence < 0.7:
            issues.append(f"⚠️ Low confidence ({confidence})")
        
        # Check 4: Expected agents (at least one should match)
        agent_match = any(
            expected.lower() in str(agents_used).lower() 
            for expected in test_case['expected_agents']
        )
        if not agent_match:
            issues.append(f"⚠️ Expected agents not found: {test_case['expected_agents']}")
        
        if issues:
            print(f"\n🔴 ISSUES:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print(f"\n✅ ALL CHECKS PASSED!")
        
        # Show preview
        print(f"\n📝 Response preview:")
        print(response_text[:400] + "..." if len(response_text) > 400 else response_text)
        
        return {
            "test": test_case['name'],
            "passed": len(issues) == 0,
            "issues": issues,
            "agents": agents_used,
            "confidence": confidence,
            "length": len(response_text)
        }
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return {
            "test": test_case['name'],
            "passed": False,
            "issues": [f"Exception: {e}"],
            "agents": [],
            "confidence": 0,
            "length": 0
        }

def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║    MULTI-AGENT ORCHESTRATION TEST SUITE                 ║
║    Goal: NO FALLBACK RESPONSES from orchestration       ║
╚══════════════════════════════════════════════════════════╝
""")
    
    results = []
    for test_case in ORCHESTRATION_TESTS:
        result = test_query(test_case)
        results.append(result)
        time.sleep(2)  # Brief pause between tests
    
    # Summary
    print(f"\n\n{'='*60}")
    print(f"📊 FINAL SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for r in results if r['passed'])
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! No fallback responses detected!")
        print("✅ System ready for launch!")
    else:
        print(f"\n⚠️ {total - passed} tests need attention:")
        for r in results:
            if not r['passed']:
                print(f"\n  ❌ {r['test']}")
                for issue in r['issues']:
                    print(f"     {issue}")
    
    # Export results
    with open('orchestration_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Results saved to orchestration_test_results.json")

if __name__ == "__main__":
    main()

