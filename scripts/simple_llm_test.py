#!/usr/bin/env python3
"""
Simple LLM Integration Test
Quick test to verify genuine LLM behavioral integration works
"""

import os
import json
from dotenv import load_dotenv
from genuine_llm_cascade_framework import GenuineLLMCascadeSimulation

load_dotenv()

def test_llm_integration():
    """Simple test of LLM coordination decision making"""
    
    print("=== SIMPLE LLM INTEGRATION TEST ===")
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OpenAI API key found")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...")
    
    try:
        # Initialize simulation
        print("Initializing LLM simulation...")
        sim = GenuineLLMCascadeSimulation()
        print("✅ LLM simulation initialized")
        
        # Run very short test (5 ticks only)
        print("Running short test scenario...")
        results = sim.run_genuine_llm_scenario("communication_breakdown", max_ticks=5, p_fail=0.1)
        
        print("✅ Test completed successfully!")
        print(f"📊 Results:")
        print(f"   LLM decisions: {results.get('total_llm_decisions', 0)}")
        print(f"   Total messages: {results.get('total_messages', 0)}")
        print(f"   Decision confidence: {results.get('average_decision_confidence', 0):.3f}")
        
        # Check if we got genuine LLM activity
        if results.get('total_llm_decisions', 0) > 0:
            print("🎉 GENUINE LLM INTEGRATION WORKING!")
            print(f"   Decision types: {results.get('decision_type_distribution', {})}")
            return True
        else:
            print("⚠️ No LLM decisions recorded - need to debug further")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_structured_baseline():
    """Test structured baseline for comparison"""
    
    print("\n=== STRUCTURED BASELINE TEST ===")
    
    try:
        from fixed_cascade_scenarios import FixedMultiHazardSimulation
        
        sim = FixedMultiHazardSimulation()
        results = sim.run_cascade_scenario("communication_breakdown", max_ticks=5)
        
        print("✅ Structured test completed")
        print(f"📊 Structured results:")
        print(f"   Total messages: {results.get('total_messages', 0)}")
        print(f"   System degradation: {results.get('system_degradation', {})}")
        
        return results
        
    except Exception as e:
        print(f"❌ Structured test failed: {e}")
        return None

def compare_approaches():
    """Compare LLM vs structured approaches"""
    
    print("\n=== COMPARISON TEST ===")
    
    # Test structured
    structured_results = test_structured_baseline()
    if not structured_results:
        print("❌ Cannot compare - structured test failed")
        return False
    
    # Test LLM
    llm_success = test_llm_integration()
    if not llm_success:
        print("❌ Cannot compare - LLM test failed")
        return False
    
    print("✅ Both approaches tested successfully")
    print("🔬 Genuine LLM behavioral integration confirmed!")
    return True

if __name__ == "__main__":
    print("Simple LLM Integration Test")
    print("===========================")
    
    success = compare_approaches()
    
    if success:
        print("\n🎉 SUCCESS: Genuine LLM integration working")
        print("Ready for full validation testing")
    else:
        print("\n❌ FAILED: Need to debug LLM integration")
        print("Check API key and framework setup")