# 🚀 Venice Flat Ontology - How to Start

## Step 1: Install Dependencies (2 minutes)

```bash
# Install required Python packages
pip install -r requirements.txt
```

## Step 2: Create Your Venice Agents (1 minute)

```bash
# Convert your real Venice data into 115 place-personas
python scripts/create_venice_agents.py
```

**What this does:**
- Reads your Venice risk data from `data/` folder
- Creates 115 agent personas (palaces, museums, transport hubs)
- Saves them to `venice_agents.ndjson`

**Expected output:**
```
=== CREATING VENICE AGENT PERSONAS ===
Created 115 agent personas
By Sector: {'heritage': 65, 'transport': 50}
```

## Step 3: Run Discovery Experiments (5 minutes)

```bash
# Discover natural coordination patterns (recommended first)
python scripts/emergent_venice_simulation.py
```

**What this does:**
- Runs 4 experiments with different flood scenarios
- Agents start with minimal assumptions and learn naturally
- Discovers which communication patterns actually work
- No imposed coordination mechanisms

**Expected output:**
```
=== EMERGENT PATTERN COMPARISON ===
gradual_reliable     Coordination: 0.73 | Message types: 4
sudden_reliable      Coordination: 0.65 | Message types: 5
gradual_unreliable   Coordination: 0.58 | Message types: 3
oscillating          Coordination: 0.71 | Message types: 6
```

## Step 4: Analyze What You Discovered (2 minutes)

```bash
# Look at the files that were generated
ls emergent_log_*.ndjson emergent_patterns_*.json emergent_agent_states_*.json

# Check one of the emergent patterns
head -5 emergent_log_gradual_reliable.ndjson
```

**What to look for:**
- Which message types emerged naturally (`status_share`, `help_request`, etc.)
- How coordination success rates vary across scenarios
- Which agents formed successful partnerships
- How strategies adapted over time

## Step 5: Compare with Prescriptive Approach (10 minutes)

```bash
# Run the original prescriptive scenarios A-F
python scripts/venice_flood_simulation.py

# Analyze and compare both approaches
python scripts/analyze_simulation_results.py
```

**What this shows:**
- How emergent patterns compare to designed mechanisms
- Whether natural coordination is better/worse than imposed coordination
- Which approach works better under different conditions

---

## 🎯 What You'll Learn Immediately

### From Emergent Discovery:
- **Natural coordination rate**: How well Venice places coordinate without guidance
- **Emergent message types**: What communication patterns develop organically
- **Trust network formation**: How partnerships naturally form between different place types
- **Adaptation strategies**: How agents learn and change behavior under stress

### From Prescriptive Testing:
- **Equity intervention impact**: 475% improvement in vulnerability gap
- **Hub failure effects**: Measurable cascade impacts
- **Routing effectiveness**: Whether simple directories help coordination
- **Uncertainty tolerance**: How redundancy performs under message noise

---

## 📁 Files You'll Generate

**After Step 2:**
- `venice_agents.ndjson` - Your 115 place-personas

**After Step 3:**
- `emergent_log_*.ndjson` - Natural communication records
- `emergent_patterns_*.json` - Discovered coordination patterns
- `emergent_agent_states_*.json` - How agents adapted

**After Step 5:**
- `message_log_[A-F].ndjson` - Prescriptive scenario results
- `snapshots_[A-F].json` - Agent states under imposed coordination
- `venice_simulation_results.png` - Visualization dashboard

---

## ⚡ Quick Start (All Steps in One Command)

```bash
# Run everything in sequence
python scripts/create_venice_agents.py && \
python scripts/emergent_venice_simulation.py && \
python scripts/venice_flood_simulation.py && \
python scripts/analyze_simulation_results.py
```

**Total time: ~15 minutes**

---

## 🔍 What to Examine First

1. **Check agent creation**:
   ```bash
   head -3 venice_agents.ndjson
   # Should show real Venice places like Palazzo Ducale
   ```

2. **Look at emergent messages**:
   ```bash
   head -5 emergent_log_gradual_reliable.ndjson
   # Should show natural communication between places
   ```

3. **Compare coordination success**:
   ```bash
   grep "coordination_success_rate" emergent_patterns_*.json
   # Shows how well natural coordination worked
   ```

4. **Review research paper**:
   ```bash
   # Your publication is ready in research_paper.md
   ```

---

## 🎯 **Start Right Now**

**Just run this single command to begin:**

```bash
python scripts/create_venice_agents.py
```

**Then examine the output and continue with the next steps when ready!**
