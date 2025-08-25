#!/usr/bin/env python3
"""
Venice Flood Simulation with LLM-Enhanced Message Content
Hybrid approach: structured intents + dynamic content generation
"""

import json
import random
import os
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pathlib import Path
import openai
from dotenv import load_dotenv

# Load environment variables - explicitly specify .env file path
load_dotenv(dotenv_path='.env')

# Debug: Verify environment loading
import sys
if not os.getenv('OPENAI_API_KEY'):
    print("DEBUG: .env not loaded properly")
    # Try loading from current directory
    load_dotenv(dotenv_path=Path('.env'))
    if not os.getenv('OPENAI_API_KEY'):
        print("DEBUG: Still no API key found")
        sys.exit(1)

@dataclass
class EnhancedMessage:
    """Message with LLM-generated content"""
    sender: str
    receiver: str  # specific agent_id or 'broadcast'
    tick: int
    intent: str  # status_update, request_support, commit, reject
    content: str  # LLM-generated natural language
    payload: Dict[str, Any]  # Structured data for processing
    success: bool = True
    
    def to_dict(self):
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'tick': self.tick,
            'intent': self.intent,
            'content': self.content,
            'payload': self.payload,
            'success': self.success
        }

class LLMMessageGenerator:
    """Generate realistic message content using OpenAI API"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.system_prompt = """You are simulating communications during a cascading flood in Venice. 
You control different agents (places, assets, communities, infrastructure). 
Each agent speaks in short, urgent messages, reporting its situation and needs. 
Never invent new places: only use the attributes provided.
Keep messages concise (1-3 sentences), urgent, and context-specific."""
    
    def generate_message_content(self, agent_data: Dict, intent: str, target: str, 
                                tick: int, flood_stage: int, need: str = None) -> str:
        """Generate LLM content for a message"""
        
        # Build agent context
        context_prompt = f"""You are the agent representing: {agent_data['place_name']}, role={agent_data['sector']}.
Location: {agent_data['coordinates']}.
Attributes: vulnerability={agent_data['vulnerability']}, exposure={agent_data['exposure']}, capabilities={agent_data['capabilities']}.
Current unmet needs: {agent_data.get('unmet_needs', [])}.
Current status: {agent_data.get('status', 'unknown')}.
Flood stage: {flood_stage}/3 (0=normal, 3=emergency).
Simulation tick: {tick}.

Your intent is: {intent}.
Your recipient is: {target}.
{f'Specific need you are addressing: {need}' if need else ''}

Write a short message (1–3 sentences) in natural language that matches your intent:
- If status_update: describe current condition, risk level, or impact.
- If request_support: specify what help you need and why.
- If commit: confirm you can provide help and what you will do.
- If reject: state you cannot help and give a short reason."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": context_prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            content = response.choices[0].message.content.strip()
            return content
            
        except Exception as e:
            # Log error but do not generate fallback content - require valid LLM API
            raise RuntimeError(f"LLM content generation failed: {e}. No fallback content will be generated.")

class EnhancedVeniceAgent:
    """Enhanced agent with LLM message generation"""
    
    def __init__(self, agent_data: Dict[str, Any]):
        # Copy all existing agent properties
        for key, value in agent_data.items():
            setattr(self, key, value)
        
        # Dynamic state
        self.status = agent_data['initial_status']
        self.message_queue = []
        self.unmet_needs = []
        self.last_update_tick = 0
        self.committed_support = []
        self.pending_requests = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary for LLM context"""
        return {
            'place_name': self.place_name,
            'coordinates': self.coordinates,
            'sector': self.sector,
            'asset_type': self.asset_type,
            'vulnerability': self.vulnerability,
            'exposure': self.exposure,
            'capabilities': self.capabilities,
            'needs': self.needs,
            'status': self.status,
            'unmet_needs': self.unmet_needs
        }
    
    def generate_enhanced_message(self, intent: str, target: str, tick: int, 
                                 flood_stage: int, llm_generator: LLMMessageGenerator,
                                 need: str = None) -> EnhancedMessage:
        """Generate message with LLM content"""
        
        # Generate LLM content
        content = llm_generator.generate_message_content(
            self.to_dict(), intent, target, tick, flood_stage, need
        )
        
        # Build structured payload
        payload = {
            'agent_type': self.asset_type,
            'sector': self.sector,
            'vulnerability': self.vulnerability,
            'coordinates': self.coordinates,
            'capabilities': self.capabilities
        }
        
        if intent == 'status_update':
            payload.update({
                'status': self.status,
                'place_name': self.place_name,
                'flood_impact': self.get_flood_impact(flood_stage)
            })
        elif intent == 'request_support':
            payload.update({
                'need': need,
                'urgency': self.status,
                'place_name': self.place_name
            })
        elif intent in ['commit', 'reject']:
            payload.update({
                'need': need,
                'response_capability': self.capabilities
            })
        
        return EnhancedMessage(
            sender=self.agent_id,
            receiver=target,
            tick=tick,
            intent=intent,
            content=content,
            payload=payload
        )
    
    def get_flood_impact(self, flood_stage: int) -> str:
        """Describe flood impact level for this agent"""
        impact_levels = {
            0: 'monitoring',
            1: 'water_approaching', 
            2: 'partial_flooding',
            3: 'severe_flooding'
        }
        return impact_levels.get(flood_stage, 'unknown')

class EnhancedFloodSimulation:
    """Enhanced simulation with LLM-generated message content"""
    
    def __init__(self, agents_file: str = "venice_agents.ndjson", use_llm: bool = True):
        self.agents = {}
        self.llm_generator = LLMMessageGenerator() if use_llm else None
        self.use_llm = use_llm
        self.load_agents(agents_file)
        self.message_log = []
        self.tick_snapshots = []
        self.current_tick = 0
        self.flood_stage = 0
        
    def load_agents(self, agents_file: str):
        """Load agents and convert to enhanced agents"""
        with open(agents_file, 'r') as f:
            for line in f:
                agent_data = json.loads(line)
                agent = EnhancedVeniceAgent(agent_data)
                self.agents[agent.agent_id] = agent
        
        print(f"Loaded {len(self.agents)} enhanced agents (LLM: {self.use_llm})")
    
    def generate_enhanced_message(self, sender_agent, intent: str, target: str, need: str = None):
        """Generate enhanced message with LLM content"""
        
        if self.use_llm and self.llm_generator:
            return sender_agent.generate_enhanced_message(
                intent, target, self.current_tick, self.flood_stage, 
                self.llm_generator, need
            )
        else:
            # Require LLM for enhanced simulation - no fallback content
            raise RuntimeError("Enhanced simulation requires OpenAI API key. No mock content will be generated.")
    
    def run_enhanced_scenario(self, scenario_name: str, max_ticks: int = 60, **params):
        """Run enhanced scenario with LLM-generated content"""
        print(f"\n=== Running Enhanced Scenario {scenario_name} ===")
        print(f"Debug: OpenAI API Key available: {bool(os.getenv('OPENAI_API_KEY'))}")
        
        # Reset state
        for agent in self.agents.values():
            agent.status = 'normal'
            agent.message_queue = []
            agent.unmet_needs = []
            agent.last_update_tick = 0
        
        self.message_log = []
        self.current_tick = 0
        
        # More aggressive flood progression to trigger LLM generation
        flood_progression = [0] * 10 + [1] * 10 + [2] * 20 + [3] * 20
        
        p_fail = params.get('p_fail', 0.1)
        
        for tick in range(max_ticks):
            self.current_tick = tick
            
            if tick < len(flood_progression):
                old_stage = self.flood_stage
                self.flood_stage = flood_progression[tick]
                if old_stage != self.flood_stage:
                    print(f"  Debug: Flood stage {old_stage} → {self.flood_stage} at tick {tick}")
            
            # Process sample of agents per tick (to manage LLM costs)
            active_agents = random.sample(list(self.agents.keys()), 
                                        min(15, len(self.agents)))  # More agents for testing
            
            tick_messages = 0
            for agent_id in active_agents:
                agent = self.agents[agent_id]
                
                # Update agent status more aggressively
                stage_key = f'stage_{self.flood_stage}'
                new_status = agent.risk_escalation.get(stage_key, 'emergency')
                status_changed = new_status != agent.status
                agent.status = new_status
                
                # Generate status update if status changed significantly
                if status_changed and new_status in ['critical', 'emergency']:
                    if tick % 3 == 0:  # More frequent status updates
                        print(f"  Debug: Generating status update for {agent.place_name} ({new_status})")
                        try:
                            msg = self.generate_enhanced_message(
                                agent, 'status_update', 'broadcast'
                            )
                            self.send_enhanced_message(msg, p_fail)
                            tick_messages += 1
                        except Exception as e:
                            print(f"  Debug: LLM generation failed: {e}")
                
                # Generate support requests for unmet needs
                if new_status in ['critical', 'emergency'] and tick % 5 == 0:
                    # Add unmet needs more aggressively
                    if new_status == 'emergency':
                        if 'evacuation' not in agent.unmet_needs:
                            agent.unmet_needs.append('evacuation')
                    if self.flood_stage >= 2:
                        if 'power' not in agent.unmet_needs:
                            agent.unmet_needs.append('power')
                        if 'protection' not in agent.unmet_needs:
                            agent.unmet_needs.append('protection')
                    
                    # Request support for one unmet need
                    if agent.unmet_needs:
                        need = random.choice(agent.unmet_needs)
                        partners = self.find_support_partners(agent, need)
                        
                        if partners:
                            target = random.choice(partners)
                            print(f"  Debug: Generating help request from {agent.place_name} to {target} for {need}")
                            try:
                                msg = self.generate_enhanced_message(
                                    agent, 'request_support', target, need
                                )
                                self.send_enhanced_message(msg, p_fail)
                                tick_messages += 1
                            except Exception as e:
                                print(f"  Debug: LLM generation failed: {e}")
            
            if tick % 10 == 0:
                print(f"  Tick {tick}: {tick_messages} enhanced messages generated this tick")
        
        print(f"Enhanced scenario {scenario_name} complete: {len(self.message_log)} messages")
        
        # Save enhanced results
        log_file = f"enhanced_message_log_{scenario_name}.ndjson"
        with open(log_file, 'w') as f:
            for msg in self.message_log:
                f.write(json.dumps(msg.to_dict()) + '\n')
        
        print(f"Enhanced results saved: {log_file}")
        return self.message_log
    
    def send_enhanced_message(self, message: EnhancedMessage, p_fail: float):
        """Send enhanced message with failure handling"""
        if random.random() < p_fail:
            message.success = False
        
        self.message_log.append(message)
        return message.success
    
    def find_support_partners(self, agent, need: str) -> List[str]:
        """Simple partner matching for demonstration"""
        partners = []
        
        capability_map = {
            'evacuation': ['evacuation_route', 'mobility', 'emergency_response'],
            'power': ['electricity', 'power_distribution'],
            'medical_care': ['medical_care', 'emergency_treatment'],
            'protection': ['emergency_response', 'security']
        }
        
        required_caps = capability_map.get(need, [need])
        
        for other_agent in self.agents.values():
            if (other_agent.agent_id != agent.agent_id and 
                any(cap in other_agent.capabilities for cap in required_caps)):
                partners.append(other_agent.agent_id)
        
        return partners[:3]

def create_env_template():
    """Create .env template for OpenAI API configuration"""
    env_content = """# OpenAI API Configuration for Venice Simulation
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Set organization if needed
# OPENAI_ORG_ID=your_org_id_here
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Created .env template - please add your OpenAI API key")
    else:
        print("📄 .env file already exists")

def test_enhanced_simulation():
    """Test the enhanced simulation with LLM content"""
    
    print("=== TESTING ENHANCED VENICE SIMULATION ===\n")
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  No OpenAI API key found in environment")
        print("   Creating .env template...")
        create_env_template()
        print("   Running simulation without LLM (fallback mode)")
        use_llm = False
    else:
        print("✅ OpenAI API key found - enabling LLM content generation")
        use_llm = True
    
    # Create enhanced simulation
    try:
        sim = EnhancedFloodSimulation(use_llm=use_llm)
        
        # Run a short test scenario
        messages = sim.run_enhanced_scenario('TEST', max_ticks=30, p_fail=0.1)
        
        print(f"\n📊 TEST RESULTS:")
        print(f"   Generated {len(messages)} enhanced messages")
        
        # Show sample messages
        print(f"\n📝 SAMPLE ENHANCED MESSAGES:")
        for i, msg in enumerate(messages[:5]):
            print(f"   {i+1}. [{msg.intent}] {msg.sender} → {msg.receiver}")
            print(f"      \"{msg.content}\"")
            print()
        
        # Show message distribution
        intent_counts = {}
        for msg in messages:
            intent_counts[msg.intent] = intent_counts.get(msg.intent, 0) + 1
        
        print(f"📈 MESSAGE DISTRIBUTION:")
        for intent, count in intent_counts.items():
            print(f"   {intent}: {count}")
        
        return True
        
    except FileNotFoundError:
        print("❌ venice_agents.ndjson not found")
        print("   Run: python scripts/create_venice_agents.py first")
        return False
    except Exception as e:
        print(f"❌ Error running enhanced simulation: {e}")
        return False

def create_example_agent_conversation():
    """Create example of agent-to-agent conversation"""
    
    example_conversation = [
        {
            "from": "venice_001",
            "to": "broadcast", 
            "tick": 35,
            "intent": "status_update",
            "content": "Palazzo Ducale reporting critical flooding in ground floor chambers. Tourist access blocked, structural assessment needed.",
            "payload": {
                "status": "critical",
                "place_name": "Palazzo Ducale", 
                "sector": "heritage",
                "flood_impact": "partial_flooding"
            }
        },
        {
            "from": "venice_045",
            "to": "venice_001",
            "tick": 36, 
            "intent": "request_support",
            "content": "Cannaregio Hospital monitoring your situation. Do you need evacuation assistance for staff or emergency shelter setup?",
            "payload": {
                "need": "evacuation_support",
                "urgency": "alert",
                "capabilities": ["medical_care", "emergency_treatment"]
            }
        },
        {
            "from": "venice_001", 
            "to": "venice_045",
            "tick": 37,
            "intent": "commit",
            "content": "Palazzo Ducale accepts. We can provide temporary shelter in upper floors for medical overflow if needed.",
            "payload": {
                "need": "shelter_space",
                "response_capability": ["cultural_preservation", "shelter_space"]
            }
        }
    ]
    
    # Save example
    with open("example_enhanced_conversation.json", 'w') as f:
        json.dump(example_conversation, f, indent=2)
    
    print("✅ Example conversation saved: example_enhanced_conversation.json")
    
    return example_conversation

if __name__ == "__main__":
    print("Venice Enhanced Simulation with LLM Content")
    print("===========================================")
    
    # Test the enhanced simulation
    success = test_enhanced_simulation()
    
    if success:
        # Create example conversation
        create_example_agent_conversation()
        
        print(f"\n🎉 ENHANCED SIMULATION READY!")
        print(f"📁 Files generated:")
        print(f"   - enhanced_message_log_TEST.ndjson")
        print(f"   - example_enhanced_conversation.json")
        print(f"   - .env (template if needed)")
        
        print(f"\n🔄 NEXT STEPS:")
        print(f"   1. Add your OpenAI API key to .env file")
        print(f"   2. Run enhanced scenarios with: sim.run_enhanced_scenario('A')")
        print(f"   3. Compare LLM vs structured message effectiveness")
        print(f"   4. Test stakeholder co-design of message templates")
        
    else:
        print(f"\n❌ Setup required before running enhanced simulation")
