#!/usr/bin/env python3
"""
Multi-Hazard Cyber-Physical Cascade Scenario Framework
Building on Venice Flat Ontology simulation for complex disaster modeling
"""

import json
import random
import copy
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path
import logging
from loguru import logger
import sys
from datetime import datetime
import numpy as np
from enum import Enum

from venice_flood_simulation import FloodSimulation, VeniceAgent, Message

class HazardType(Enum):
    FLOOD = "flood"
    CYBER_ATTACK = "cyber_attack"
    POWER_OUTAGE = "power_outage"
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"
    SOCIAL_DISRUPTION = "social_disruption"
    SUPPLY_CHAIN = "supply_chain"
    COMMUNICATION_FAILURE = "communication_failure"

@dataclass
class CascadeEvent:
    """Individual cascade event in multi-hazard scenario"""
    event_id: str
    hazard_type: HazardType
    trigger_tick: int
    duration: int
    affected_agents: List[str]
    severity: float  # 0.0 to 1.0
    dependencies: List[str]  # Other event IDs this depends on
    cyber_physical_links: Dict[str, Any]
    description: str
    
    def to_dict(self):
        return {
            'event_id': self.event_id,
            'hazard_type': self.hazard_type.value,
            'trigger_tick': self.trigger_tick,
            'duration': self.duration,
            'affected_agents': self.affected_agents,
            'severity': self.severity,
            'dependencies': self.dependencies,
            'cyber_physical_links': self.cyber_physical_links,
            'description': self.description
        }

@dataclass
class SystemInterdependency:
    """Cyber-physical system interdependency definition"""
    dependency_id: str
    system_a: str  # e.g., "power_grid"
    system_b: str  # e.g., "water_pumps"
    dependency_type: str  # "functional", "cyber", "physical", "logical"
    coupling_strength: float  # 0.0 to 1.0
    failure_threshold: float  # At what point does system_a failure affect system_b
    propagation_delay: int  # Ticks for cascade to propagate
    bidirectional: bool = False

class MultiHazardCascadeSimulation(FloodSimulation):
    """Enhanced simulation with multi-hazard cyber-physical cascades"""
    
    def __init__(self, agents_file: str = "venice_agents.ndjson", log_level: str = "INFO"):
        super().__init__(agents_file, log_level)
        
        self.cascade_events: List[CascadeEvent] = []
        self.active_events: Set[str] = set()
        self.system_states: Dict[str, float] = {}
        self.interdependencies: List[SystemInterdependency] = []
        self.cascade_log: List[Dict] = []
        
        # Initialize system states
        self.initialize_system_states()
        self.define_cyber_physical_interdependencies()
        
        logger.info(f"MultiHazardCascadeSimulation initialized with {len(self.interdependencies)} interdependencies")
    
    def initialize_system_states(self):
        """Initialize cyber-physical system states"""
        systems = [
            "power_grid", "water_system", "communication_network", 
            "transport_network", "emergency_services", "digital_infrastructure",
            "pumping_stations", "flood_barriers", "sensor_network",
            "emergency_communications", "public_wifi", "cellular_network"
        ]
        
        for system in systems:
            self.system_states[system] = 1.0  # Fully operational
    
    def define_cyber_physical_interdependencies(self):
        """Define key cyber-physical interdependencies for Venice"""
        
        interdependencies = [
            # Power dependencies
            SystemInterdependency(
                "power_pumps", "power_grid", "pumping_stations", 
                "functional", 0.9, 0.1, 2
            ),
            SystemInterdependency(
                "power_communications", "power_grid", "communication_network",
                "functional", 0.8, 0.2, 1
            ),
            SystemInterdependency(
                "power_sensors", "power_grid", "sensor_network",
                "functional", 0.7, 0.3, 1
            ),
            
            # Cyber dependencies
            SystemInterdependency(
                "cyber_pumps", "digital_infrastructure", "pumping_stations",
                "cyber", 0.85, 0.15, 3, True
            ),
            SystemInterdependency(
                "cyber_barriers", "digital_infrastructure", "flood_barriers",
                "cyber", 0.75, 0.25, 2
            ),
            SystemInterdependency(
                "cyber_emergency", "digital_infrastructure", "emergency_services",
                "cyber", 0.6, 0.4, 1
            ),
            
            # Communication dependencies
            SystemInterdependency(
                "comm_emergency", "communication_network", "emergency_services",
                "logical", 0.9, 0.1, 1, True
            ),
            SystemInterdependency(
                "comm_coordination", "communication_network", "transport_network",
                "logical", 0.5, 0.5, 2
            ),
            
            # Physical cascade dependencies
            SystemInterdependency(
                "flood_power", "water_system", "power_grid",
                "physical", 0.7, 0.3, 5
            ),
            SystemInterdependency(
                "flood_transport", "water_system", "transport_network",
                "physical", 0.8, 0.2, 3
            ),
            SystemInterdependency(
                "flood_digital", "water_system", "digital_infrastructure",
                "physical", 0.6, 0.4, 4
            )
        ]
        
        self.interdependencies = interdependencies
    
    def create_cyber_physical_cascade_scenario(self, scenario_name: str) -> List[CascadeEvent]:
        """Create a specific multi-hazard cascade scenario"""
        
        scenarios = {
            "ransomware_flood": self._create_ransomware_flood_scenario(),
            "power_surge_cascade": self._create_power_surge_scenario(),
            "cyber_storm_perfect": self._create_cyber_storm_scenario(),
            "supply_chain_flood": self._create_supply_chain_scenario(),
            "communication_breakdown": self._create_communication_breakdown_scenario(),
            "infrastructure_aging": self._create_infrastructure_aging_scenario(),
            "social_media_panic": self._create_social_media_panic_scenario(),
            "sensor_network_failure": self._create_sensor_failure_scenario()
        }
        
        return scenarios.get(scenario_name, [])
    
    def _create_ransomware_flood_scenario(self) -> List[CascadeEvent]:
        """Scenario: Ransomware attack during high tide flood"""
        
        # Select critical infrastructure agents
        pump_agents = [aid for aid, agent in self.agents.items() 
                      if 'pumping' in agent.capabilities]
        emergency_agents = [aid for aid, agent in self.agents.items() 
                           if 'emergency_response' in agent.capabilities]
        
        events = [
            # Initial flood starts
            CascadeEvent(
                "flood_init", HazardType.FLOOD, 10, 100,
                list(self.agents.keys()), 0.6, [],
                {"flood_stage_progression": [0, 1, 2, 3, 2, 1]},
                "Venice acqua alta flooding begins - 120cm expected"
            ),
            
            # Ransomware attack on digital infrastructure
            CascadeEvent(
                "ransomware_attack", HazardType.CYBER_ATTACK, 20, 60,
                pump_agents + emergency_agents, 0.8, [],
                {"attack_vector": "phishing", "encryption_rate": 0.7, 
                 "backup_systems": False, "payment_demand": True},
                "Ransomware attack targets pump control systems"
            ),
            
            # Pump systems fail due to cyber attack
            CascadeEvent(
                "pump_failure", HazardType.INFRASTRUCTURE_FAILURE, 25, 50,
                pump_agents, 0.9, ["ransomware_attack"],
                {"manual_override": False, "remote_access": False, 
                 "local_control": 0.2},
                "Automated pump systems offline - manual operation only"
            ),
            
            # Communication systems overloaded
            CascadeEvent(
                "comm_overload", HazardType.COMMUNICATION_FAILURE, 30, 40,
                [aid for aid, agent in self.agents.items() 
                 if 'coordination' in agent.capabilities], 0.7, ["ransomware_attack"],
                {"network_congestion": 0.8, "priority_channels": True},
                "Emergency communication channels overwhelmed"
            ),
            
            # Social disruption from failed response
            CascadeEvent(
                "public_panic", HazardType.SOCIAL_DISRUPTION, 40, 30,
                [aid for aid, agent in self.agents.items() 
                 if agent.sector in ['tourism', 'commercial']], 0.6, 
                ["pump_failure", "comm_overload"],
                {"social_media_spread": True, "misinformation": 0.4},
                "Public panic due to failed flood response systems"
            )
        ]
        
        return events
    
    def _create_power_surge_scenario(self) -> List[CascadeEvent]:
        """Scenario: Power surge cascading through interconnected systems"""
        
        power_dependent = [aid for aid, agent in self.agents.items() 
                          if any(cap in ['electricity', 'pumping', 'coordination'] 
                                for cap in agent.capabilities)]
        
        events = [
            CascadeEvent(
                "power_surge", HazardType.POWER_OUTAGE, 15, 80,
                power_dependent, 0.75, [],
                {"surge_cause": "grid_instability", "cascade_rate": 0.6},
                "Electrical grid surge damages connected systems"
            ),
            
            CascadeEvent(
                "pump_degradation", HazardType.INFRASTRUCTURE_FAILURE, 20, 70,
                [aid for aid, agent in self.agents.items() 
                 if 'pumping' in agent.capabilities], 0.8, ["power_surge"],
                {"pump_efficiency": 0.3, "backup_power": False},
                "Pump systems operating at reduced capacity"
            ),
            
            CascadeEvent(
                "sensor_blackout", HazardType.INFRASTRUCTURE_FAILURE, 18, 60,
                [aid for aid, agent in self.agents.items() 
                 if 'monitoring' in agent.capabilities], 0.9, ["power_surge"],
                {"blind_operations": True, "manual_monitoring": 0.2},
                "Flood monitoring sensors offline"
            )
        ]
        
        return events
    
    def _create_cyber_storm_scenario(self) -> List[CascadeEvent]:
        """Scenario: Perfect storm - cyber attack during major flood"""
        
        events = [
            CascadeEvent(
                "major_flood", HazardType.FLOOD, 5, 110,
                list(self.agents.keys()), 0.9, [],
                {"exceptional_tide": True, "storm_surge": True, "wind_damage": True},
                "Exceptional acqua alta + storm surge - 160cm flooding"
            ),
            
            CascadeEvent(
                "nation_state_cyber", HazardType.CYBER_ATTACK, 25, 80,
                list(self.agents.keys()), 0.85, [],
                {"attack_sophistication": "nation_state", "zero_day": True,
                 "multi_vector": True, "stealth_mode": True},
                "Sophisticated cyber attack on critical infrastructure"
            ),
            
            CascadeEvent(
                "supply_disruption", HazardType.SUPPLY_CHAIN, 30, 90,
                [aid for aid, agent in self.agents.items() 
                 if agent.sector in ['commercial', 'emergency_response']], 0.7,
                ["major_flood", "nation_state_cyber"],
                {"logistics_breakdown": True, "fuel_shortage": True,
                 "equipment_unavailable": True},
                "Supply chain collapse - no replacement equipment"
            )
        ]
        
        return events
    
    def _create_supply_chain_scenario(self) -> List[CascadeEvent]:
        """Scenario: Supply chain disruption during flood response"""
        
        events = [
            CascadeEvent(
                "supply_crisis", HazardType.SUPPLY_CHAIN, 40, 60,
                [aid for aid, agent in self.agents.items() 
                 if 'emergency_response' in agent.capabilities], 0.6, [],
                {"fuel_shortage": True, "equipment_delays": True,
                 "maintenance_parts": False},
                "Supply chain disruption affects flood response equipment"
            )
        ]
        
        return events
    
    def _create_communication_breakdown_scenario(self) -> List[CascadeEvent]:
        """Scenario: Communication network failure cascade"""
        
        comm_agents = [aid for aid, agent in self.agents.items() 
                      if 'coordination' in agent.capabilities]
        
        events = [
            CascadeEvent(
                "cell_tower_flood", HazardType.INFRASTRUCTURE_FAILURE, 35, 50,
                comm_agents, 0.8, [],
                {"physical_damage": True, "backup_power": False},
                "Cellular towers flooded - network capacity reduced"
            ),
            
            CascadeEvent(
                "internet_backbone", HazardType.INFRASTRUCTURE_FAILURE, 45, 40,
                comm_agents, 0.7, ["cell_tower_flood"],
                {"fiber_cuts": True, "data_center_flood": True},
                "Internet backbone damage - digital isolation"
            )
        ]
        
        return events
    
    def _create_infrastructure_aging_scenario(self) -> List[CascadeEvent]:
        """Scenario: Aging infrastructure failures during stress"""
        
        infrastructure_agents = [aid for aid, agent in self.agents.items() 
                                if any(cap in ['pumping', 'emergency_response', 'electricity'] 
                                      for cap in agent.capabilities)]
        
        events = [
            CascadeEvent(
                "aging_failure", HazardType.INFRASTRUCTURE_FAILURE, 50, 70,
                infrastructure_agents, 0.6, [],
                {"deferred_maintenance": True, "stress_fractures": True,
                 "component_fatigue": True},
                "Aging infrastructure fails under flood stress"
            )
        ]
        
        return events
    
    def _create_social_media_panic_scenario(self) -> List[CascadeEvent]:
        """Scenario: Social media amplified panic and misinformation"""
        
        public_spaces = [aid for aid, agent in self.agents.items() 
                        if agent.sector in ['tourism', 'commercial', 'transport']]
        
        events = [
            CascadeEvent(
                "viral_misinformation", HazardType.SOCIAL_DISRUPTION, 60, 45,
                public_spaces, 0.5, [],
                {"social_media_amplification": True, "fake_news": True,
                 "panic_buying": True, "evacuation_chaos": True},
                "Viral misinformation causes evacuation panic"
            )
        ]
        
        return events
    
    def _create_sensor_failure_scenario(self) -> List[CascadeEvent]:
        """Scenario: Sensor network failure creates blind spots"""
        
        monitoring_agents = [aid for aid, agent in self.agents.items() 
                           if any(cap in ['monitoring', 'emergency_response'] 
                                 for cap in agent.capabilities)]
        
        events = [
            CascadeEvent(
                "sensor_network_down", HazardType.INFRASTRUCTURE_FAILURE, 25, 80,
                monitoring_agents, 0.8, [],
                {"sensor_calibration_drift": True, "data_corruption": True,
                 "false_readings": 0.3, "communication_loss": True},
                "Flood sensor network provides false/no data"
            )
        ]
        
        return events
    
    def apply_cascade_effects(self, event: CascadeEvent, tick: int):
        """Apply the effects of a cascade event on agents and systems"""
        
        logger.info(f"Tick {tick}: Applying cascade event {event.event_id} - {event.description}")
        
        # Update system states based on event
        system_impacts = self.calculate_system_impacts(event)
        
        for system, impact in system_impacts.items():
            old_state = self.system_states.get(system, 1.0)
            new_state = max(0.0, old_state - (impact * event.severity))
            self.system_states[system] = new_state
            
            if old_state - new_state > 0.1:  # Significant degradation
                logger.warning(f"System {system}: {old_state:.2f} → {new_state:.2f}")
        
        # Apply effects to specific agents
        for agent_id in event.affected_agents:
            if agent_id in self.agents:
                self.apply_agent_cascade_effects(self.agents[agent_id], event, system_impacts)
        
        # Check for propagation to dependent systems
        self.propagate_cascade_effects(event, tick)
        
        # Log cascade event
        self.cascade_log.append({
            'tick': tick,
            'event_id': event.event_id,
            'description': event.description,
            'affected_agents': len(event.affected_agents),
            'system_states': copy.deepcopy(self.system_states),
            'severity': event.severity
        })
    
    def calculate_system_impacts(self, event: CascadeEvent) -> Dict[str, float]:
        """Calculate impact on different systems from cascade event"""
        
        impacts = {}
        
        if event.hazard_type == HazardType.CYBER_ATTACK:
            impacts.update({
                "digital_infrastructure": 0.8,
                "pumping_stations": 0.6,
                "communication_network": 0.7,
                "emergency_services": 0.4
            })
            
        elif event.hazard_type == HazardType.POWER_OUTAGE:
            impacts.update({
                "power_grid": 0.9,
                "pumping_stations": 0.8,
                "communication_network": 0.6,
                "sensor_network": 0.7,
                "emergency_services": 0.3
            })
            
        elif event.hazard_type == HazardType.INFRASTRUCTURE_FAILURE:
            impacts.update({
                "pumping_stations": 0.7,
                "transport_network": 0.5,
                "emergency_services": 0.4
            })
            
        elif event.hazard_type == HazardType.COMMUNICATION_FAILURE:
            impacts.update({
                "communication_network": 0.9,
                "emergency_services": 0.6,
                "transport_network": 0.3
            })
            
        elif event.hazard_type == HazardType.SOCIAL_DISRUPTION:
            impacts.update({
                "transport_network": 0.4,
                "emergency_services": 0.5,
                "communication_network": 0.3
            })
            
        elif event.hazard_type == HazardType.SUPPLY_CHAIN:
            impacts.update({
                "emergency_services": 0.6,
                "pumping_stations": 0.4,
                "power_grid": 0.3
            })
        
        return impacts
    
    def apply_agent_cascade_effects(self, agent: VeniceAgent, event: CascadeEvent, system_impacts: Dict[str, float]):
        """Apply cascade event effects to individual agent"""
        
        # Modify agent's message failure probability
        base_p_fail = 0.1
        
        # Cyber attacks affect digital systems
        if event.hazard_type == HazardType.CYBER_ATTACK:
            if 'pumping' in agent.capabilities:
                agent.cyber_disruption = event.severity * 0.8
            if 'coordination' in agent.capabilities:
                agent.comm_disruption = event.severity * 0.6
                
        # Power outages affect electrical systems
        elif event.hazard_type == HazardType.POWER_OUTAGE:
            if any(cap in ['electricity', 'pumping', 'monitoring'] for cap in agent.capabilities):
                agent.power_disruption = event.severity * 0.9
                
        # Infrastructure failures affect specific capabilities
        elif event.hazard_type == HazardType.INFRASTRUCTURE_FAILURE:
            # Reduce agent effectiveness
            if hasattr(agent, 'effectiveness'):
                agent.effectiveness *= (1 - event.severity * 0.5)
            else:
                agent.effectiveness = 1 - event.severity * 0.5
                
        # Communication failures increase message failure rates
        elif event.hazard_type == HazardType.COMMUNICATION_FAILURE:
            if hasattr(agent, 'message_failure_rate'):
                agent.message_failure_rate = min(0.9, base_p_fail + event.severity * 0.4)
            else:
                agent.message_failure_rate = base_p_fail + event.severity * 0.4
    
    def propagate_cascade_effects(self, trigger_event: CascadeEvent, tick: int):
        """Propagate cascade effects through system interdependencies"""
        
        for interdep in self.interdependencies:
            system_a_state = self.system_states.get(interdep.system_a, 1.0)
            
            # Check if system A failure threshold is reached
            if system_a_state < (1.0 - interdep.failure_threshold):
                # Calculate impact on system B
                impact_strength = interdep.coupling_strength * (1.0 - system_a_state)
                
                # Apply with delay
                propagation_tick = tick + interdep.propagation_delay
                
                # Create secondary cascade event
                secondary_event = CascadeEvent(
                    f"cascade_{interdep.dependency_id}_{tick}",
                    HazardType.INFRASTRUCTURE_FAILURE,
                    propagation_tick,
                    20,  # Default duration
                    [],  # Will be filled based on system type
                    min(0.9, impact_strength),
                    [trigger_event.event_id],
                    {"propagated_from": interdep.system_a, "propagated_to": interdep.system_b},
                    f"Cascade failure: {interdep.system_a} → {interdep.system_b}"
                )
                
                # Add affected agents based on system type
                secondary_event.affected_agents = self.get_agents_for_system(interdep.system_b)
                
                # Schedule secondary event
                self.cascade_events.append(secondary_event)
                
                logger.warning(f"Cascade propagation: {interdep.system_a} → {interdep.system_b} "
                             f"(strength: {impact_strength:.2f}, delay: {interdep.propagation_delay})")
    
    def get_agents_for_system(self, system_name: str) -> List[str]:
        """Get agents associated with a particular system"""
        
        system_capability_map = {
            "pumping_stations": ["pumping"],
            "power_grid": ["electricity", "power_distribution"],
            "communication_network": ["coordination", "communication"],
            "emergency_services": ["emergency_response", "rescue"],
            "transport_network": ["mobility", "evacuation_route"],
            "sensor_network": ["monitoring"],
            "digital_infrastructure": ["coordination", "pumping"],
            "flood_barriers": ["protection"],
            "water_system": ["pumping", "drainage"]
        }
        
        required_capabilities = system_capability_map.get(system_name, [])
        
        agents = []
        for agent_id, agent in self.agents.items():
            if any(cap in agent.capabilities for cap in required_capabilities):
                agents.append(agent_id)
        
        return agents
    
    def run_multi_hazard_scenario(self, scenario_name: str, max_ticks: int = 120, **scenario_params):
        """Run a multi-hazard cascade scenario"""
        
        logger.info(f"Starting multi-hazard scenario: {scenario_name}")
        
        # Reset simulation
        self.reset_simulation()
        
        # Create scenario events
        self.cascade_events = self.create_cyber_physical_cascade_scenario(scenario_name)
        
        logger.info(f"Loaded {len(self.cascade_events)} cascade events for scenario {scenario_name}")
        
        # Run simulation with cascade event processing
        for tick in range(max_ticks):
            self.current_tick = tick
            
            # Check for cascade events to trigger
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
                logger.info(f"Cascade event {event.event_id} expired at tick {tick}")
            
            # Update flood stage (base hazard)
            self.update_flood_progression(tick, max_ticks)
            
            # Process agent turns with cascade effects
            agent_order = list(self.agents.keys())
            random.shuffle(agent_order)
            
            for agent_id in agent_order:
                agent = self.agents[agent_id]
                
                # Calculate dynamic failure probability based on active cascade effects
                p_fail = self.calculate_agent_failure_probability(agent)
                
                # Process agent turn
                self.process_agent_turn(agent, p_fail, scenario_params.get('equity_weighting', 0.0))
            
            # Take snapshot
            self.take_snapshot_with_cascades()
            
            # Log progress
            if tick % 20 == 0:
                active_events = len(self.active_events)
                total_messages = len([m for m in self.message_log if m.tick == tick])
                logger.info(f"Tick {tick}: {active_events} active events, {total_messages} messages")
        
        results = self.get_cascade_scenario_results()
        logger.info(f"Multi-hazard scenario {scenario_name} complete: {results['total_messages']} messages, "
                   f"{len(self.cascade_log)} cascade events triggered")
        
        return results
    
    def reset_simulation(self):
        """Reset simulation state for new scenario"""
        # Reset parent class state
        for agent in self.agents.values():
            agent.status = 'normal'
            agent.message_queue = []
            agent.unmet_needs = []
            agent.pending_requests = []
            agent.committed_support = []
            agent.last_update_tick = 0
            
            # Reset cascade-specific attributes
            if hasattr(agent, 'cyber_disruption'):
                delattr(agent, 'cyber_disruption')
            if hasattr(agent, 'comm_disruption'):
                delattr(agent, 'comm_disruption')
            if hasattr(agent, 'power_disruption'):
                delattr(agent, 'power_disruption')
            if hasattr(agent, 'effectiveness'):
                delattr(agent, 'effectiveness')
            if hasattr(agent, 'message_failure_rate'):
                delattr(agent, 'message_failure_rate')
        
        self.message_log = []
        self.tick_snapshots = []
        self.cascade_log = []
        self.current_tick = 0
        self.flood_stage = 0
        self.active_events = set()
        
        # Reset system states
        self.initialize_system_states()
    
    def update_flood_progression(self, tick: int, max_ticks: int):
        """Update flood stage progression"""
        # Standard flood progression
        if tick < 30:
            new_stage = 0
        elif tick < 60:
            new_stage = 1
        elif tick < 90:
            new_stage = 2
        else:
            new_stage = 3
            
        if new_stage != self.flood_stage:
            old_stage = self.flood_stage
            self.set_flood_stage(new_stage)
            logger.info(f"Tick {tick}: Flood stage {old_stage} → {new_stage}")
    
    def calculate_agent_failure_probability(self, agent: VeniceAgent) -> float:
        """Calculate dynamic failure probability based on cascade effects"""
        base_p_fail = 0.1
        
        # Accumulate failure probability from various disruptions
        total_disruption = 0.0
        
        if hasattr(agent, 'cyber_disruption'):
            total_disruption += agent.cyber_disruption * 0.4
            
        if hasattr(agent, 'power_disruption'):
            total_disruption += agent.power_disruption * 0.5
            
        if hasattr(agent, 'comm_disruption'):
            total_disruption += agent.comm_disruption * 0.3
            
        if hasattr(agent, 'message_failure_rate'):
            return agent.message_failure_rate
        
        return min(0.9, base_p_fail + total_disruption)
    
    def take_snapshot_with_cascades(self):
        """Enhanced snapshot including cascade information"""
        snapshot = {
            'tick': self.current_tick,
            'flood_stage': self.flood_stage,
            'active_events': list(self.active_events),
            'system_states': copy.deepcopy(self.system_states),
            'agents': {}
        }
        
        for agent_id, agent in self.agents.items():
            agent_state = {
                'status': agent.status,
                'queue_len': len(agent.message_queue),
                'unmet_needs': len(agent.unmet_needs),
                'pending_requests': len(agent.pending_requests),
                'committed_support': len(agent.committed_support),
                'vulnerability': agent.vulnerability,
                'sector': agent.sector,
                'cascade_effects': {
                    'cyber_disruption': getattr(agent, 'cyber_disruption', 0.0),
                    'power_disruption': getattr(agent, 'power_disruption', 0.0),
                    'comm_disruption': getattr(agent, 'comm_disruption', 0.0),
                    'effectiveness': getattr(agent, 'effectiveness', 1.0),
                    'message_failure_rate': getattr(agent, 'message_failure_rate', 0.1)
                }
            }
            snapshot['agents'][agent_id] = agent_state
        
        self.tick_snapshots.append(snapshot)
    
    def get_cascade_scenario_results(self) -> Dict[str, Any]:
        """Calculate enhanced metrics for cascade scenarios"""
        
        # Get base results from parent class
        base_results = self.get_scenario_results()
        
        # Add cascade-specific metrics
        cascade_results = {
            'total_cascade_events': len([e for e in self.cascade_log]),
            'system_degradation': {},
            'cascade_propagations': 0,
            'max_simultaneous_events': 0,
            'cyber_disruption_impact': 0.0,
            'infrastructure_resilience': 0.0
        }
        
        # Calculate system degradation over time
        for system in self.system_states.keys():
            min_state = min([snap['system_states'].get(system, 1.0) 
                           for snap in self.tick_snapshots if 'system_states' in snap] + [1.0])
            cascade_results['system_degradation'][system] = 1.0 - min_state
        
        # Count cascade propagations
        cascade_results['cascade_propagations'] = len([
            event for event in self.cascade_log 
            if event['event_id'].startswith('cascade_')
        ])
        
        # Calculate maximum simultaneous events
        if self.tick_snapshots:
            cascade_results['max_simultaneous_events'] = max(
                len(snap.get('active_events', [])) for snap in self.tick_snapshots
            )
        
        # Calculate cyber disruption impact
        cyber_events = [e for e in self.cascade_log if 'cyber' in e['event_id'].lower()]
        if cyber_events:
            cascade_results['cyber_disruption_impact'] = np.mean([e['severity'] for e in cyber_events])
        
        # Calculate infrastructure resilience (how well systems recovered)
        final_snapshot = self.tick_snapshots[-1] if self.tick_snapshots else None
        if final_snapshot:
            final_system_states = final_snapshot.get('system_states', {})
            cascade_results['infrastructure_resilience'] = np.mean(list(final_system_states.values()))
        
        # Merge results
        return {**base_results, **cascade_results}
    
    def save_cascade_results(self, scenario_name: str):
        """Save enhanced results including cascade information"""
        
        # Save message log (inherited)
        log_file = f"cascade_message_log_{scenario_name}.ndjson"
        with open(log_file, 'w') as f:
            for msg in self.message_log:
                f.write(json.dumps(msg.to_dict()) + '\n')
        
        # Save enhanced snapshots
        snapshot_file = f"cascade_snapshots_{scenario_name}.json"
        with open(snapshot_file, 'w') as f:
            json.dump(self.tick_snapshots, f, indent=2)
        
        # Save cascade event log
        cascade_file = f"cascade_events_{scenario_name}.json"
        with open(cascade_file, 'w') as f:
            json.dump(self.cascade_log, f, indent=2)
        
        # Save system interdependencies
        interdep_file = f"interdependencies_{scenario_name}.json"
        interdep_data = []
        for interdep in self.interdependencies:
            interdep_data.append({
                'dependency_id': interdep.dependency_id,
                'system_a': interdep.system_a,
                'system_b': interdep.system_b,
                'dependency_type': interdep.dependency_type,
                'coupling_strength': interdep.coupling_strength,
                'failure_threshold': interdep.failure_threshold,
                'propagation_delay': interdep.propagation_delay,
                'bidirectional': interdep.bidirectional
            })
        
        with open(interdep_file, 'w') as f:
            json.dump(interdep_data, f, indent=2)
        
        logger.info(f"Cascade results saved: {log_file}, {snapshot_file}, {cascade_file}, {interdep_file}")


def run_multi_hazard_scenarios():
    """Run comprehensive multi-hazard cascade scenarios"""
    
    sim = MultiHazardCascadeSimulation()
    results = {}
    
    scenarios = [
        "ransomware_flood",
        "power_surge_cascade", 
        "cyber_storm_perfect",
        "supply_chain_flood",
        "communication_breakdown",
        "infrastructure_aging",
        "social_media_panic",
        "sensor_network_failure"
    ]
    
    print("=== MULTI-HAZARD CASCADE SCENARIOS ===")
    print(f"Running {len(scenarios)} advanced cascade scenarios...")
    
    for scenario in scenarios:
        print(f"\n--- Running {scenario.upper().replace('_', ' ')} ---")
        
        try:
            results[scenario] = sim.run_multi_hazard_scenario(scenario, max_ticks=120)
            sim.save_cascade_results(scenario)
            
            # Print key results
            r = results[scenario]
            print(f"  Messages: {r['total_messages']}")
            print(f"  Cascade events: {r['total_cascade_events']}")
            print(f"  System degradation: {np.mean(list(r['system_degradation'].values())):.2f}")
            print(f"  Cascade propagations: {r['cascade_propagations']}")
            print(f"  Infrastructure resilience: {r['infrastructure_resilience']:.2f}")
            
        except Exception as e:
            logger.error(f"Error running scenario {scenario}: {e}")
            results[scenario] = {"error": str(e)}
    
    # Generate comparison report
    generate_cascade_comparison_report(results)
    
    return results


def generate_cascade_comparison_report(results: Dict[str, Dict]):
    """Generate comprehensive comparison report of cascade scenarios"""
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'scenario_comparison': {},
        'insights': {},
        'recommendations': {}
    }
    
    # Scenario comparison table
    comparison_data = []
    for scenario, data in results.items():
        if 'error' not in data:
            comparison_data.append({
                'scenario': scenario,
                'total_messages': data.get('total_messages', 0),
                'cascade_events': data.get('total_cascade_events', 0),
                'propagations': data.get('cascade_propagations', 0),
                'system_degradation': np.mean(list(data.get('system_degradation', {}).values())),
                'infrastructure_resilience': data.get('infrastructure_resilience', 0),
                'delivery_ratio': data.get('delivery_ratio', 0),
                'response_time': data.get('median_response_time', 0),
                'unmet_needs': data.get('total_unmet_needs', 0)
            })
    
    report['scenario_comparison'] = comparison_data
    
    # Key insights
    if comparison_data:
        report['insights'] = {
            'most_disruptive': max(comparison_data, key=lambda x: x['system_degradation'])['scenario'],
            'most_resilient': max(comparison_data, key=lambda x: x['infrastructure_resilience'])['scenario'],
            'highest_cascade': max(comparison_data, key=lambda x: x['propagations'])['scenario'],
            'communication_impact': np.mean([d['delivery_ratio'] for d in comparison_data]),
            'average_degradation': np.mean([d['system_degradation'] for d in comparison_data])
        }
    
    # Save report
    with open('multi_hazard_cascade_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n=== MULTI-HAZARD CASCADE ANALYSIS SUMMARY ===")
    if comparison_data:
        print(f"Most Disruptive Scenario: {report['insights']['most_disruptive']}")
        print(f"Most Resilient Scenario: {report['insights']['most_resilient']}")
        print(f"Highest Cascade Propagation: {report['insights']['highest_cascade']}")
        print(f"Average System Degradation: {report['insights']['average_degradation']:.2f}")
        print(f"Average Communication Impact: {report['insights']['communication_impact']:.2f}")
    
    return report


if __name__ == "__main__":
    print("Venice Multi-Hazard Cyber-Physical Cascade Simulation")
    print("=====================================================")
    print("Developing advanced cascade scenarios...")
    
    # Run all multi-hazard scenarios
    results = run_multi_hazard_scenarios()
    
    print("\n=== EXECUTION COMPLETE ===")
    print(f"Successfully ran {len([r for r in results.values() if 'error' not in r])} scenarios")
    print("Results saved to cascade_* files")
    print("Comprehensive report: multi_hazard_cascade_report.json")
