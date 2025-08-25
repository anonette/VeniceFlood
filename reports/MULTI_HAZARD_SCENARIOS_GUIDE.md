# Multi-Hazard Cyber-Physical Cascade Scenarios

## 🎯 Overview

This framework extends the Venice Flat Ontology simulation to model complex **multi-hazard cyber-physical cascades**. Built on top of the proven Venice flood simulation, it enables testing of compound disasters where cyber attacks, infrastructure failures, and natural hazards interact through system interdependencies.

## 🌊 Key Innovation: Cyber-Physical Cascade Modeling

### **What Makes This Different**
- **Real Venice agents**: 115 authentic place-personas with actual coordinates and capabilities
- **Cyber-physical interdependencies**: Explicit modeling of how digital and physical systems interact
- **Dynamic cascade propagation**: Failures automatically cascade through dependent systems
- **Multi-hazard scenarios**: Compound events that unfold over time with realistic dependencies
- **Agent-level impacts**: Individual places experience different disruption effects

### **Core Cascade Concepts**
1. **System Interdependencies**: Power → Pumps → Digital Systems → Communications
2. **Propagation Delays**: Realistic time for cascade effects to spread (1-5 ticks)
3. **Coupling Strength**: How tightly systems are connected (0.0 to 1.0)
4. **Failure Thresholds**: At what degradation point does one system affect another
5. **Bidirectional Effects**: Some dependencies work both ways

---

## 📋 Available Scenarios

### **1. Ransomware Flood (ransomware_flood)**
**The Perfect Storm**: Cyber attack during Venice acqua alta

**Event Timeline:**
- **Tick 10**: Major flood begins (120cm acqua alta)
- **Tick 20**: Ransomware attack targets pump systems
- **Tick 25**: Automated pumps fail, manual operation only
- **Tick 30**: Communication systems overwhelmed
- **Tick 40**: Public panic from failed flood response

**Key Features:**
- Demonstrates cyber-physical vulnerability
- Tests coordination under dual stress
- Shows cascade from cyber to physical to social

**Expected Results:**
- High message failure rates due to communication overload
- Severe pump system degradation
- Social disruption amplifying coordination failures

### **2. Power Surge Cascade (power_surge_cascade)**
**Grid Instability Ripple Effects**: Electrical surge cascading through Venice

**Event Timeline:**
- **Tick 15**: Electrical grid surge damages connected systems
- **Tick 18**: Flood monitoring sensors go offline (blind operations)
- **Tick 20**: Pump systems operate at 30% capacity

**Key Features:**
- Power-dependent system failures
- Sensor blackouts creating information gaps
- Infrastructure degradation under stress

**Expected Results:**
- Widespread power-dependent system failures
- Loss of situational awareness
- Reduced flood response capacity

### **3. Cyber Storm Perfect (cyber_storm_perfect)**
**Worst Case Scenario**: Sophisticated nation-state attack during exceptional flood

**Event Timeline:**
- **Tick 5**: Exceptional acqua alta (160cm) + storm surge
- **Tick 25**: Nation-state cyber attack (zero-day exploits)
- **Tick 30**: Supply chain collapse - no replacement equipment

**Key Features:**
- Multiple simultaneous stressors
- Sophisticated attack vectors
- Complete system breakdown scenario

**Expected Results:**
- Maximum system disruption
- Highest cascade propagation
- Complete coordination breakdown

### **4. Communication Breakdown (communication_breakdown)**
**Digital Isolation**: Progressive communication network failure

**Event Timeline:**
- **Tick 35**: Cellular towers flooded, capacity reduced
- **Tick 45**: Internet backbone damage, digital isolation

**Key Features:**
- Progressive communication degradation
- Physical infrastructure flooding
- Information isolation effects

### **5. Infrastructure Aging (infrastructure_aging)**
**Stress Fractures**: Deferred maintenance failures under flood stress

**Event Timeline:**
- **Tick 50**: Aging infrastructure fails under flood stress

**Key Features:**
- Realistic infrastructure limitations
- Stress-induced component failures
- Maintenance neglect consequences

### **6. Social Media Panic (social_media_panic)**
**Information Warfare**: Viral misinformation amplifying disaster

**Event Timeline:**
- **Tick 60**: Viral misinformation causes evacuation panic

**Key Features:**
- Social amplification of disaster
- Misinformation spread modeling
- Behavioral disruption effects

### **7. Supply Chain Flood (supply_chain_flood)**
**Logistics Breakdown**: Equipment unavailable when needed most

**Event Timeline:**
- **Tick 40**: Supply chain disruption affects flood response equipment

**Key Features:**
- Resource availability constraints
- Equipment replacement delays
- Logistical vulnerability

### **8. Sensor Network Failure (sensor_network_failure)**
**Blind Spots**: False data creating coordination chaos

**Event Timeline:**
- **Tick 25**: Flood sensor network provides false/corrupted data

**Key Features:**
- Sensor calibration drift
- Data corruption effects
- False information propagation

---

## 🔧 System Architecture

### **Cyber-Physical System States**
The framework tracks 12 critical systems:
- `power_grid`: Electrical infrastructure
- `water_system`: Flood management systems
- `communication_network`: Emergency communications
- `transport_network`: Evacuation routes
- `emergency_services`: Response coordination
- `digital_infrastructure`: Control systems
- `pumping_stations`: Flood pumps
- `flood_barriers`: Physical barriers
- `sensor_network`: Monitoring systems
- `emergency_communications`: Priority channels
- `public_wifi`: Public connectivity
- `cellular_network`: Mobile communications

### **Interdependency Types**
- **Functional**: Direct operational dependency (power → pumps)
- **Cyber**: Digital system dependency (control systems → infrastructure)
- **Physical**: Physical damage propagation (flooding → electrical)
- **Logical**: Information/coordination dependency (comms → emergency response)

### **Agent Cascade Effects**
Individual Venice agents experience:
- `cyber_disruption`: Digital system compromise (0.0-1.0)
- `power_disruption`: Electrical system failure (0.0-1.0)
- `comm_disruption`: Communication degradation (0.0-1.0)
- `effectiveness`: Overall operational capacity (0.0-1.0)
- `message_failure_rate`: Dynamic communication failure probability

---

## 📊 Metrics and Analysis

### **Enhanced Cascade Metrics**
- **Total cascade events**: Number of triggered cascade events
- **System degradation**: Per-system operational degradation
- **Cascade propagations**: Secondary failures from interdependencies
- **Max simultaneous events**: Peak concurrent disruptions
- **Cyber disruption impact**: Severity of cyber attack effects
- **Infrastructure resilience**: System recovery capability

### **Traditional Coordination Metrics**
- **Delivery ratio**: Successful message percentage
- **Response time**: Median time from request to commitment
- **Unmet needs**: Final coordination failures
- **Equity gap**: Vulnerable vs resilient population outcomes

### **Cross-Scenario Comparisons**
- **Most disruptive**: Scenario causing maximum system degradation
- **Most resilient**: Scenario with best recovery
- **Highest cascade**: Scenario with most propagation events
- **Communication impact**: Average delivery ratio across scenarios

---

## 🚀 Usage Instructions

### **Basic Execution**
```python
from scripts.multi_hazard_cascade_scenarios import MultiHazardCascadeSimulation

# Initialize simulation
sim = MultiHazardCascadeSimulation()

# Run single scenario
results = sim.run_multi_hazard_scenario("ransomware_flood", max_ticks=120)
sim.save_cascade_results("ransomware_flood")

print(f"Cascade events: {results['total_cascade_events']}")
print(f"System degradation: {results['system_degradation']}")
```

### **Run All Scenarios**
```python
from scripts.multi_hazard_cascade_scenarios import run_multi_hazard_scenarios

# Execute comprehensive analysis
results = run_multi_hazard_scenarios()

# Results automatically saved to:
# - cascade_message_log_[scenario].ndjson
# - cascade_snapshots_[scenario].json  
# - cascade_events_[scenario].json
# - interdependencies_[scenario].json
# - multi_hazard_cascade_report.json
```

### **Command Line Execution**
```bash
# Activate Venice environment
venice_env\Scripts\activate.bat

# Run comprehensive multi-hazard analysis
python scripts/multi_hazard_cascade_scenarios.py
```

---

## 📈 Expected Research Insights

### **Cyber-Physical Vulnerability Patterns**
- Which system interdependencies are most critical?
- How do cyber attacks amplify physical disaster impacts?
- What cascade propagation delays are most dangerous?

### **Coordination Under Compound Stress**
- How does multi-hazard stress affect agent coordination?
- Which communication patterns emerge under cascade failures?
- Do established coordination protocols break under compound stress?

### **Infrastructure Resilience Design**
- Which system architectures best resist cascade failures?
- How much redundancy is needed for cyber-physical resilience?
- What early warning indicators predict cascade events?

### **Emergency Management Insights**
- Which scenarios pose greatest threat to Venice emergency response?
- How should emergency protocols adapt to cyber-physical cascades?
- What backup systems are most critical during compound disasters?

---

## 🎯 Stakeholder Applications

### **Venice Emergency Management**
- **Tabletop exercises**: Use realistic cascade scenarios for training
- **Protocol testing**: Test emergency procedures under compound stress
- **Resource planning**: Identify critical backup systems needed
- **Risk assessment**: Quantify cyber-physical cascade vulnerabilities

### **Critical Infrastructure Operators**
- **Vulnerability assessment**: Test interdependency resilience
- **Backup system design**: Identify critical redundancy needs
- **Cascade prevention**: Design circuit breakers for failure propagation
- **Recovery planning**: Optimize system restoration sequences

### **Policy and Planning**
- **Regulation development**: Inform cyber-physical security requirements
- **Investment priorities**: Identify most critical infrastructure upgrades
- **Inter-agency coordination**: Test multi-organization response protocols
- **Public communication**: Develop crisis communication strategies

### **Research and Academic**
- **Cascade theory testing**: Validate interdependency models
- **Coordination science**: Study agent behavior under extreme stress
- **Resilience measurement**: Develop metrics for compound disaster recovery
- **Multi-hazard methodology**: Extend framework to other cities/hazards

---

## 🔬 Technical Implementation Details

### **Cascade Event Structure**
```python
@dataclass
class CascadeEvent:
    event_id: str                    # Unique identifier
    hazard_type: HazardType          # Type of hazard (cyber, power, etc.)
    trigger_tick: int                # When event activates
    duration: int                    # How long event lasts
    affected_agents: List[str]       # Which Venice agents affected
    severity: float                  # Impact intensity (0.0-1.0)
    dependencies: List[str]          # Events this depends on
    cyber_physical_links: Dict       # System interaction details
    description: str                 # Human-readable description
```

### **System Interdependency Structure**
```python
@dataclass 
class SystemInterdependency:
    dependency_id: str               # Unique identifier
    system_a: str                    # Source system
    system_b: str                    # Dependent system
    dependency_type: str             # functional/cyber/physical/logical
    coupling_strength: float         # How strongly connected (0.0-1.0)
    failure_threshold: float         # When system_a failure affects system_b
    propagation_delay: int           # Ticks for cascade to propagate
    bidirectional: bool              # Whether dependency works both ways
```

### **Enhanced Agent State Tracking**
Each Venice agent tracks additional cascade effects:
- Real-time disruption levels for cyber/power/communication systems
- Dynamic message failure probabilities based on active disruptions
- Effectiveness degradation from infrastructure failures
- Capability-specific impacts (pumps vs coordination vs monitoring)

---

## 📋 Next Steps and Extensions

### **Immediate Enhancements**
1. **Validation with Venice experts**: Test scenarios with actual emergency managers
2. **Calibration with real data**: Adjust cascade parameters using historical incidents
3. **Additional scenarios**: Create scenarios for specific Venice vulnerabilities
4. **Multi-city adaptation**: Extend framework to other flood-prone cities

### **Advanced Research Directions**
1. **Machine learning integration**: Train agents to adapt to cascade patterns
2. **Real-time data feeds**: Connect to actual Venice sensor networks
3. **Predictive cascade detection**: Early warning systems for compound disasters
4. **Policy optimization**: Test different coordination protocols and regulations

### **Stakeholder Engagement**
1. **Venice demonstration**: Present framework to city emergency management
2. **Workshop series**: Co-design scenarios with local experts  
3. **Training integration**: Incorporate into emergency management training programs
4. **Academic publication**: Share methodology and findings with disaster research community

---

## 🎉 Framework Significance

This multi-hazard cascade framework represents a **breakthrough in compound disaster modeling** by:

✅ **Combining realistic place-based agents** with sophisticated system interdependencies  
✅ **Modeling cyber-physical interactions** that are increasingly critical in smart cities  
✅ **Testing coordination protocols** under compound stress conditions  
✅ **Providing actionable insights** for emergency management and infrastructure planning  
✅ **Creating reproducible scenarios** for training and policy development  

The framework transforms abstract cascade theory into **concrete, testable scenarios** that emergency managers can use immediately while advancing academic understanding of compound disaster dynamics.

---

*Framework developed as extension of Venice Flat Ontology simulation*  
*Building on 192,807+ simulated messages and 115 authentic Venice place-personas*  
*Ready for validation and real-world application*
