#!/usr/bin/env python3
"""
Emergent Venice Flood Simulation - Discovering Natural Communication Patterns
No predefined coordination - let agents develop their own strategies
"""

import json
import random
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger
import sys
from datetime import datetime

@dataclass
class EmergentMessage:
    """Basic message structure - minimal constraints"""
    sender: str
    receiver: str  # agent_id or 'broadcast'
    tick: int
    content: Dict[str, Any]  # Completely open content
    success: bool = True
    
    def to_dict(self):
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'tick': self.tick,
            'content': self.content,
            'success': self.success
        }

class EmergentVeniceAgent:
    """Venice agent with minimal predefined behavior - let strategies emerge"""
    
    def __init__(self, agent_data: Dict[str, Any]):
        # Basic identity (from real Venice data)
        self.agent_id = agent_data['agent_id']
        self.place_name = agent_data['place_name']
        self.coordinates = agent_data['coordinates']
        self.sector = agent_data['sector']
        self.vulnerability = agent_data['vulnerability']
        self.exposure = agent_data['exposure']
        self.capabilities = agent_data['capabilities']
        self.needs = agent_data['needs']
        
        # Emergent state (starts minimal, develops through interaction)
        self.status = 'normal'
        self.message_history = []
        self.known_agents = {}  # Discovered through communication
        self.trust_network = {}  # Develops based on successful interactions
        self.communication_strategy = {}  # Emerges through trial and error
        self.current_concerns = []
        self.successful_partnerships = []
        
        # Learning parameters (start neutral, adapt based on experience)
        self.response_eagerness = 0.5  # How quickly to respond to requests
        self.broadcast_tendency = 0.3   # How often to broadcast vs direct message
        self.trust_threshold = 0.5      # How much trust needed to accept help
        self.help_willingness = 0.7     # Base willingness to help others
        
    def sense_environment(self, flood_stage: int, tick: int) -> Dict[str, Any]:
        """Sense current conditions and determine internal state"""
        
        # Basic flood impact assessment
        flood_impact = 0.0
        if flood_stage >= 1:
            flood_impact += 0.2 * self.exposure
        if flood_stage >= 2:
            flood_impact += 0.3 * self.vulnerability
        if flood_stage >= 3:
            flood_impact += 0.5
            
        # Determine status based on impact
        if flood_impact < 0.3:
            self.status = 'monitoring'
        elif flood_impact < 0.6:
            self.status = 'concerned'
        elif flood_impact < 0.8:
            self.status = 'stressed'
        else:
            self.status = 'crisis'
        
        # Update concerns based on needs and flood stage
        self.current_concerns = []
        for need in self.needs:
            if flood_stage >= 2 or (flood_stage >= 1 and self.vulnerability > 0.6):
                concern_level = min(1.0, flood_impact + random.uniform(-0.1, 0.1))
                if concern_level > 0.4:
                    self.current_concerns.append({
                        'need': need,
                        'urgency': concern_level,
                        'discovered_at': tick
                    })
        
        return {
            'status': self.status,
            'flood_impact': flood_impact,
            'concerns': self.current_concerns
        }
    
    def decide_communication(self, sensing_result: Dict, all_agents: Dict, tick: int) -> List[EmergentMessage]:
        """Decide what to communicate - no predefined rules"""
        messages = []
        
        # Adaptive communication based on learned experience
        should_broadcast = random.random() < self.broadcast_tendency
        
        # Status sharing - frequency adapts based on situation and experience
        status_changed = len(self.current_concerns) > 0
        if status_changed and should_broadcast:
            # Broadcast status to discover who's listening
            msg = EmergentMessage(
                sender=self.agent_id,
                receiver='broadcast',
                tick=tick,
                content={
                    'type': 'status_share',
                    'place_name': self.place_name,
                    'status': self.status,
                    'concerns': [c['need'] for c in self.current_concerns],
                    'capabilities': self.capabilities,
                    'sector': self.sector,
                    'coordinates': self.coordinates
                }
            )
            messages.append(msg)
        
        # Direct help requests - targeting adapts based on learned trust network
        urgent_concerns = [c for c in self.current_concerns if c['urgency'] > 0.7]
        for concern in urgent_concerns[:2]:  # Limit concurrent requests
            
            # Choose target based on learned network or discovery
            potential_helpers = []
            
            # First try known successful partners
            for partner_id, trust_score in self.trust_network.items():
                if trust_score > self.trust_threshold:
                    potential_helpers.append(partner_id)
            
            # If no trusted partners, try discovery
            if not potential_helpers:
                # Pick agents from different sectors for diversity
                other_sectors = [aid for aid, agent in all_agents.items() 
                               if aid != self.agent_id and agent.sector != self.sector]
                potential_helpers = random.sample(other_sectors, min(3, len(other_sectors)))
            
            # Send help request
            for helper_id in potential_helpers[:2]:
                msg = EmergentMessage(
                    sender=self.agent_id,
                    receiver=helper_id,
                    tick=tick,
                    content={
                        'type': 'help_request',
                        'need': concern['need'],
                        'urgency': concern['urgency'],
                        'place_name': self.place_name,
                        'reason': f"flood_impact_stage_{sensing_result.get('flood_impact', 0):.1f}",
                        'can_reciprocate': self.capabilities
                    }
                )
                messages.append(msg)
        
        return messages
    
    def process_incoming_message(self, message: EmergentMessage, all_agents: Dict, tick: int) -> Optional[EmergentMessage]:
        """Process incoming message and potentially respond"""
        
        sender_id = message.sender
        content = message.content
        msg_type = content.get('type', 'unknown')
        
        # Learn about other agents from their messages
        if sender_id not in self.known_agents:
            self.known_agents[sender_id] = {
                'discovered_at': tick,
                'messages_received': 0,
                'last_interaction': tick
            }
        
        self.known_agents[sender_id]['messages_received'] += 1
        self.known_agents[sender_id]['last_interaction'] = tick
        
        response = None
        
        if msg_type == 'status_share':
            # Learn about other agent's capabilities and situation
            sender_capabilities = content.get('capabilities', [])
            sender_concerns = content.get('concerns', [])
            
            # Decide if we can/should help based on our willingness and capability
            can_help = any(cap in self.capabilities for cap in sender_concerns)
            
            if can_help and random.random() < self.help_willingness:
                # Proactively offer help
                relevant_capabilities = [cap for cap in self.capabilities 
                                       if any(need in cap.lower() for need in sender_concerns)]
                
                response = EmergentMessage(
                    sender=self.agent_id,
                    receiver=sender_id,
                    tick=tick,
                    content={
                        'type': 'offer_help',
                        'offered_capabilities': relevant_capabilities,
                        'availability': self.status,
                        'place_name': self.place_name,
                        'conditions': 'none' if self.status == 'monitoring' else 'limited'
                    }
                )
        
        elif msg_type == 'help_request':
            need = content.get('need', '')
            urgency = content.get('urgency', 0.5)
            
            # Decide whether to help based on capability, willingness, and own status
            can_provide = need.lower() in ' '.join(self.capabilities).lower()
            should_help = random.random() < (self.help_willingness * urgency)
            not_too_busy = self.status in ['monitoring', 'concerned']
            
            if can_provide and should_help and not_too_busy:
                # Accept help request
                response = EmergentMessage(
                    sender=self.agent_id,
                    receiver=sender_id,
                    tick=tick,
                    content={
                        'type': 'help_accept',
                        'for_need': need,
                        'response_time': random.randint(1, 5),
                        'capabilities': self.capabilities,
                        'place_name': self.place_name,
                        'commitment_level': 'full' if self.status == 'monitoring' else 'partial'
                    }
                )
                
                # Update trust network positively for this agent
                self.trust_network[sender_id] = self.trust_network.get(sender_id, 0.5) + 0.1
                self.successful_partnerships.append({
                    'partner': sender_id,
                    'need': need,
                    'tick': tick
                })
                
            else:
                # Decline help request with reason
                reason = 'no_capability' if not can_provide else 'currently_busy'
                response = EmergentMessage(
                    sender=self.agent_id,
                    receiver=sender_id,
                    tick=tick,
                    content={
                        'type': 'help_decline',
                        'for_need': need,
                        'reason': reason,
                        'alternative_suggestion': self.suggest_alternative_helper(need, all_agents),
                        'place_name': self.place_name
                    }
                )
        
        elif msg_type == 'help_accept':
            # Someone accepted our request - update trust and remove concern
            need = content.get('for_need', '')
            self.current_concerns = [c for c in self.current_concerns if c['need'] != need]
            
            # Increase trust in this helper
            self.trust_network[sender_id] = self.trust_network.get(sender_id, 0.5) + 0.2
            
            # Adapt communication strategy - this type of request worked
            if 'successful_requests' not in self.communication_strategy:
                self.communication_strategy['successful_requests'] = []
            self.communication_strategy['successful_requests'].append({
                'partner_sector': all_agents[sender_id].sector,
                'need_type': need,
                'tick': tick
            })
        
        elif msg_type == 'help_decline':
            # Request was declined - adapt strategy
            reason = content.get('reason', 'unknown')
            alternative = content.get('alternative_suggestion', None)
            
            # Decrease trust slightly
            self.trust_network[sender_id] = self.trust_network.get(sender_id, 0.5) - 0.05
            
            # Learn from the alternative suggestion
            if alternative:
                self.broadcast_tendency += 0.05  # Try broadcasting next time
        
        return response
    
    def suggest_alternative_helper(self, need: str, all_agents: Dict) -> Optional[str]:
        """Suggest alternative helper based on observed network"""
        
        # Look for agents we've seen help with similar needs
        for partnership in self.successful_partnerships:
            if partnership['need'] == need:
                return partnership['partner']
        
        # Otherwise suggest random agent from different sector
        other_sectors = [aid for aid, agent in all_agents.items() 
                        if aid != self.agent_id and agent.sector != self.sector]
        
        return random.choice(other_sectors) if other_sectors else None
    
    def adapt_behavior(self, tick: int):
        """Adapt behavior based on experience"""
        
        # Adjust communication strategy based on success rate
        recent_interactions = [
            interaction for interaction in self.successful_partnerships
            if tick - interaction['tick'] < 20  # Recent memory window
        ]
        
        if len(recent_interactions) > 2:
            # Successful partnerships - become more trusting and helpful
            self.help_willingness = min(0.9, self.help_willingness + 0.05)
            self.trust_threshold = max(0.3, self.trust_threshold - 0.05)
        elif len(recent_interactions) == 0 and len(self.current_concerns) > 1:
            # No successful partnerships but still have concerns - try broadcasting more
            self.broadcast_tendency = min(0.8, self.broadcast_tendency + 0.1)
            self.response_eagerness = min(0.9, self.response_eagerness + 0.1)

class EmergentFloodSimulation:
    """Simulation engine for discovering emergent coordination patterns"""
    
    def __init__(self, agents_file: str = "venice_agents.ndjson"):
        self.setup_logging()
        self.agents = {}
        self.load_agents(agents_file)
        self.message_log = []
        self.current_tick = 0
        self.flood_stage = 0
        
        logger.info(f"EmergentFloodSimulation initialized with {len(self.agents)} agents")
    
    def setup_logging(self):
        """Setup logging for emergent behavior discovery"""
        logger.remove()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Console logging
        logger.add(sys.stderr, 
                  format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}",
                  level="INFO")
        
        # File logging for detailed analysis
        Path("logs").mkdir(exist_ok=True)
        logger.add(f"logs/emergent_{timestamp}.log",
                  format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
                  level="DEBUG")
    
    def load_agents(self, agents_file: str):
        """Load Venice agents for emergent simulation"""
        with open(agents_file, 'r') as f:
            for line in f:
                agent_data = json.loads(line)
                agent = EmergentVeniceAgent(agent_data)
                self.agents[agent.agent_id] = agent
        
        logger.info(f"Loaded {len(self.agents)} agents for emergent discovery")
    
    def discover_coordination_patterns(self, experiment_name: str, 
                                     max_ticks: int = 120,
                                     flood_scenario: str = 'gradual',
                                     message_reliability: float = 0.9,
                                     agent_sample_size: int = None):
        """Run open-ended simulation to discover natural coordination patterns"""
        
        logger.info(f"Starting emergent discovery: {experiment_name}")
        logger.info(f"Parameters: flood={flood_scenario}, reliability={message_reliability}")
        
        # Reset all agents to neutral state
        for agent in self.agents.values():
            agent.status = 'normal'
            agent.message_history = []
            agent.current_concerns = []
            agent.known_agents = {}
            agent.trust_network = {}
            agent.communication_strategy = {}
        
        self.message_log = []
        self.current_tick = 0
        
        # Define flood progression scenarios
        flood_progressions = {
            'gradual': [0] * 40 + [1] * 30 + [2] * 30 + [3] * 20,
            'sudden': [0] * 20 + [2] * 40 + [3] * 60,
            'oscillating': [0, 1, 0, 1, 2, 1, 2, 3, 2, 3] * 12,
            'static_high': [3] * max_ticks
        }
        
        flood_progression = flood_progressions.get(flood_scenario, flood_progressions['gradual'])
        
        # Track emergent patterns
        communication_patterns = {
            'broadcast_adoption': {},      # How broadcast usage changes
            'network_formation': {},       # How agent networks develop
            'strategy_evolution': {},      # How strategies adapt
            'coordination_emergence': {}   # How coordination develops
        }
        
        for tick in range(max_ticks):
            self.current_tick = tick
            
            # Update flood stage
            if tick < len(flood_progression):
                old_stage = self.flood_stage
                self.flood_stage = flood_progression[tick]
                if self.flood_stage != old_stage:
                    logger.info(f"Tick {tick}: Flood stage changed {old_stage} → {self.flood_stage}")
            
            # Select active agents (sample if specified)
            active_agents = list(self.agents.keys())
            if agent_sample_size:
                active_agents = random.sample(active_agents, min(agent_sample_size, len(active_agents)))
            
            tick_messages = []
            
            # Phase 1: Each agent senses and decides independently
            for agent_id in active_agents:
                agent = self.agents[agent_id]
                
                # Agent senses environment
                sensing = agent.sense_environment(self.flood_stage, tick)
                
                # Agent decides what to communicate (no constraints)
                outgoing_messages = agent.decide_communication(sensing, self.agents, tick)
                
                # Send messages with reliability factor
                for msg in outgoing_messages:
                    if random.random() < message_reliability:
                        msg.success = True
                        tick_messages.append(msg)
                    else:
                        msg.success = False
                        tick_messages.append(msg)
                
                # Log significant agent state changes
                if len(agent.current_concerns) > 0:
                    logger.debug(f"Agent {agent_id} ({agent.place_name}) concerns: {[c['need'] for c in agent.current_concerns]}")
            
            # Phase 2: Deliver successful messages and generate responses
            successful_messages = [msg for msg in tick_messages if msg.success]
            
            for msg in successful_messages:
                if msg.receiver == 'broadcast':
                    # Broadcast to all agents except sender
                    for agent_id, agent in self.agents.items():
                        if agent_id != msg.sender:
                            response = agent.process_incoming_message(msg, self.agents, tick)
                            if response:
                                if random.random() < message_reliability:
                                    response.success = True
                                    tick_messages.append(response)
                                else:
                                    response.success = False
                                    tick_messages.append(response)
                else:
                    # Direct message
                    if msg.receiver in self.agents:
                        receiver = self.agents[msg.receiver]
                        response = receiver.process_incoming_message(msg, self.agents, tick)
                        if response:
                            if random.random() < message_reliability:
                                response.success = True
                                tick_messages.append(response)
                            else:
                                response.success = False
                                tick_messages.append(response)
            
            # Phase 3: Agents adapt based on interaction outcomes
            for agent_id in active_agents:
                self.agents[agent_id].adapt_behavior(tick)
            
            # Record all messages for this tick
            self.message_log.extend(tick_messages)
            
            # Track emergent patterns
            if tick % 10 == 0:
                self.track_emergent_patterns(tick, communication_patterns)
                logger.info(f"Tick {tick}: {len(tick_messages)} messages, flood_stage={self.flood_stage}")
        
        logger.info(f"Experiment {experiment_name} complete: {len(self.message_log)} total messages")
        
        # Save results
        self.save_emergent_results(experiment_name, communication_patterns)
        
        return self.analyze_emergent_patterns(communication_patterns)
    
    def track_emergent_patterns(self, tick: int, patterns: Dict):
        """Track how communication patterns emerge and evolve"""
        
        # Track broadcast adoption rates
        recent_messages = [msg for msg in self.message_log if msg.tick >= tick - 10]
        broadcast_ratio = len([msg for msg in recent_messages if msg.receiver == 'broadcast']) / max(1, len(recent_messages))
        patterns['broadcast_adoption'][tick] = broadcast_ratio
        
        # Track network density (how connected agents become)
        connections = set()
        for msg in recent_messages:
            if msg.receiver != 'broadcast':
                connections.add((msg.sender, msg.receiver))
        
        network_density = len(connections) / max(1, len(self.agents) * (len(self.agents) - 1) / 2)
        patterns['network_formation'][tick] = network_density
        
        # Track strategy diversity
        help_request_types = set()
        for msg in recent_messages:
            if msg.content.get('type') == 'help_request':
                help_request_types.add(msg.content.get('need', 'unknown'))
        
        patterns['strategy_evolution'][tick] = len(help_request_types)
    
    def analyze_emergent_patterns(self, patterns: Dict) -> Dict[str, Any]:
        """Analyze what coordination patterns emerged naturally"""
        
        results = {
            'total_messages': len(self.message_log),
            'successful_messages': len([msg for msg in self.message_log if msg.success]),
            'emergent_patterns': {}
        }
        
        # Analyze message type evolution
        message_types = {}
        for msg in self.message_log:
            msg_type = msg.content.get('type', 'unknown')
            message_types[msg_type] = message_types.get(msg_type, 0) + 1
        
        results['emergent_patterns']['communication_types'] = message_types
        
        # Analyze network formation
        final_networks = {}
        for agent_id, agent in self.agents.items():
            final_networks[agent_id] = {
                'known_agents': len(agent.known_agents),
                'trust_network_size': len(agent.trust_network),
                'successful_partnerships': len(agent.successful_partnerships),
                'final_broadcast_tendency': agent.broadcast_tendency,
                'final_help_willingness': agent.help_willingness
            }
        
        results['emergent_patterns']['network_evolution'] = final_networks
        
        # Analyze coordination success
        help_requests = [msg for msg in self.message_log if msg.content.get('type') == 'help_request']
        help_accepts = [msg for msg in self.message_log if msg.content.get('type') == 'help_accept']
        
        coordination_success_rate = len(help_accepts) / max(1, len(help_requests))
        results['emergent_patterns']['coordination_success_rate'] = coordination_success_rate
        
        return results
    
    def save_emergent_results(self, experiment_name: str, patterns: Dict):
        """Save results for analysis"""
        
        # Save message log
        log_file = f"emergent_log_{experiment_name}.ndjson"
        with open(log_file, 'w') as f:
            for msg in self.message_log:
                f.write(json.dumps(msg.to_dict()) + '\n')
        
        # Save emergent patterns
        patterns_file = f"emergent_patterns_{experiment_name}.json"
        with open(patterns_file, 'w') as f:
            json.dump(patterns, f, indent=2)
        
        # Save final agent states
        final_states = {}
        for agent_id, agent in self.agents.items():
            final_states[agent_id] = {
                'place_name': agent.place_name,
                'final_status': agent.status,
                'concerns_remaining': len(agent.current_concerns),
                'network_size': len(agent.known_agents),
                'trust_network': agent.trust_network,
                'communication_adaptations': {
                    'broadcast_tendency': agent.broadcast_tendency,
                    'help_willingness': agent.help_willingness,
                    'trust_threshold': agent.trust_threshold
                },
                'partnerships_formed': len(agent.successful_partnerships)
            }
        
        states_file = f"emergent_agent_states_{experiment_name}.json"
        with open(states_file, 'w') as f:
            json.dump(final_states, f, indent=2)
        
        logger.info(f"Emergent results saved: {log_file}, {patterns_file}, {states_file}")

def run_emergent_discovery_experiments():
    """Run multiple experiments to discover natural coordination patterns"""
    
    print("Venice Emergent Coordination Discovery")
    print("=====================================")
    
    sim = EmergentFloodSimulation()
    results = {}
    
    # Experiment 1: Gradual flood with high reliability
    results['gradual_reliable'] = sim.discover_coordination_patterns(
        'gradual_reliable',
        flood_scenario='gradual',
        message_reliability=0.9,
        max_ticks=120
    )
    
    # Experiment 2: Sudden flood with high reliability
    results['sudden_reliable'] = sim.discover_coordination_patterns(
        'sudden_reliable', 
        flood_scenario='sudden',
        message_reliability=0.9,
        max_ticks=120
    )
    
    # Experiment 3: Gradual flood with low reliability (test uncertainty)
    results['gradual_unreliable'] = sim.discover_coordination_patterns(
        'gradual_unreliable',
        flood_scenario='gradual', 
        message_reliability=0.7,
        max_ticks=120
    )
    
    # Experiment 4: Oscillating flood (test adaptation)
    results['oscillating'] = sim.discover_coordination_patterns(
        'oscillating',
        flood_scenario='oscillating',
        message_reliability=0.85,
        max_ticks=120
    )
    
    # Compare results
    print("\n=== EMERGENT PATTERN COMPARISON ===")
    for exp_name, data in results.items():
        coord_rate = data['emergent_patterns']['coordination_success_rate']
        comm_types = len(data['emergent_patterns']['communication_types'])
        print(f"{exp_name:<20} Coordination: {coord_rate:.2f} | Message types: {comm_types}")
    
    return results

if __name__ == "__main__":
    run_emergent_discovery_experiments()
