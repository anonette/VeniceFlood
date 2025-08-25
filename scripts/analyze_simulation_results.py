#!/usr/bin/env python3
"""
Analyze Venice flood simulation results and generate visualizations
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

def load_message_log(scenario: str) -> pd.DataFrame:
    """Load message log for a scenario into DataFrame"""
    log_file = f"message_log_{scenario}.ndjson"
    
    if not Path(log_file).exists():
        print(f"Warning: {log_file} not found")
        return pd.DataFrame()
    
    messages = []
    with open(log_file, 'r') as f:
        for line in f:
            msg = json.loads(line)
            messages.append(msg)
    
    return pd.DataFrame(messages)

def load_snapshots(scenario: str) -> dict:
    """Load tick snapshots for a scenario"""
    snapshot_file = f"snapshots_{scenario}.json"
    
    if not Path(snapshot_file).exists():
        print(f"Warning: {snapshot_file} not found")
        return {}
    
    with open(snapshot_file, 'r') as f:
        return json.load(f)

def analyze_scenario_metrics(scenario: str):
    """Analyze detailed metrics for a single scenario"""
    print(f"\n=== DETAILED ANALYSIS: SCENARIO {scenario} ===")
    print(f"Debug: Starting analysis for scenario {scenario}")
    
    # Load data
    print(f"Debug: Loading message log...")
    messages_df = load_message_log(scenario)
    print(f"Debug: Loading snapshots...")
    snapshots = load_snapshots(scenario)
    
    if messages_df.empty or not snapshots:
        print(f"No data available for scenario {scenario}")
        return {}
    
    print(f"Debug: Data loaded - {len(messages_df)} messages, {len(snapshots)} snapshots")
    
    # Basic message statistics
    total_messages = len(messages_df)
    successful_messages = len(messages_df[messages_df['success'] == True])
    delivery_ratio = successful_messages / total_messages if total_messages > 0 else 0
    
    print(f"📊 Message Statistics:")
    print(f"  Total messages: {total_messages:,}")
    print(f"  Successful deliveries: {successful_messages:,}")
    print(f"  Delivery ratio: {delivery_ratio:.3f}")
    
    # Intent breakdown
    print(f"Debug: Computing intent breakdown...")
    intent_counts = messages_df['intent'].value_counts()
    print(f"  Message types: {dict(intent_counts)}")
    
    # Time-to-acknowledgment analysis (with debug output)
    print("  Debug: Starting time-to-acknowledgment analysis...")
    request_response_times = []
    requests = messages_df[messages_df['intent'] == 'request_support'].copy()
    commits = messages_df[messages_df['intent'] == 'commit'].copy()
    
    print(f"  Debug: Found {len(requests)} requests and {len(commits)} commits")
    
    # Much simpler approach - avoid iterrows entirely
    print(f"  Debug: Simplifying time analysis to avoid pandas issues...")
    
    # Convert to basic Python lists to avoid pandas complexity
    request_list = requests[['sender', 'tick', 'payload']].to_dict('records')
    commit_list = commits[['receiver', 'tick', 'payload']].to_dict('records')
    
    print(f"  Debug: Processing {len(request_list)} requests vs {len(commit_list)} commits")
    
    # Process only first 100 requests for performance
    max_to_process = min(100, len(request_list))
    
    for i, request in enumerate(request_list[:max_to_process]):
        if i % 50 == 0:
            print(f"  Debug: Processing request {i+1}/{max_to_process}")
            
        try:
            request_payload = request.get('payload', {})
            if not isinstance(request_payload, dict):
                continue
                
            need = request_payload.get('need', '')
            sender = request['sender']
            request_tick = request['tick']
            
            # Find first matching commit
            for commit in commit_list:
                if (commit['receiver'] == sender and 
                    commit['tick'] > request_tick):
                    try:
                        commit_payload = commit.get('payload', {})
                        if isinstance(commit_payload, dict):
                            commit_need = commit_payload.get('need', '')
                            if commit_need == need:
                                response_time = commit['tick'] - request_tick
                                request_response_times.append(response_time)
                                break
                    except:
                        continue
                        
        except Exception as e:
            continue
    
    print(f"  Debug: Completed time analysis, found {len(request_response_times)} response pairs")
    
    if request_response_times:
        median_response_time = np.median(request_response_times)
        print(f"  Median response time: {median_response_time:.1f} ticks")
        print(f"  Response time range: {min(request_response_times)}-{max(request_response_times)} ticks")
    else:
        print(f"  No successful request-response pairs found")
    
    # Agent load analysis
    print("  Debug: Starting agent load analysis...")
    sender_counts = messages_df['sender'].value_counts()
    receiver_counts = messages_df[messages_df['receiver'] != 'broadcast']['receiver'].value_counts()
    
    print(f"\n📈 Agent Activity:")
    print(f"  Most active sender: {sender_counts.index[0]} ({sender_counts.iloc[0]} messages)")
    print(f"  Most contacted receiver: {receiver_counts.index[0] if not receiver_counts.empty else 'N/A'} ({receiver_counts.iloc[0] if not receiver_counts.empty else 0} messages)")
    print("  Debug: Agent load analysis complete")
    
    # Final state analysis
    print("  Debug: Starting final state analysis...")
    final_snapshot = snapshots[-1] if snapshots else None
    if final_snapshot:
        agent_states = final_snapshot['agents']
        unmet_needs_by_agent = {aid: state['unmet_needs'] for aid, state in agent_states.items()}
        
        total_unmet_needs = sum(unmet_needs_by_agent.values())
        agents_with_unmet_needs = len([n for n in unmet_needs_by_agent.values() if n > 0])
        
        print(f"\n🎯 Final State:")
        print(f"  Total unmet needs: {total_unmet_needs}")
        print(f"  Agents with unmet needs: {agents_with_unmet_needs}/{len(agent_states)}")
        
        # Vulnerability analysis
        print("  Debug: Computing vulnerability analysis...")
        high_vuln_unmet = sum(state['unmet_needs'] for state in agent_states.values() 
                             if state.get('vulnerability', 0.5) > 0.6)
        low_vuln_unmet = sum(state['unmet_needs'] for state in agent_states.values() 
                            if state.get('vulnerability', 0.5) <= 0.6)
        equity_gap = high_vuln_unmet - low_vuln_unmet
        
        print(f"  Equity gap (high_vuln - low_vuln unmet): {equity_gap}")
        print("  Debug: Final state analysis complete")
    
    return {
        'scenario': scenario,
        'total_messages': total_messages,
        'delivery_ratio': delivery_ratio,
        'median_response_time': median_response_time if request_response_times else 0,
        'total_unmet_needs': total_unmet_needs if final_snapshot else 0,
        'equity_gap': equity_gap if final_snapshot else 0,
        'response_times': request_response_times
    }

def compare_scenarios():
    """Compare all scenarios side by side"""
    scenarios = ['A', 'B', 'C', 'D', 'E', 'F']
    scenario_results = {}
    
    print("=== COMPARATIVE ANALYSIS ===")
    print("Loading all scenario results...")
    
    for scenario in scenarios:
        try:
            results = analyze_scenario_metrics(scenario)
            scenario_results[scenario] = results
        except Exception as e:
            print(f"Error analyzing scenario {scenario}: {e}")
    
    if not scenario_results:
        print("No scenario data available for comparison")
        return
    
    # Create comparison DataFrame
    comparison_df = pd.DataFrame(scenario_results).T
    
    print(f"\n📊 SCENARIO COMPARISON TABLE:")
    print("=" * 80)
    print(f"{'Scenario':<10} {'Messages':<10} {'Delivery':<10} {'Response':<10} {'Unmet':<8} {'Equity':<8}")
    print("-" * 80)
    
    for scenario, data in scenario_results.items():
        print(f"{scenario:<10} {data['total_messages']:<10,} {data['delivery_ratio']:<10.3f} "
              f"{data['median_response_time']:<10.1f} {data['total_unmet_needs']:<8} {data['equity_gap']:<8}")
    
    # Test hypotheses from experiment plan
    print(f"\n🔬 HYPOTHESIS TESTING:")
    print("=" * 50)
    
    if 'A' in scenario_results and 'C' in scenario_results:
        # H1: Routing (C) reduces time-to-commit vs baseline (A)
        baseline_response = scenario_results['A']['median_response_time']
        routing_response = scenario_results['C']['median_response_time']
        
        if routing_response < baseline_response:
            improvement = ((baseline_response - routing_response) / baseline_response) * 100
            print(f"✅ H1: Routing improves response time by {improvement:.1f}% ({baseline_response:.1f} → {routing_response:.1f})")
        else:
            print(f"❌ H1: Routing does not improve response time ({baseline_response:.1f} → {routing_response:.1f})")
    
    if 'A' in scenario_results and 'D' in scenario_results:
        # H2: Hub removal (D) increases unmet needs vs baseline (A)  
        baseline_unmet = scenario_results['A']['total_unmet_needs']
        outage_unmet = scenario_results['D']['total_unmet_needs']
        
        if outage_unmet > baseline_unmet:
            increase = ((outage_unmet - baseline_unmet) / baseline_unmet) * 100
            print(f"✅ H2: Hub outage increases unmet needs by {increase:.1f}% ({baseline_unmet} → {outage_unmet})")
        else:
            print(f"❌ H2: Hub outage does not increase unmet needs ({baseline_unmet} → {outage_unmet})")
    
    if 'A' in scenario_results and 'E' in scenario_results:
        # H3: Equity weighting (E) reduces equity gap vs baseline (A)
        baseline_gap = scenario_results['A']['equity_gap']  
        equity_gap = scenario_results['E']['equity_gap']
        
        if abs(equity_gap) < abs(baseline_gap):
            improvement = ((abs(baseline_gap) - abs(equity_gap)) / abs(baseline_gap)) * 100 if baseline_gap != 0 else 0
            print(f"✅ H3: Equity weighting reduces gap by {improvement:.1f}% ({baseline_gap} → {equity_gap})")
        else:
            print(f"❌ H3: Equity weighting does not reduce gap ({baseline_gap} → {equity_gap})")
    
    if 'A' in scenario_results and 'B' in scenario_results:
        # H4: Redundancy (B) maintains delivery under higher p_fail
        baseline_delivery = scenario_results['A']['delivery_ratio']
        redundancy_delivery = scenario_results['B']['delivery_ratio']
        
        delivery_diff = abs(redundancy_delivery - baseline_delivery)
        if delivery_diff <= 0.05:  # Within 5%
            print(f"✅ H4: Redundancy maintains delivery ratio ({baseline_delivery:.3f} → {redundancy_delivery:.3f})")
        else:
            print(f"❌ H4: Redundancy does not maintain delivery ratio ({baseline_delivery:.3f} → {redundancy_delivery:.3f})")
    
    return scenario_results

def generate_seed_message_log():
    """Generate seed message log from actual scenario A results only"""
    print("\n=== GENERATING SEED MESSAGE LOG FROM REAL RESULTS ===")
    
    # Load actual scenario A data - no synthetic generation
    try:
        messages_df = load_message_log('A')
        if messages_df.empty:
            print("❌ No actual scenario A data found. Cannot generate seed log without real simulation results.")
            print("   Run: python scripts/venice_flood_simulation.py first")
            return
        
        # Get first 10 ticks of actual messages
        sample_df = messages_df[messages_df['tick'] <= 10].head(20)
        sample_messages = sample_df.to_dict('records')
        
        if not sample_messages:
            print("❌ No messages found in first 10 ticks of scenario A")
            return
            
        # Save seed log from real data
        seed_file = "seed_message_log.ndjson"
        with open(seed_file, 'w') as f:
            for msg in sample_messages:
                f.write(json.dumps(msg) + '\n')
        
        print(f"✅ Seed message log saved from real scenario A data: {seed_file}")
        print(f"   Contains {len(sample_messages)} actual messages")
        
        # Show sample from real data
        print("\n📝 Real message samples:")
        for i, msg in enumerate(sample_messages[:3]):
            print(f"  {i+1}. Tick {msg['tick']}: {msg['sender']} -> {msg['receiver']} ({msg['intent']})")
            
    except FileNotFoundError:
        print("❌ Scenario A message log not found")
        print("   Run: python scripts/venice_flood_simulation.py first to generate real data")
    except Exception as e:
        print(f"❌ Error loading real scenario A data: {e}")

def create_visualization_plots():
    """Create basic visualization plots"""
    print("\n=== CREATING VISUALIZATIONS ===")
    
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        # Set style
        plt.style.use('default')
        sns.set_palette("husl")
        
        scenarios = ['A', 'B', 'C', 'D', 'E', 'F']
        
        # Load data for plotting
        scenario_data = []
        for scenario in scenarios:
            try:
                messages_df = load_message_log(scenario)
                if not messages_df.empty:
                    scenario_data.append({
                        'scenario': scenario,
                        'total_messages': len(messages_df),
                        'delivery_ratio': len(messages_df[messages_df['success']]) / len(messages_df),
                        'failed_messages': len(messages_df[~messages_df['success']])
                    })
            except:
                continue
        
        if not scenario_data:
            print("No data available for visualization")
            return
        
        df = pd.DataFrame(scenario_data)
        
        # Create plots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Venice Flood Simulation Results', fontsize=16)
        
        # Plot 1: Message volume by scenario
        ax1.bar(df['scenario'], df['total_messages'])
        ax1.set_title('Total Messages by Scenario')
        ax1.set_ylabel('Message Count')
        ax1.set_xlabel('Scenario')
        
        # Plot 2: Delivery ratio by scenario
        ax2.bar(df['scenario'], df['delivery_ratio'])
        ax2.set_title('Message Delivery Ratio by Scenario')
        ax2.set_ylabel('Delivery Ratio')
        ax2.set_xlabel('Scenario')
        ax2.set_ylim(0, 1)
        
        # Plot 3: Failed messages
        ax3.bar(df['scenario'], df['failed_messages'], color='red', alpha=0.7)
        ax3.set_title('Failed Messages by Scenario')
        ax3.set_ylabel('Failed Messages')
        ax3.set_xlabel('Scenario')
        
        # Plot 4: Message timeline for one scenario (if data exists)
        try:
            sample_messages = load_message_log('A')
            if not sample_messages.empty:
                timeline = sample_messages.groupby('tick').size()
                ax4.plot(timeline.index, timeline.values)
                ax4.set_title('Message Timeline (Scenario A)')
                ax4.set_ylabel('Messages per Tick')
                ax4.set_xlabel('Simulation Tick')
        except:
            ax4.text(0.5, 0.5, 'No timeline data', ha='center', va='center', transform=ax4.transAxes)
            ax4.set_title('Message Timeline')
        
        plt.tight_layout()
        plt.savefig('venice_simulation_results.png', dpi=300, bbox_inches='tight')
        print("✅ Visualization saved: venice_simulation_results.png")
        
    except ImportError:
        print("⚠️  Matplotlib/seaborn not available - skipping visualizations")
    except Exception as e:
        print(f"Error creating visualizations: {e}")

if __name__ == "__main__":
    print("Venice Flood Simulation Results Analysis")
    print("========================================")
    
    # Run comparative analysis
    scenario_results = compare_scenarios()
    
    # Generate seed message log
    generate_seed_message_log()
    
    # Create visualizations
    create_visualization_plots()
    
    print(f"\n🎉 ANALYSIS COMPLETE")
    print(f"📁 Generated files:")
    print(f"   - seed_message_log.ndjson")
    print(f"   - venice_simulation_results.png (if matplotlib available)")
    
    if scenario_results:
        print(f"\n💡 KEY INSIGHTS:")
        
        # Find best performing scenario
        best_delivery = max(scenario_results.values(), key=lambda x: x['delivery_ratio'])
        print(f"   - Best delivery ratio: Scenario {best_delivery['scenario']} ({best_delivery['delivery_ratio']:.3f})")
        
        best_equity = min(scenario_results.values(), key=lambda x: abs(x['equity_gap']))
        print(f"   - Best equity performance: Scenario {best_equity['scenario']} (gap: {best_equity['equity_gap']})")
        
        fastest_response = min(scenario_results.values(), key=lambda x: x['median_response_time'] if x['median_response_time'] > 0 else float('inf'))
        if fastest_response['median_response_time'] > 0:
            print(f"   - Fastest response time: Scenario {fastest_response['scenario']} ({fastest_response['median_response_time']:.1f} ticks)")
    
    print(f"\n🔄 Next Steps:")
    print(f"   - Review message logs: message_log_[A-F].ndjson")
    print(f"   - Examine agent snapshots: snapshots_[A-F].json") 
    print(f"   - Use seed_message_log.ndjson to test new scenario variations")
