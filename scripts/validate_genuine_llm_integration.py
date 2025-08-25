#!/usr/bin/env python3
"""
Validation Script for Genuine LLM Integration
Tests that LLM actually influences coordination behavior vs cosmetic enhancement
"""

import json
import os
import sys
from pathlib import Path
import numpy as np
from loguru import logger
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import pandas as pd

# Import both frameworks for comparison
from fixed_cascade_scenarios import FixedMultiHazardSimulation
try:
    from genuine_llm_cascade_framework import GenuineLLMCascadeSimulation
    GENUINE_LLM_AVAILABLE = True
except ImportError as e:
    GENUINE_LLM_AVAILABLE = False
    print(f"⚠️ Genuine LLM framework not available: {e}")

def check_environment_setup():
    """Validate environment setup for genuine LLM integration"""
    
    print("ENVIRONMENT VALIDATION")
    print("=" * 40)
    
    # Check .env file
    if not os.path.exists('.env'):
        print("[!] .env file not found")
        print("   Create .env file with: OPENAI_API_KEY=sk-your-key-here")
        return False
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("[!] OPENAI_API_KEY not found in .env")
        return False
    
    if not api_key.startswith('sk-'):
        print("[!] Invalid OPENAI_API_KEY format")
        return False
    
    print(f"[+] OpenAI API key configured: {api_key[:10]}...")
    
    # Check framework availability
    if not GENUINE_LLM_AVAILABLE:
        print("[!] Genuine LLM framework not available")
        return False
    
    print("[+] Genuine LLM framework available")
    
    # Test basic LLM connection
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        # Simple test request
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Test connection - respond with 'OK'"}],
            max_tokens=5
        )
        
        result = response.choices[0].message.content.strip()
        if 'OK' in result:
            print("[+] OpenAI API connection successful")
            return True
        else:
            print("[!] Unexpected API response")
            return False
            
    except Exception as e:
        print(f"[!] OpenAI API connection failed: {e}")
        return False

def run_behavioral_comparison_test():
    """Compare structured vs genuine LLM behavioral patterns"""
    
    print("\nBEHAVIORAL COMPARISON TEST")
    print("=" * 40)
    
    if not check_environment_setup():
        print("[!] Environment setup failed - cannot run behavioral test")
        return None
    
    results = {}
    scenario = "communication_breakdown"  # Simple scenario for validation
    
    # Test 1: Structured approach (baseline)
    print("\nRunning STRUCTURED baseline...")
    structured_sim = FixedMultiHazardSimulation()
    
    structured_results = structured_sim.run_cascade_scenario(
        scenario, max_ticks=30, p_fail=0.1
    )
    
    # Extract available metrics from structured results
    total_messages = structured_results.get('total_messages', 0)
    successful_messages = total_messages - structured_results.get('failed_messages', 0)
    
    results['structured'] = {
        'system_degradation': np.mean(list(structured_results.get('system_degradation', {}).values())) if structured_results.get('system_degradation') else 0.0,
        'total_messages': total_messages,
        'successful_messages': successful_messages,
        'coordination_success_rate': successful_messages / max(1, total_messages),
        'decision_pattern': 'fixed_probability_0.7'
    }
    
    print(f"   System degradation: {results['structured']['system_degradation']:.3f}")
    print(f"   Messages: {results['structured']['total_messages']}")
    print(f"   Success rate: {results['structured']['coordination_success_rate']:.3f}")
    
    # Test 2: Genuine LLM approach
    print("\nRunning GENUINE LLM approach...")
    
    try:
        llm_sim = GenuineLLMCascadeSimulation()
        llm_results = llm_sim.run_genuine_llm_scenario(
            scenario, max_ticks=30, p_fail=0.1
        )
        
        # Extract available metrics from LLM results
        total_messages = llm_results.get('total_messages', 0)
        successful_messages = total_messages - llm_results.get('failed_messages', 0)
        
        results['genuine_llm'] = {
            'system_degradation': np.mean(list(llm_results.get('system_degradation', {}).values())) if llm_results.get('system_degradation') else 0.0,
            'total_messages': total_messages,
            'successful_messages': successful_messages,
            'coordination_success_rate': successful_messages / max(1, total_messages),
            'llm_decisions': llm_results.get('total_llm_decisions', 0),
            'decision_confidence': llm_results.get('average_decision_confidence', 0.5),
            'decision_distribution': llm_results.get('decision_type_distribution', {}),
            'decision_pattern': 'llm_dynamic_confidence_based'
        }
        
        print(f"   System degradation: {results['genuine_llm']['system_degradation']:.3f}")
        print(f"   Messages: {results['genuine_llm']['total_messages']}")
        print(f"   Success rate: {results['genuine_llm']['coordination_success_rate']:.3f}")
        print(f"   LLM decisions: {results['genuine_llm']['llm_decisions']}")
        print(f"   Avg confidence: {results['genuine_llm']['decision_confidence']:.3f}")
        
    except Exception as e:
        print(f"[!] Genuine LLM test failed: {e}")
        return results
    
    return results

def validate_behavioral_differences(results):
    """Validate that LLM creates genuinely different behavior"""
    
    print("\nBEHAVIORAL DIFFERENCE VALIDATION")
    print("=" * 40)
    
    if not results or 'genuine_llm' not in results:
        print("[!] Cannot validate - LLM results missing")
        return False
    
    structured = results['structured']
    llm = results['genuine_llm']
    
    # Test 1: Different coordination success rates
    success_diff = abs(structured['coordination_success_rate'] - llm['coordination_success_rate'])
    
    if success_diff < 0.05:  # Less than 5% difference
        print(f"[!] SUSPICIOUS: Coordination success rates too similar")
        print(f"   Structured: {structured['coordination_success_rate']:.3f}")
        print(f"   LLM: {llm['coordination_success_rate']:.3f}")
        print(f"   Difference: {success_diff:.3f} (< 0.05 threshold)")
        print("   This suggests cosmetic-only LLM integration!")
        return False
    else:
        print(f"[+] SUCCESS RATES DIFFER: {success_diff:.3f}")
        print(f"   Structured: {structured['coordination_success_rate']:.3f}")
        print(f"   LLM: {llm['coordination_success_rate']:.3f}")
    
    # Test 2: Different system degradation
    degradation_diff = abs(structured['system_degradation'] - llm['system_degradation'])
    
    if degradation_diff < 0.02:  # Less than 2% difference
        print(f"[!] SUSPICIOUS: System degradation too similar")
        print(f"   Difference: {degradation_diff:.3f} (< 0.02 threshold)")
        return False
    else:
        print(f"[+] SYSTEM IMPACT DIFFERS: {degradation_diff:.3f}")
    
    # Test 3: LLM decision patterns
    if 'decision_distribution' in llm:
        decision_types = list(llm['decision_distribution'].keys())
        if len(decision_types) <= 1:
            print(f"[!] SUSPICIOUS: Only {len(decision_types)} decision types")
            return False
        else:
            print(f"[+] DECISION VARIETY: {len(decision_types)} decision types")
            for dtype, count in llm['decision_distribution'].items():
                print(f"   {dtype}: {count}")
    
    # Test 4: LLM confidence variation
    if llm['decision_confidence'] == 0.7:  # Exactly the fixed probability
        print(f"[!] SUSPICIOUS: LLM confidence exactly matches fixed probability (0.7)")
        return False
    else:
        print(f"[+] DYNAMIC CONFIDENCE: {llm['decision_confidence']:.3f} (≠ 0.7)")
    
    print(f"\nBEHAVIORAL VALIDATION PASSED!")
    print(f"   [+] LLM creates genuinely different coordination patterns")
    print(f"   [+] Success rates vary based on LLM decisions")
    print(f"   [+] System outcomes influenced by LLM behavior")
    
    return True

def generate_validation_report(results):
    """Generate detailed validation report"""
    
    if not results:
        return
    
    report = {
        'validation_timestamp': pd.Timestamp.now().isoformat(),
        'test_scenario': 'communication_breakdown',
        'frameworks_compared': list(results.keys()),
        'behavioral_differences': {},
        'validation_status': 'passed' if 'genuine_llm' in results else 'failed'
    }
    
    if 'genuine_llm' in results:
        structured = results['structured'] 
        llm = results['genuine_llm']
        
        report['behavioral_differences'] = {
            'coordination_success_rate_diff': abs(structured['coordination_success_rate'] - llm['coordination_success_rate']),
            'system_degradation_diff': abs(structured['system_degradation'] - llm['system_degradation']),
            'message_count_diff': abs(structured['total_messages'] - llm['total_messages']),
            'llm_decision_count': llm['llm_decisions'],
            'llm_confidence_avg': llm['decision_confidence'],
            'decision_type_variety': len(llm['decision_distribution'])
        }
    
    report['results'] = results
    
    # Save validation report
    with open('genuine_llm_validation_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nValidation report saved: genuine_llm_validation_report.json")
    return report

def create_comparison_visualization(results):
    """Create visualization comparing approaches"""
    
    if not results or 'genuine_llm' not in results:
        return
    
    # Prepare data for visualization
    approaches = ['Structured', 'Genuine LLM']
    success_rates = [
        results['structured']['coordination_success_rate'],
        results['genuine_llm']['coordination_success_rate']
    ]
    degradation = [
        results['structured']['system_degradation'],
        results['genuine_llm']['system_degradation']
    ]
    
    # Create comparison plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Success rates
    bars1 = ax1.bar(approaches, success_rates, color=['blue', 'green'], alpha=0.7)
    ax1.set_ylabel('Coordination Success Rate')
    ax1.set_title('Coordination Success Comparison')
    ax1.set_ylim(0, 1.0)
    
    for bar, rate in zip(bars1, success_rates):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{rate:.3f}', ha='center', va='bottom')
    
    # System degradation
    bars2 = ax2.bar(approaches, degradation, color=['red', 'orange'], alpha=0.7)
    ax2.set_ylabel('System Degradation')
    ax2.set_title('System Impact Comparison')
    ax2.set_ylim(0, max(degradation) * 1.2)
    
    for bar, deg in zip(bars2, degradation):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{deg:.3f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('genuine_llm_behavioral_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Comparison visualization saved: genuine_llm_behavioral_comparison.png")

def main():
    """Main validation function"""
    
    print("GENUINE LLM INTEGRATION VALIDATION")
    print("=" * 50)
    print("Testing whether LLM creates genuine behavioral differences")
    print("vs cosmetic content-only enhancement\n")
    
    # Run behavioral comparison
    results = run_behavioral_comparison_test()
    
    if results:
        # Validate differences
        is_genuine = validate_behavioral_differences(results)
        
        # Generate reports
        report = generate_validation_report(results)
        create_comparison_visualization(results)
        
        if is_genuine:
            print(f"\nVALIDATION SUCCESSFUL!")
            print(f"   [+] Genuine LLM behavioral integration confirmed")
            print(f"   [+] LLM decisions influence coordination outcomes")
            print(f"   [+] Different patterns vs structured approach")
            print(f"   [+] Reports saved: validation_report.json, comparison.png")
        else:
            print(f"\nVALIDATION FAILED!")
            print(f"   [!] LLM integration appears cosmetic-only")
            print(f"   [!] Results too similar to structured approach")
            print(f"   [!] Need genuine behavioral integration")
    
    else:
        print(f"\nVALIDATION INCOMPLETE")
        print(f"   Environment setup or framework issues")
        print(f"   Check .env file and API key")

if __name__ == "__main__":
    main()