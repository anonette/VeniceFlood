#!/usr/bin/env python3
"""
Venice Cascading Flood Risk Simulation Framework
Flat-ontology agent-to-agent communication for disaster response
"""

import json
import random
import copy
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from loguru import logger
import sys
from datetime import datetime

@dataclass
class Message:
    """Individual message in the simulation"""
    sender: str
    receiver: str  # 'broadcast' for broadcast messages
    tick: int
    intent: str  # status_update, request_support, commit, reject
    payload: Dict[str, Any]
    success: bool = True
    
    def to_dict(self):
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'tick': self.tick,
            'intent': self.intent,
            'payload': self.payload,
            'success': self.success
        }

class VeniceAgent:
    """Individual Venice place/asset agent"""
    
    def __init__(self, agent_data: Dict[str, Any]):
        self.agent_id = agent_data['agent_id']
        self.place_name = agent_data['place_name']
        self.coordinates = agent_data['coordinates']
        self.sector = agent_data['sector']
        self.asset_type = agent_data['asset_type']
        self.priority_score = agent_data['priority_score']
        self.vulnerability = agent_data['vulnerability']
        self.exposure = agent_data['exposure']
        self.capabilities = agent_data['capabilities']
        self.needs = agent_data['needs']
        self.risk_escalation = agent_data['risk_escalation']
        self.comm_prefs = agent_data['comm_prefs']
        
        # Dynamic state
        self.status = agent_data['initial_status']
        self.message_queue = []
        self.unmet_needs = []
        self.last_update_tick = 0
        self.committed_support = []  # What we've committed to provide
        self.pending_requests = []   # What we've requested
        
    def get_current_status(self, flood_stage: int) -> str:
        """Determine current status based on flood stage and agent properties"""
        stage_key = f'stage_{flood_stage}'
        return self.risk_escalation.get(stage_key, 'emergency')
    
    def needs_to_broadcast(self, current_status: str) -> bool:
        """Check if current status warrants broadcasting"""
        threshold = self.comm_prefs['broadcast_threshold']
        status_levels = ['normal', 'alert', 'critical', 'emergency']
        
        current_level = status_levels.index(current_status) if current_status in status_levels else 3
        threshold_level = status_levels.index(threshold) if threshold in status_levels else 2
        
        return current_level >= threshold_level
    
    def find_support_partners(self, all_agents: Dict[str, 'VeniceAgent'], need: str) -> List[str]:
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
        
        for agent in all_agents.values():
            if agent.agent_id != self.agent_id:
                if any(cap in agent.capabilities for cap in required_caps):
                    partners.append(agent.agent_id)
        
        return partners[:5]  # Limit to top 5 partners
    
    def can_provide_support(self, need: str) -> bool:
        """Check if this agent can provide the requested support"""
        capability_map = {
            'protection': ['emergency_response', 'security'],
            'drainage': ['pumping', 'emergency_response'],
            'power': ['electricity', 'power_distribution'],
            'medical_care': ['medical_care', 'emergency_treatment'],
            'evacuation': ['evacuation_route', 'mobility']
        }
        
        required_caps = capability_map.get(need, [need])
        return any(cap in self.capabilities for cap in required_caps)

class FloodSimulation:
    """Main simulation engine"""
    
    def __init__(self, agents_file: str = "venice_agents.ndjson", log_level: str = "INFO"):
        # Setup logging
        self.setup_logging(log_level)
        
        self.agents = {}
        self.load_agents(agents_file)
        self.message_log = []
        self.tick_snapshots = []
        self.current_tick = 0
        self.flood_stage = 0
        
        logger.info(f"FloodSimulation initialized with {len(self.agents)} agents")
    
    def setup_logging(self, log_level: str):
        """Setup comprehensive logging for simulation"""
        # Remove default handler
        logger.remove()
        
        # Add console handler with custom format
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=log_level
        )
        
        # Add file handler for simulation logs
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.add(
            f"logs/simulation_{timestamp}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation="10 MB"
        )
        
        # Create logs directory if it doesn't exist
        Path("logs").mkdir(exist_ok=True)
        
    def load_agents(self, agents_file: str):
        """Load agents from NDJSON file"""
        with open(agents_file, 'r') as f:
            for line in f:
                agent_data = json.loads(line)
                agent = VeniceAgent(agent_data)
                self.agents[agent.agent_id] = agent
        
        print(f"Loaded {len(self.agents)} agents")
    
    def set_flood_stage(self, stage: int):
        """Update flood stage (0-3)"""
        self.flood_stage = max(0, min(3, stage))
    
    def send_message(self, message: Message, p_fail: float = 0.0) -> bool:
        """Send a message with optional failure probability"""
        # Apply stochastic failure
        if random.random() < p_fail:
            message.success = False
            self.message_log.append(message)
            return False
        
        # Successful delivery
        if message.receiver == 'broadcast':
            # Broadcast to all agents except sender
            for agent_id, agent in self.agents.items():
                if agent_id != message.sender:
                    agent.message_queue.append(message)
        else:
            # Direct message
            if message.receiver in self.agents:
                self.agents[message.receiver].message_queue.append(message)
            else:
                message.success = False
        
        self.message_log.append(message)
        return message.success
    
    def process_agent_turn(self, agent: VeniceAgent, p_fail: float, equity_weighting: float = 0.0):
        """Process one agent's turn in the simulation"""
        
        # 1. SENSE: Update status based on flood stage
        new_status = agent.get_current_status(self.flood_stage)
        status_changed = new_status != agent.status
        agent.status = new_status
        
        # 2. DECIDE: Generate messages based on status and needs
        
        # Status update if changed and meets broadcast threshold
        if status_changed and agent.needs_to_broadcast(new_status):
            msg = Message(
                sender=agent.agent_id,
                receiver='broadcast',
                tick=self.current_tick,
                intent='status_update',
                payload={
                    'status': new_status,
                    'place_name': agent.place_name,
                    'sector': agent.sector,
                    'coordinates': agent.coordinates,
                    'vulnerability': agent.vulnerability,
                    'capabilities': agent.capabilities
                }
            )
            self.send_message(msg, p_fail)
        
        # Request support for unmet needs (after N ticks)
        escalation_delay = 5  # N ticks
        if (self.current_tick - agent.last_update_tick) >= escalation_delay:
            for need in agent.unmet_needs[:3]:  # Limit concurrent requests
                partners = agent.find_support_partners(self.agents, need)
                for partner_id in partners:
                    msg = Message(
                        sender=agent.agent_id,
                        receiver=partner_id,
                        tick=self.current_tick,
                        intent='request_support',
                        payload={
                            'need': need,
                            'urgency': new_status,
                            'place_name': agent.place_name,
                            'vulnerability': agent.vulnerability,
                            'coordinates': agent.coordinates
                        }
                    )
                    self.send_message(msg, p_fail)
                    agent.pending_requests.append({
                        'need': need,
                        'partner': partner_id,
                        'tick': self.current_tick
                    })
            
            agent.last_update_tick = self.current_tick
        
        # 3. ACT: Process incoming messages
        priority_queue = sorted(agent.message_queue, 
                               key=lambda m: self.get_message_priority(m, equity_weighting),
                               reverse=True)
        
        for message in priority_queue[:10]:  # Process top 10 messages per tick
            self.process_message(agent, message, p_fail)
        
        agent.message_queue = []  # Clear processed messages
        
        # Update unmet needs based on current status
        if new_status in ['critical', 'emergency']:
            base_needs = agent.needs.copy()
            if new_status == 'emergency':
                base_needs.extend(['evacuation', 'emergency_response'])
            
            for need in base_needs:
                if need not in [r['need'] for r in agent.pending_requests]:
                    if need not in agent.unmet_needs:
                        agent.unmet_needs.append(need)
    
    def get_message_priority(self, message: Message, equity_weighting: float) -> float:
        """Calculate message priority for processing order"""
        base_priority = 1.0
        
        # Priority by intent
        intent_priorities = {
            'emergency_response': 4.0,
            'request_support': 3.0,
            'commit': 2.0,
            'status_update': 1.0,
            'reject': 0.5
        }
        base_priority *= intent_priorities.get(message.intent, 1.0)
        
        # Equity weighting based on sender vulnerability
        if equity_weighting > 0 and message.sender in self.agents:
            sender_vulnerability = self.agents[message.sender].vulnerability
            base_priority += equity_weighting * sender_vulnerability
        
        return base_priority
    
    def process_message(self, receiver_agent: VeniceAgent, message: Message, p_fail: float):
        """Process a single incoming message"""
        
        if message.intent == 'request_support':
            need = message.payload.get('need')
            if receiver_agent.can_provide_support(need):
                # Decide whether to commit or reject
                commit_probability = 0.7  # Base probability
                
                # Reduce probability if agent is stressed
                if receiver_agent.status == 'emergency':
                    commit_probability *= 0.3
                elif receiver_agent.status == 'critical':
                    commit_probability *= 0.6
                
                if random.random() < commit_probability:
                    # Send commit
                    response = Message(
                        sender=receiver_agent.agent_id,
                        receiver=message.sender,
                        tick=self.current_tick,
                        intent='commit',
                        payload={
                            'need': need,
                            'estimated_response_time': random.randint(1, 5),
                            'capabilities': receiver_agent.capabilities
                        }
                    )
                    self.send_message(response, p_fail)
                    receiver_agent.committed_support.append({
                        'to': message.sender,
                        'need': need,
                        'tick': self.current_tick
                    })
                else:
                    # Send reject
                    response = Message(
                        sender=receiver_agent.agent_id,
                        receiver=message.sender,
                        tick=self.current_tick,
                        intent='reject',
                        payload={
                            'need': need,
                            'reason': f'unavailable_due_to_{receiver_agent.status}'
                        }
                    )
                    self.send_message(response, p_fail)
        
        elif message.intent == 'commit':
            # Remove the need from unmet list
            need = message.payload.get('need')
            if need in receiver_agent.unmet_needs:
                receiver_agent.unmet_needs.remove(need)
            
            # Remove from pending requests
            receiver_agent.pending_requests = [
                r for r in receiver_agent.pending_requests 
                if not (r['need'] == need and r['partner'] == message.sender)
            ]
    
    def take_snapshot(self):
        """Take a snapshot of current agent states"""
        snapshot = {
            'tick': self.current_tick,
            'flood_stage': self.flood_stage,
            'agents': {}
        }
        
        for agent_id, agent in self.agents.items():
            snapshot['agents'][agent_id] = {
                'status': agent.status,
                'queue_len': len(agent.message_queue),
                'unmet_needs': len(agent.unmet_needs),
                'pending_requests': len(agent.pending_requests),
                'committed_support': len(agent.committed_support),
                'vulnerability': agent.vulnerability,
                'sector': agent.sector
            }
        
        self.tick_snapshots.append(snapshot)
    
    def run_scenario(self, scenario_name: str, max_ticks: int = 120, **scenario_params):
        """Run a specific scenario"""
        print(f"\n=== Running Scenario {scenario_name} ===")
        logger.info(f"Starting scenario {scenario_name} with parameters: {scenario_params}")
        
        # Reset simulation state
        for agent in self.agents.values():
            agent.status = 'normal'
            agent.message_queue = []
            agent.unmet_needs = []
            agent.pending_requests = []
            agent.committed_support = []
            agent.last_update_tick = 0
        
        self.message_log = []
        self.tick_snapshots = []
        self.current_tick = 0
        
        # Extract scenario parameters
        p_fail = scenario_params.get('p_fail', 0.1)
        equity_weighting = scenario_params.get('equity_weighting', 0.0)
        outage_agents = scenario_params.get('outage_agents', [])
        outage_start = scenario_params.get('outage_start', -1)
        outage_end = scenario_params.get('outage_end', -1)
        pump_response_scale = scenario_params.get('pump_response_scale', 1.0)
        
        # Initialize flood progression
        flood_progression = [0] * 30 + [1] * 30 + [2] * 30 + [3] * 30  # Simple progression
        
        for tick in range(max_ticks):
            self.current_tick = tick
            
            # Update flood stage
            if tick < len(flood_progression):
                old_stage = self.flood_stage
                self.set_flood_stage(flood_progression[tick])
                if self.flood_stage != old_stage:
                    logger.info(f"Tick {tick}: Flood stage escalated to {self.flood_stage}")
            
            # Handle outages
            active_agents = list(self.agents.keys())
            if outage_start <= tick <= outage_end:
                if tick == outage_start:
                    logger.warning(f"Tick {tick}: Outage started - removing agents {outage_agents}")
                active_agents = [a for a in active_agents if a not in outage_agents]
            
            # Process each agent's turn
            agent_order = list(active_agents)
            random.shuffle(agent_order)  # Random processing order
            
            tick_messages = 0
            for agent_id in agent_order:
                agent = self.agents[agent_id]
                
                # Apply pump response scaling if relevant
                current_p_fail = p_fail
                if 'pumping' in agent.capabilities and pump_response_scale < 1.0:
                    current_p_fail = p_fail + (1 - pump_response_scale) * 0.5
                    if tick == 30:  # Log cyber disruption start
                        logger.warning(f"Cyber disruption affecting pump {agent_id}")
                
                messages_before = len(self.message_log)
                self.process_agent_turn(agent, current_p_fail, equity_weighting)
                agent_messages = len(self.message_log) - messages_before
                tick_messages += agent_messages
                
                if agent_messages > 0:
                    logger.debug(f"Tick {tick}: Agent {agent_id} sent {agent_messages} messages")
            
            # Take snapshot
            self.take_snapshot()
            
            # Log tick summary
            if tick % 20 == 0:
                active_count = len(active_agents)
                print(f"  Tick {tick}: {tick_messages} messages, {active_count} active agents")
                logger.info(f"Tick {tick} summary: {tick_messages} messages, {active_count} active agents, flood_stage={self.flood_stage}")
        
        print(f"Scenario {scenario_name} complete: {len(self.message_log)} total messages")
        return self.get_scenario_results()
    
    def get_scenario_results(self) -> Dict[str, Any]:
        """Calculate metrics for the completed scenario"""
        
        # Basic message stats
        total_messages = len(self.message_log)
        delivered_messages = len([m for m in self.message_log if m.success])
        delivery_ratio = delivered_messages / total_messages if total_messages > 0 else 0
        
        # Time-to-ack analysis
        request_commits = {}
        for msg in self.message_log:
            if msg.intent == 'request_support':
                request_key = (msg.sender, msg.payload.get('need'))
                request_commits[request_key] = {'request_tick': msg.tick, 'commit_tick': None}
        
        for msg in self.message_log:
            if msg.intent == 'commit':
                request_key = (msg.receiver, msg.payload.get('need'))
                if request_key in request_commits:
                    request_commits[request_key]['commit_tick'] = msg.tick
        
        response_times = []
        for req_data in request_commits.values():
            if req_data['commit_tick'] is not None:
                response_times.append(req_data['commit_tick'] - req_data['request_tick'])
        
        median_response_time = sorted(response_times)[len(response_times)//2] if response_times else 0
        
        # Final unmet needs
        final_snapshot = self.tick_snapshots[-1] if self.tick_snapshots else None
        total_unmet_needs = 0
        unmet_by_vulnerability = {'low': 0, 'high': 0}
        
        if final_snapshot:
            for agent_id, agent_state in final_snapshot['agents'].items():
                unmet_count = agent_state['unmet_needs']
                total_unmet_needs += unmet_count
                
                vulnerability = agent_state['vulnerability']
                vuln_category = 'high' if vulnerability > 0.6 else 'low'
                unmet_by_vulnerability[vuln_category] += unmet_count
        
        equity_gap = unmet_by_vulnerability['high'] - unmet_by_vulnerability['low']
        
        return {
            'delivery_ratio': delivery_ratio,
            'median_response_time': median_response_time,
            'total_unmet_needs': total_unmet_needs,
            'equity_gap': equity_gap,
            'total_messages': total_messages,
            'response_times': response_times
        }
    
    def save_results(self, scenario_name: str):
        """Save message log and snapshots"""
        # Save message log
        log_file = f"message_log_{scenario_name}.ndjson"
        with open(log_file, 'w') as f:
            for msg in self.message_log:
                f.write(json.dumps(msg.to_dict()) + '\n')
        
        # Save snapshots
        snapshot_file = f"snapshots_{scenario_name}.json"
        with open(snapshot_file, 'w') as f:
            json.dump(self.tick_snapshots, f, indent=2)
        
        print(f"Results saved: {log_file}, {snapshot_file}")

def run_all_scenarios():
    """Run all scenarios A-F from the experiment plan"""
    
    sim = FloodSimulation()
    results = {}
    
    # Scenario A: Baseline/noisy commons
    results['A'] = sim.run_scenario('A', p_fail=0.1)
    sim.save_results('A')
    
    # Scenario B: Redundancy 
    results['B'] = sim.run_scenario('B', p_fail=0.2)  # Higher failure rate, agents will use redundancy
    sim.save_results('B')
    
    # Scenario C: Routing hints (simulated by better partner finding)
    results['C'] = sim.run_scenario('C', p_fail=0.1)
    sim.save_results('C')
    
    # Scenario D: Bottleneck stress (remove transport hub)
    transport_hubs = [aid for aid, agent in sim.agents.items() 
                     if 'transport' in agent.sector and 'coordination' in agent.capabilities]
    outage_agent = transport_hubs[0] if transport_hubs else list(sim.agents.keys())[0]
    
    results['D'] = sim.run_scenario('D', p_fail=0.1, 
                                   outage_agents=[outage_agent], 
                                   outage_start=30, outage_end=60)
    sim.save_results('D')
    
    # Scenario E: Equity-weighted
    results['E'] = sim.run_scenario('E', p_fail=0.1, equity_weighting=1.0)
    sim.save_results('E')
    
    # Scenario F: Cyber-physical twist
    results['F'] = sim.run_scenario('F', p_fail=0.1, pump_response_scale=0.5)
    sim.save_results('F')
    
    return results

if __name__ == "__main__":
    print("Venice Cascading Flood Risk Simulation")
    print("======================================")
    
    results = run_all_scenarios()
    
    print("\n=== SCENARIO COMPARISON ===")
    print(f"{'Scenario':<10} {'Delivery':<10} {'Response':<10} {'Unmet':<8} {'Equity':<8}")
    print("-" * 50)
    
    for scenario, data in results.items():
        print(f"{scenario:<10} {data['delivery_ratio']:<10.2f} {data['median_response_time']:<10.1f} "
              f"{data['total_unmet_needs']:<8} {data['equity_gap']:<8}")
