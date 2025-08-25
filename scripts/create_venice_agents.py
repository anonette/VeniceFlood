#!/usr/bin/env python3
"""
Convert Venice risk data into agent personas for cascading flood simulation
"""

import json
import pandas as pd
import random
from pathlib import Path

def create_venice_agents():
    """Convert Venice data into agent personas for simulation"""
    
    print("=== CREATING VENICE AGENT PERSONAS ===\n")
    
    # Load the risk data
    data_dir = Path("data")
    
    # Load CSV data
    risk_df = pd.read_csv(data_dir / "venice_risk_table.csv")
    priority_df = pd.read_csv(data_dir / "Top-5_priority_assets_selected_for_tailored_scenario.csv")
    
    # Load GeoJSON for coordinates
    with open(data_dir / "venice_assets_at_risk.geojson", 'r') as f:
        geojson_data = json.load(f)
    
    # Load stakeholder routing
    with open(data_dir / "stakeholder_routes.json", 'r') as f:
        routing_config = json.load(f)
    
    # Create coordinate lookup
    coords_lookup = {}
    for feature in geojson_data['features']:
        place_name = feature['properties']['place_name']
        coords = feature['geometry']['coordinates']
        coords_lookup[place_name] = {'lon': coords[0], 'lat': coords[1]}
    
    # Create priority score lookup
    priority_lookup = {}
    for _, row in priority_df.iterrows():
        priority_lookup[row['name']] = {
            'priority_score': row['priority_score'],
            'type_enriched': row['type_enriched']
        }
    
    agents = []
    agent_id = 1
    
    print("Creating agent personas...")
    
    for _, row in risk_df.iterrows():
        place_name = row['place_name']
        sector = row['sector']
        risk = row['risk']
        
        # Get coordinates
        coords = coords_lookup.get(place_name, {'lon': 12.35, 'lat': 45.43})  # Venice center default
        
        # Get priority info if available
        priority_info = priority_lookup.get(place_name, {})
        priority_score = priority_info.get('priority_score', 1.0)  # Use 1.0 as base if not in priority data
        asset_type = priority_info.get('type_enriched', 'general_asset')
        
        # Determine agent capabilities and needs based on sector and type
        capabilities = []
        needs = []
        vulnerability = 0.5  # base vulnerability
        exposure = 0.5  # base exposure
        
        if sector == 'heritage':
            capabilities = ['cultural_value', 'tourism', 'historical_data']
            needs = ['protection', 'drainage', 'structural_support']
            vulnerability = 0.7  # heritage sites are more vulnerable
            if 'museo' in place_name.lower() or 'museum' in place_name.lower():
                capabilities.extend(['exhibition_space', 'public_education'])
                needs.extend(['climate_control', 'artifact_protection'])
                
        elif sector == 'transport':
            capabilities = ['mobility', 'access', 'evacuation_route']
            needs = ['maintenance', 'power', 'communication']
            exposure = 0.8  # transport is highly exposed
            
            if 'bus' in place_name.lower() or 'transport' in place_name.lower():
                capabilities.extend(['passenger_transport', 'route_coordination'])
            elif 'carabinieri' in place_name.lower() or 'police' in place_name.lower():
                capabilities.extend(['emergency_response', 'coordination', 'security'])
                needs.extend(['communication', 'vehicle_access'])
            elif 'vigili' in place_name.lower() or 'fire' in place_name.lower():
                capabilities.extend(['emergency_response', 'rescue', 'pumping'])
                needs.extend(['water_access', 'vehicle_access'])
        
        # Special types from enriched data
        if asset_type == 'power_substation':
            capabilities.extend(['electricity', 'power_distribution'])
            needs.extend(['flood_protection', 'maintenance'])
            exposure = 0.9
        elif asset_type == 'hospital':
            capabilities.extend(['medical_care', 'emergency_treatment'])
            needs.extend(['power', 'water', 'medical_supplies', 'access'])
            vulnerability = 0.3  # hospitals are built to be resilient
        elif asset_type == 'school':
            capabilities.extend(['shelter_space', 'community_gathering'])
            needs.extend(['protection', 'emergency_supplies'])
        elif asset_type == 'museum':
            capabilities.extend(['cultural_preservation', 'shelter_space'])
            needs.extend(['climate_control', 'artifact_protection'])
        
        # Flood risk escalation rules (personalized per agent)
        risk_escalation = {
            'stage_0': 'normal',
            'stage_1': 'alert' if vulnerability > 0.6 else 'normal',
            'stage_2': 'critical' if vulnerability > 0.4 else 'alert',
            'stage_3': 'emergency'
        }
        
        # Communication preferences based on real sector data
        comm_prefs = {
            'broadcast_threshold': 'alert' if sector == 'transport' else 'critical',
            'direct_partners': [],
            'redundancy_factor': 2 if priority_score > 8 else 1,
            'response_delay': 1  # Fixed response delay based on sector
        }
        
        # Adjust response delay based on sector characteristics
        if sector == 'transport':
            comm_prefs['response_delay'] = 1  # Fast response for transport
        elif sector == 'heritage':
            comm_prefs['response_delay'] = 2  # Moderate response for heritage
        
        # Determine partners based on stakeholder routing
        for stakeholder, asset_types in routing_config.get('stakeholders', {}).items():
            if any(atype in asset_type or atype in sector for atype in asset_types):
                comm_prefs['stakeholder_group'] = stakeholder
                break
        else:
            comm_prefs['stakeholder_group'] = 'general'
        
        agent = {
            'agent_id': f"venice_{agent_id:03d}",
            'place_name': place_name,
            'coordinates': coords,
            'sector': sector,
            'asset_type': asset_type,
            'priority_score': round(priority_score, 2),
            'vulnerability': round(vulnerability, 2),
            'exposure': round(exposure, 2),
            'capabilities': capabilities,
            'needs': needs,
            'risk_escalation': risk_escalation,
            'comm_prefs': comm_prefs,
            'initial_status': 'normal',
            'message_queue': [],
            'unmet_needs': [],
            'last_update_tick': 0
        }
        
        agents.append(agent)
        agent_id += 1
    
    # Save agents to NDJSON format
    output_file = "venice_agents.ndjson"
    with open(output_file, 'w') as f:
        for agent in agents:
            f.write(json.dumps(agent) + '\n')
    
    print(f"Created {len(agents)} agent personas")
    print(f"Saved to: {output_file}")
    
    # Print summary statistics
    sectors = {}
    stakeholder_groups = {}
    for agent in agents:
        sector = agent['sector']
        sectors[sector] = sectors.get(sector, 0) + 1
        
        stakeholder = agent['comm_prefs']['stakeholder_group']
        stakeholder_groups[stakeholder] = stakeholder_groups.get(stakeholder, 0) + 1
    
    print(f"\nAgent Distribution:")
    print(f"By Sector: {sectors}")
    print(f"By Stakeholder Group: {stakeholder_groups}")
    
    print(f"\nCapability Distribution:")
    all_capabilities = {}
    for agent in agents:
        for cap in agent['capabilities']:
            all_capabilities[cap] = all_capabilities.get(cap, 0) + 1
    
    top_capabilities = sorted(all_capabilities.items(), key=lambda x: x[1], reverse=True)[:10]
    for cap, count in top_capabilities:
        print(f"  {cap}: {count} agents")
    
    return agents

if __name__ == "__main__":
    create_venice_agents()
