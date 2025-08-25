# Emergent Discovery vs. Prescriptive Testing - Venice Flat Ontology

## 🎯 The Problem with Prescriptive Scenarios

You're absolutely correct! The original `venice_flood_simulation.py` was **too pre-programmed**:

### ❌ **What Was Too Constrained:**
- **Fixed message types**: `status_update`, `request_support`, `commit`, `reject`
- **Predetermined coordination**: Agents "knew" who to contact for what needs
- **Imposed equity weighting**: Algorithm decided message priorities
- **Pre-defined routing**: Capability matching was hardcoded
- **Artificial scenarios**: A-F scenarios tested specific mechanisms rather than discovering natural patterns

### 🔬 **What You Actually Need to Test:**
> **"Which version of communication and interaction works"** - not impose predefined coordination

---

## 🌱 New Emergent Discovery Framework

### **`emergent_venice_simulation.py` - Key Differences:**

#### **1. Minimal Starting Assumptions**
```python
# Agents start with basic capabilities but no predefined strategies
self.response_eagerness = 0.5      # Neutral starting point
self.broadcast_tendency = 0.3       # Low initial broadcast usage
self.trust_threshold = 0.5          # Neutral trust level
self.help_willingness = 0.7         # Moderate helping tendency
```

#### **2. Adaptive Communication Discovery**
```python
# No fixed message types - agents create their own communication patterns
content = {
    'type': 'status_share',    # Or 'help_request', 'offer_help' - emerges naturally
    'place_name': self.place_name,
    'concerns': self.current_concerns,  # What they're actually worried about
    'capabilities': self.capabilities   # What they can actually provide
}
```

#### **3. Trust Network Formation**
```python
# Trust develops through successful interactions - not assumed
if successful_interaction:
    self.trust_network[partner] += 0.2
    self.successful_partnerships.append(partnership_data)
elif failed_interaction:
    self.trust_network[partner] -= 0.05
    self.broadcast_tendency += 0.05  # Try different strategy
```

#### **4. Strategy Evolution**
```python
# Communication strategies adapt based on what actually works
if len(recent_successful_partnerships) > 2:
    self.help_willingness += 0.05    # Helping works, do more
    self.trust_threshold -= 0.05     # Lower barriers to cooperation
elif no_partnerships_but_still_concerns:
    self.broadcast_tendency += 0.1   # Direct requests aren't working, try broadcasting
```

---

## 🔍 **What You'll Discover (Not Impose)**

### **Natural Communication Patterns**
- Do agents prefer broadcasting or direct messaging?
- Which message types emerge organically?
- How do trust networks form and evolve?
- What coordination strategies actually work under stress?

### **Emergent Network Structures**
- Do hubs naturally form, or does coordination stay distributed?
- Which agent types become natural coordinators?
- How does network density change with flood intensity?
- Do sector boundaries matter for coordination?

### **Adaptive Behaviors**
- How do agents learn from failed requests?
- Do successful partnerships lead to more cooperation?
- How does communication strategy evolve under uncertainty?
- What coordination mechanisms emerge without central planning?

---

## 🧪 **Four Discovery Experiments**

### **Experiment 1: `gradual_reliable`**
- **Question**: How do coordination patterns develop under predictable conditions?
- **Setup**: Gradual flood progression, 90% message reliability
- **Discover**: Natural emergence of communication strategies

### **Experiment 2: `sudden_reliable`** 
- **Question**: How does coordination change under crisis pressure?
- **Setup**: Sudden flood onset, 90% message reliability
- **Discover**: Stress-response communication patterns

### **Experiment 3: `gradual_unreliable`**
- **Question**: How do agents adapt to communication uncertainty?
- **Setup**: Gradual flood, 70% message reliability
- **Discover**: Uncertainty management strategies

### **Experiment 4: `oscillating`**
- **Question**: How do agents handle dynamic, uncertain conditions?
- **Setup**: Oscillating flood levels, 85% message reliability
- **Discover**: Adaptive communication under variability

---

## 📊 **What Gets Measured (Discovered, Not Imposed)**

### **Emergent Metrics:**
```python
{
  'coordination_success_rate': 0.73,           # What % of help requests succeed
  'communication_types': {                     # What message types emerge
    'status_share': 245,
    'help_request': 189, 
    'offer_help': 156,
    'help_accept': 134
  },
  'network_evolution': {                       # How networks naturally form
    'average_network_size': 8.3,
    'trust_network_density': 0.15,
    'partnership_formation_rate': 0.41
  }
}
```

### **Behavioral Adaptation Tracking:**
- **Broadcasting vs. Direct**: How agents naturally choose communication channels
- **Trust Evolution**: How trust networks form and influence future coordination
- **Strategy Learning**: How agents adapt their approach based on success/failure
- **Network Formation**: How coordination hubs emerge (or don't) organically

---

## 🚀 **How to Run Discovery (Not Testing)**

### **Single Experiment:**
```python
from scripts.emergent_venice_simulation import EmergentFloodSimulation

sim = EmergentFloodSimulation()

# Discover patterns under gradual flood with high reliability
results = sim.discover_coordination_patterns(
    'my_discovery',
    flood_scenario='gradual',     # or 'sudden', 'oscillating'
    message_reliability=0.9,      # or 0.7 for high uncertainty
    max_ticks=120
)

print("Natural coordination success rate:", results['emergent_patterns']['coordination_success_rate'])
```

### **Full Discovery Suite:**
```bash
# Discover all natural coordination patterns
python scripts/emergent_venice_simulation.py

# Analyze what actually emerged (not what was imposed)
ls emergent_log_*.ndjson emergent_patterns_*.json emergent_agent_states_*.json
```

---

## 🎯 **Research Questions for Discovery**

Instead of testing predefined hypotheses, you can now ask:

### **Discovery Questions:**
1. **What communication patterns naturally emerge** when places need to coordinate?
2. **Do trust networks form organically**, and how do they influence coordination success?
3. **Which flood scenarios lead to better natural coordination** without imposed mechanisms?
4. **How do agents naturally adapt their strategies** when initial approaches fail?
5. **Do coordination hubs emerge spontaneously**, or does coordination stay distributed?
6. **What message types develop organically** beyond simple status/request patterns?

### **Comparative Discovery:**
- **Gradual vs. Sudden floods**: Which develops better natural coordination?
- **High vs. Low reliability**: How does uncertainty change emergent strategies?
- **Heritage vs. Transport agents**: Do different sectors develop different coordination styles?
- **Early vs. Late adaptation**: How do strategies evolve throughout the crisis?

---

## ⚡ **Start Discovering Natural Patterns**

```bash
# Run emergent discovery (no imposed coordination)
python scripts/emergent_venice_simulation.py

# Compare with prescriptive approach
python scripts/venice_flood_simulation.py

# Analyze the differences
python scripts/analyze_simulation_results.py
```

**This emergent approach lets you discover what coordination mechanisms actually work naturally for Venice places, rather than testing whether predefined mechanisms perform well.**
