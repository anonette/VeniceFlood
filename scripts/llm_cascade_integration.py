#!/usr/bin/env python3
"""
LLM-Enhanced Multi-Hazard Cascade Simulation
Combines structured cascade analysis with LLM-generated natural language content
"""

import json
import random
import copy
import os
from dataclasses import dataclass
from typing import List, Dict, Any, Set
from pathlib import Path
from loguru import logger
import sys
from datetime import datetime
import numpy as np
from enum import Enum
import openai
from dotenv import load_dotenv

# Import base frameworks
from fixed_cascade_scenarios import FixedMultiHazardSimulation, CascadeEvent, HazardType
from llm_enhanced_simulation import LLMMessageGenerator, EnhancedMessage, EnhancedVeniceAgent

# Load environment variables
load_dotenv(dotenv_path='.env')

class LLMCascadeSimulation(FixedMultiHazardSimulation):
    """Cascade simulation enhanced with LLM-generated message content"""
    
    def __init__(self, agents_file: str = "venice_agents.ndjson", log_level: str = "INFO"):
        # Initialize base cascade simulation
        super().__init__(agents_file, log_level)
        
        # Add LLM capabilities
        self.llm_generator = LLMMessageGenerator() if os.getenv('OPENAI_API_KEY') else None
        self.enhanced_message_log = []  # Store LLM-enhanced messages
        self.communication_patterns = {}  # Track communication analytics
        
        # Convert agents to enhanced agents
        self.convert_to_enhanced_agents()
        
        logger.info(f"LLMCascadeSimulation initialized with LLM: {bool(self.llm_generator)}")
    
    def convert_to_enhanced_agents(self):
        """Convert existing agents to enhanced agents with LLM capabilities"""
        enhanced_agents = {}
        
        for agent_id, agent in self.agents.items():
            # Convert VeniceAgent to enhanced agent data
            agent_data = {
                'agent_id': agent.agent_id,
                'place_name': agent.place_name,
                'coordinates': agent.coordinates,
                'sector': agent.sector,
                'asset_type': agent.asset_type,
                'priority_score': agent.priority_score,
                'vulnerability': agent.vulnerability,
                'exposure': agent.exposure,
                'capabilities': agent.capabilities,
                'needs': agent.needs,
                'risk_escalation': agent.risk_escalation,
                'comm_prefs': agent.comm_prefs,
                'initial_status': agent.status
            }
            
            enhanced_agent = EnhancedVeniceAgent(agent_data)
            
            # Add missing methods from original VeniceAgent
            enhanced_agent.get_current_status = lambda flood_stage, agent=enhanced_agent: agent.risk_escalation.get(f'stage_{flood_stage}', 'emergency')
            enhanced_agent.needs_to_broadcast = lambda current_status, agent=enhanced_agent: self._needs_to_broadcast(agent, current_status)
            enhanced_agent.find_support_partners = lambda all_agents, need, agent=enhanced_agent: self._find_support_partners(agent, all_agents, need)
            enhanced_agent.can_provide_support = lambda need, agent=enhanced_agent: self._can_provide_support(agent, need)
            
            enhanced_agents[agent_id] = enhanced_agent
        
        self.agents = enhanced_agents
    
    def _needs_to_broadcast(self, agent, current_status: str) -> bool:
        """Check if current status warrants broadcasting"""
        threshold = agent.comm_prefs['broadcast_threshold']
        status_levels = ['normal', 'alert', 'critical', 'emergency']
        
        current_level = status_levels.index(current_status) if current_status in status_levels else 3
        threshold_level = status_levels.index(threshold) if threshold in status_levels else 2
        
        return current_level >= threshold_level
    
    def _find_support_partners(self, agent, all_agents: Dict, need: str) -> List[str]:
        """Find agents that might be able to help with a specific need"""
        partners = []
        
        # Simple capability matching
        capability_map = {
            'protection': ['emergency_response', 'security'],
            'drainage': ['pumping', 'emergency_response'],
            'structural_support': ['emergency_response', 'rescue'],
            'power': ['electricity', 'power_distribution'],
            'communication': ['coordination', 'emergency_response'],
            'medical_care': ['medical_care', 'emergency_treatment'],
            'vehicle_access': ['mobility', 'evacuation_route'],
            'water_access': ['pumping', 'emergency_response']
        }
        
        required_caps = capability_map.get(need, [need])
        
        for other_agent in all_agents.values():
            if other_agent.agent_id != agent.agent_id:
                if any(cap in other_agent.capabilities for cap in required_caps):
                    partners.append(other_agent.agent_id)
        
        return partners[:5]  # Limit to top 5 partners
    
    def _can_provide_support(self, agent, need: str) -> bool:
        """Check if this agent can provide the requested support"""
        capability_map = {
            'protection': ['emergency_response', 'security'],
            'drainage': ['pumping', 'emergency_response'],
            'power': ['electricity', 'power_distribution'],
            'medical_care': ['medical_care', 'emergency_treatment'],
            'evacuation': ['evacuation_route', 'mobility']
        }
        
        required_caps = capability_map.get(need, [need])
        return any(cap in agent.capabilities for cap in required_caps)
    
    def generate_cascade_message_with_llm(self, sender_agent, intent: str, target: str, need: str = None):
        """Generate cascade message with LLM content + structured payload"""
        
        if not self.llm_generator:
            # Fallback to structured message without LLM content
            return self.generate_structured_message(sender_agent, intent, target, need)
        
        try:
            # Generate LLM-enhanced message
            enhanced_msg = sender_agent.generate_enhanced_message(
                intent, target, self.current_tick, self.flood_stage, 
                self.llm_generator, need
            )
            
            # Add cascade-specific payload data
            enhanced_msg.payload.update({
                'cascade_context': {
                    'active_events': list(self.active_events),
                    'system_states': copy.deepcopy(self.system_states),
                    'flood_stage': self.flood_stage
                }
            })
            
            return enhanced_msg
            
        except Exception as e:
            logger.warning(f"LLM generation failed for {sender_agent.agent_id}: {e}")
            return self.generate_structured_message(sender_agent, intent, target, need)
    
    def generate_structured_message(self, sender_agent, intent: str, target: str, need: str = None):
        """Generate structured message without LLM (fallback)"""
        
        payload = {
            'agent_type': sender_agent.asset_type,
            'sector': sender_agent.sector,
            'vulnerability': sender_agent.vulnerability,
            'coordinates': sender_agent.coordinates,
            'capabilities': sender_agent.capabilities,
            'status': sender_agent.status,
            'place_name': sender_agent.place_name,
            'cascade_context': {
                'active_events': list(self.active_events),
                'system_states': copy.deepcopy(self.system_states),
                'flood_stage': self.flood_stage
            }
        }
        
        if need:
            payload['need'] = need
        
        # Generate basic content
        content = f"{sender_agent.place_name} {intent}: {sender_agent.status}"
        if need:
            content += f" - requesting {need}"
        
        return EnhancedMessage(
            sender=sender_agent.agent_id,
            receiver=target,
            tick=self.current_tick,
            intent=intent,
            content=content,
            payload=payload
        )
    
    def process_agent_turn_with_llm(self, agent, p_fail: float, equity_weighting: float = 0.0):
        """Process agent turn with LLM-enhanced message generation"""
        
        # Update status based on flood stage
        new_status = agent.get_current_status(self.flood_stage)
        status_changed = new_status != agent.status
        agent.status = new_status
        
        # Generate status update with LLM content
        if status_changed and agent.needs_to_broadcast(new_status):
            msg = self.generate_cascade_message_with_llm(
                agent, 'status_update', 'broadcast'
            )
            self.send_enhanced_cascade_message(msg, p_fail)
        
        # Generate support requests with LLM content
        escalation_delay = 5
        if (self.current_tick - agent.last_update_tick) >= escalation_delay:
            for need in agent.unmet_needs[:2]:  # Limit requests
                partners = agent.find_support_partners(self.agents, need)
                for partner_id in partners[:2]:  # Limit partners
                    msg = self.generate_cascade_message_with_llm(
                        agent, 'request_support', partner_id, need
                    )
                    self.send_enhanced_cascade_message(msg, p_fail)
                    agent.pending_requests.append({
                        'need': need,
                        'partner': partner_id, 
                        'tick': self.current_tick
                    })
            
            agent.last_update_tick = self.current_tick
        
        # Process incoming messages (enhanced)
        priority_queue = sorted(agent.message_queue,
                               key=lambda m: self.get_message_priority(m, equity_weighting),
                               reverse=True)
        
        for message in priority_queue[:10]:
            self.process_enhanced_message(agent, message, p_fail)
        
        agent.message_queue = []
        
        # Update unmet needs
        if new_status in ['critical', 'emergency']:
            base_needs = agent.needs.copy()
            if new_status == 'emergency':
                base_needs.extend(['evacuation', 'emergency_response'])
            
            for need in base_needs:
                if need not in [r['need'] for r in agent.pending_requests]:
                    if need not in agent.unmet_needs:
                        agent.unmet_needs.append(need)
    
    def process_enhanced_message(self, receiver_agent, message, p_fail: float):
        """Process enhanced message with LLM content analysis"""
        
        # Standard cascade processing
        if hasattr(message, 'payload') and message.intent == 'request_support':
            need = message.payload.get('need')
            if receiver_agent.can_provide_support(need):
                commit_probability = 0.7
                
                # Adjust probability based on system state
                if receiver_agent.status == 'emergency':
                    commit_probability *= 0.3
                elif receiver_agent.status == 'critical':
                    commit_probability *= 0.6
                
                if random.random() < commit_probability:
                    response = self.generate_cascade_message_with_llm(
                        receiver_agent, 'commit', message.sender, need
                    )
                else:
                    response = self.generate_cascade_message_with_llm(
                        receiver_agent, 'reject', message.sender, need
                    )
                
                self.send_enhanced_cascade_message(response, p_fail)
        
        elif hasattr(message, 'payload') and message.intent == 'commit':
            need = message.payload.get('need')
            if need in receiver_agent.unmet_needs:
                receiver_agent.unmet_needs.remove(need)
            
            receiver_agent.pending_requests = [
                r for r in receiver_agent.pending_requests
                if not (r['need'] == need and r['partner'] == message.sender)
            ]
        
        # Track communication patterns for analysis
        self.track_communication_pattern(message, receiver_agent)
    
    def track_communication_pattern(self, message, receiver_agent):
        """Track communication patterns for analysis"""
        
        if not hasattr(message, 'content'):
            return
        
        pattern_key = f"{message.payload.get('sector', 'unknown')}_{message.intent}"
        
        if pattern_key not in self.communication_patterns:
            self.communication_patterns[pattern_key] = {
                'messages': [],
                'success_rate': 0,
                'response_times': [],
                'content_analysis': {}
            }
        
        self.communication_patterns[pattern_key]['messages'].append({
            'content': message.content,
            'success': message.success,
            'sender_vulnerability': message.payload.get('vulnerability', 0),
            'tick': message.tick
        })
    
    def send_enhanced_cascade_message(self, message: EnhancedMessage, p_fail: float):
        """Send enhanced message with cascade effects"""
        
        # Apply stochastic failure
        if random.random() < p_fail:
            message.success = False
        
        # Deliver to recipients
        if message.receiver == 'broadcast':
            for agent_id, agent in self.agents.items():
                if agent_id != message.sender:
                    agent.message_queue.append(message)
        else:
            if message.receiver in self.agents:
                self.agents[message.receiver].message_queue.append(message)
            else:
                message.success = False
        
        # Store in both logs
        self.enhanced_message_log.append(message)
        # Also store in regular message log for cascade analysis compatibility
        self.message_log.append(message)
    
    def run_llm_cascade_scenario(self, scenario_name: str, max_ticks: int = 120, **scenario_params):
        """Run cascade scenario with LLM-enhanced messages"""
        
        logger.info(f"Starting LLM-enhanced cascade scenario: {scenario_name}")
        
        # Reset simulation
        self.reset_simulation()
        
        # Create cascade events (same as base framework)
        self.cascade_events = self.create_scenario_events(scenario_name)
        
        logger.info(f"Loaded {len(self.cascade_events)} cascade events for scenario {scenario_name}")
        
        # Run simulation with LLM enhancement
        for tick in range(max_ticks):
            self.current_tick = tick
            
            # Apply cascade events
            events_to_trigger = [e for e in self.cascade_events
                               if e.trigger_tick == tick and e.event_id not in self.active_events]
            
            for event in events_to_trigger:
                self.apply_cascade_effects(event, tick)
                self.active_events.add(event.event_id)
            
            # Remove expired events
            expired_events = [e for e in self.cascade_events
                            if e.trigger_tick + e.duration <= tick and e.event_id in self.active_events]
            
            for event in expired_events:
                self.active_events.remove(event.event_id)
            
            # Update flood stage
            self.update_flood_progression(tick, max_ticks)
            
            # Process agent turns with LLM enhancement
            agent_order = list(self.agents.keys())
            random.shuffle(agent_order)
            
            for agent_id in agent_order:
                agent = self.agents[agent_id]
                p_fail = self.calculate_agent_failure_probability(agent)
                self.process_agent_turn_with_llm(agent, p_fail, scenario_params.get('equity_weighting', 0.0))
            
            # Take snapshot
            self.take_cascade_snapshot()
            
            # Log progress
            if tick % 20 == 0:
                active_events = len(self.active_events)
                total_messages = len([m for m in self.enhanced_message_log if m.tick == tick])
                logger.info(f"Tick {tick}: {active_events} active events, {total_messages} LLM messages")
        
        # Generate results with dual analysis
        results = self.get_llm_cascade_results()
        logger.info(f"LLM cascade scenario {scenario_name} complete: {results['total_enhanced_messages']} enhanced messages")
        
        return results
    
    def get_llm_cascade_results(self) -> Dict[str, Any]:
        """Get results with both cascade and communication analysis"""
        
        # Get base cascade results
        base_results = self.get_cascade_results()
        
        # Add LLM-specific analysis
        enhanced_results = {
            'total_enhanced_messages': len(self.enhanced_message_log),
            'communication_patterns': self.analyze_communication_patterns(),
            'content_effectiveness': self.analyze_content_effectiveness(),
            'place_voice_analysis': self.analyze_place_voices(),
            'llm_cascade_correlation': self.correlate_content_with_cascade_outcomes()
        }
        
        return {**base_results, **enhanced_results}
    
    def analyze_communication_patterns(self) -> Dict[str, Any]:
        """Analyze communication patterns from LLM content"""
        
        analysis = {}
        
        for pattern_key, data in self.communication_patterns.items():
            if data['messages']:
                analysis[pattern_key] = {
                    'message_count': len(data['messages']),
                    'avg_success_rate': np.mean([m['success'] for m in data['messages']]),
                    'sample_content': data['messages'][0]['content'][:100] if data['messages'] else ""
                }
        
        return analysis
    
    def analyze_content_effectiveness(self) -> Dict[str, Any]:
        """Analyze which content types are most effective"""
        
        # Group messages by sector and intent
        by_sector = {}
        for msg in self.enhanced_message_log:
            sector = msg.payload.get('sector', 'unknown')
            if sector not in by_sector:
                by_sector[sector] = {'success': 0, 'total': 0, 'contents': []}
            
            by_sector[sector]['total'] += 1
            if msg.success:
                by_sector[sector]['success'] += 1
            by_sector[sector]['contents'].append(msg.content)
        
        effectiveness = {}
        for sector, data in by_sector.items():
            effectiveness[sector] = {
                'success_rate': data['success'] / data['total'] if data['total'] > 0 else 0,
                'message_count': data['total'],
                'sample_messages': data['contents'][:3]
            }
        
        return effectiveness
    
    def analyze_place_voices(self) -> Dict[str, Any]:
        """Analyze distinct place voice characteristics"""
        
        by_place = {}
        for msg in self.enhanced_message_log:
            place = msg.payload.get('place_name', 'unknown')
            if place not in by_place:
                by_place[place] = []
            by_place[place].append(msg.content)
        
        voice_analysis = {}
        for place, contents in list(by_place.items())[:10]:  # Top 10 places
            voice_analysis[place] = {
                'message_count': len(contents),
                'sample_voice': contents[0] if contents else "",
                'avg_length': np.mean([len(c.split()) for c in contents]) if contents else 0
            }
        
        return voice_analysis
    
    def correlate_content_with_cascade_outcomes(self) -> Dict[str, Any]:
        """Correlate message content with cascade success"""
        
        # Find relationships between content characteristics and outcomes
        heritage_msgs = [m for m in self.enhanced_message_log if m.payload.get('sector') == 'heritage']
        transport_msgs = [m for m in self.enhanced_message_log if m.payload.get('sector') == 'transport']
        
        return {
            'heritage_effectiveness': np.mean([m.success for m in heritage_msgs]) if heritage_msgs else 0,
            'transport_effectiveness': np.mean([m.success for m in transport_msgs]) if transport_msgs else 0,
            'total_sectors_compared': len(set(m.payload.get('sector') for m in self.enhanced_message_log))
        }
    
    def save_llm_cascade_results(self, scenario_name: str):
        """Save enhanced results with both cascade and communication data"""
        
        # Save enhanced message log
        enhanced_log_file = f"llm_cascade_log_{scenario_name}.ndjson"
        with open(enhanced_log_file, 'w') as f:
            for msg in self.enhanced_message_log:
                f.write(json.dumps(msg.to_dict()) + '\n')
        
        # Save communication patterns analysis
        patterns_file = f"communication_patterns_{scenario_name}.json"
        with open(patterns_file, 'w') as f:
            json.dump(self.communication_patterns, f, indent=2)
        
        # Save cascade snapshots (same as base)
        snapshot_file = f"llm_cascade_snapshots_{scenario_name}.json"
        with open(snapshot_file, 'w') as f:
            json.dump(self.tick_snapshots, f, indent=2)
        
        # Save cascade events (same as base)
        events_file = f"llm_cascade_events_{scenario_name}.json"
        with open(events_file, 'w') as f:
            json.dump(self.cascade_log, f, indent=2)
        
        logger.info(f"LLM cascade results saved: {enhanced_log_file}, {patterns_file}")

def run_llm_cascade_demonstration():
    """Run cascade scenarios with LLM enhancement"""
    
    print("=== LLM-ENHANCED CASCADE DEMONSTRATION ===")
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  No OpenAI API key found - will run with structured content only")
        print("   Add OPENAI_API_KEY to .env file for full LLM enhancement")
    else:
        print("✅ OpenAI API key found - enabling LLM content generation")
    
    sim = LLMCascadeSimulation()
    results = {}
    
    scenarios = ["ransomware_flood", "communication_breakdown"]  # Start with 2 scenarios
    
    print(f"Running {len(scenarios)} LLM-enhanced cascade scenarios...")
    
    for scenario in scenarios:
        print(f"\n--- Running LLM-Enhanced {scenario.upper().replace('_', ' ')} ---")
        
        try:
            results[scenario] = sim.run_llm_cascade_scenario(scenario, max_ticks=60)  # Shorter for testing
            sim.save_llm_cascade_results(scenario)
            
            # Print results
            r = results[scenario]
            print(f"  ✅ Complete: {r['total_enhanced_messages']} LLM messages")
            print(f"  📊 Cascade events: {r['total_cascade_events']}")
            print(f"  ⚡ System degradation: {np.mean(list(r['system_degradation'].values())):.2f}")
            print(f"  🗣️ Communication patterns: {len(r['communication_patterns'])} types")
            print(f"  🏛️ Place voices: {len(r['place_voice_analysis'])} places analyzed")
            
            # Show sample LLM content
            if r['place_voice_analysis']:
                sample_place = list(r['place_voice_analysis'].keys())[0]
                sample_voice = r['place_voice_analysis'][sample_place]['sample_voice']
                print(f"  📝 Sample voice ({sample_place}): \"{sample_voice[:80]}...\"")
            
        except Exception as e:
            logger.error(f"Error running LLM scenario {scenario}: {e}")
            results[scenario] = {"error": str(e)}
    
    # Generate comparison report
    generate_llm_cascade_report(results)
    
    return results

def generate_llm_cascade_report(results: Dict[str, Dict]):
    """Generate comprehensive LLM cascade report"""
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'llm_enhanced_analysis': True,
        'scenarios_analyzed': list(results.keys()),
        'cascade_metrics': {},
        'communication_insights': {},
        'stakeholder_applications': {}
    }
    
    # Extract cascade metrics (same as base)
    for scenario, data in results.items():
        if 'error' not in data:
            report['cascade_metrics'][scenario] = {
                'system_degradation': np.mean(list(data.get('system_degradation', {}).values())),
                'infrastructure_resilience': data.get('infrastructure_resilience', 0),
                'cascade_events': data.get('total_cascade_events', 0)
            }
    
    # Extract communication insights (new)
    for scenario, data in results.items():
        if 'error' not in data:
            report['communication_insights'][scenario] = {
                'total_enhanced_messages': data.get('total_enhanced_messages', 0),
                'communication_patterns': len(data.get('communication_patterns', {})),
                'place_voices_analyzed': len(data.get('place_voice_analysis', {})),
                'content_effectiveness': data.get('content_effectiveness', {})
            }
    
    # Save comprehensive report
    with open('LLM_CASCADE_DEMONSTRATION_REPORT.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n=== LLM CASCADE DEMONSTRATION RESULTS ===")
    print(f"✅ Analysis complete: {len([r for r in results.values() if 'error' not in r])} scenarios")
    print(f"📊 Cascade + Communication metrics generated")
    print(f"📝 Report saved: LLM_CASCADE_DEMONSTRATION_REPORT.json")
    
    return report

if __name__ == "__main__":
    print("LLM-Enhanced Venice Cascade Framework")
    print("====================================")
    
    # Run the demonstration
    results = run_llm_cascade_demonstration()
    
    print(f"\n🎉 LLM CASCADE INTEGRATION COMPLETE!")
    print(f"📁 Files generated:")
    for scenario in results.keys():
        if 'error' not in results[scenario]:
            print(f"   - llm_cascade_log_{scenario}.ndjson")
            print(f"   - communication_patterns_{scenario}.json")
    print(f"   - LLM_CASCADE_DEMONSTRATION_REPORT.json")
    
    print(f"\n🔬 DUAL ANALYSIS CAPABILITIES:")
    print(f"   ✅ All cascade metrics (system degradation, vulnerability hierarchy)")
    print(f"   ✅ Communication patterns (place voices, message effectiveness)")
    print(f"   ✅ Content correlation (which communication styles work best)")
    print(f"   ✅ Stakeholder engagement (realistic dialogue for presentations)")