#!/usr/bin/env python3
"""
Analyze Venice data files for consistency and quality
"""

import json
import pandas as pd
import os
from pathlib import Path

def analyze_venice_data():
    """Analyze all Venice data files for consistency and quality issues"""
    
    print("=== VENICE DATA ANALYSIS ===\n")
    
    data_dir = Path("data")
    
    # Check if data directory exists
    if not data_dir.exists():
        print("❌ Error: data directory not found")
        return
        
    print("📁 Data Directory Contents:")
    print("-" * 40)
    
    files_found = {}
    for file_path in data_dir.iterdir():
        if file_path.is_file():
            file_size = file_path.stat().st_size
            files_found[file_path.suffix] = files_found.get(file_path.suffix, 0) + 1
            print(f"  {file_path.name} ({file_size:,} bytes)")
    
    print(f"\n📊 File Type Summary:")
    for ext, count in files_found.items():
        print(f"  {ext or 'no extension'}: {count} files")
    
    print("\n" + "="*60)
    
    # Analyze GeoJSON files
    print("🗺️  ANALYZING GEOJSON FILES")
    print("-" * 40)
    
    geojson_files = [
        "export (1).geojson",
        "export (2).geojson", 
        "venice_assets_at_risk.geojson",
        "venice_risk_layer.geojson"
    ]
    
    geojson_data = {}
    for filename in geojson_files:
        filepath = data_dir / filename
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                geojson_data[filename] = data
                
                # Basic stats
                feature_count = len(data.get('features', []))
                print(f"\n📄 {filename}:")
                print(f"  Features: {feature_count}")
                
                if feature_count > 0:
                    # Analyze properties
                    properties_keys = set()
                    geometry_types = set()
                    
                    for feature in data['features']:
                        if 'properties' in feature:
                            properties_keys.update(feature['properties'].keys())
                        if 'geometry' in feature:
                            geometry_types.add(feature['geometry']['type'])
                    
                    print(f"  Property keys: {sorted(properties_keys)}")
                    print(f"  Geometry types: {sorted(geometry_types)}")
                    
                    # Sample coordinates range
                    coords = []
                    for feature in data['features'][:10]:  # Sample first 10
                        if feature['geometry']['type'] == 'Point':
                            coords.append(feature['geometry']['coordinates'])
                    
                    if coords:
                        lons = [c[0] for c in coords]
                        lats = [c[1] for c in coords]
                        print(f"  Sample coordinates range: Lon {min(lons):.4f}-{max(lons):.4f}, Lat {min(lats):.4f}-{max(lats):.4f}")
                        
            except Exception as e:
                print(f"❌ Error reading {filename}: {e}")
        else:
            print(f"❌ File not found: {filename}")
    
    print("\n" + "="*60)
    
    # Analyze CSV files
    print("📊 ANALYZING CSV FILES")
    print("-" * 40)
    
    csv_files = [
        "Top-5_priority_assets_selected_for_tailored_scenario.csv",
        "venice_risk_table.csv"
    ]
    
    csv_data = {}
    for filename in csv_files:
        filepath = data_dir / filename
        if filepath.exists():
            try:
                df = pd.read_csv(filepath)
                csv_data[filename] = df
                
                print(f"\n📄 {filename}:")
                print(f"  Shape: {df.shape} (rows, columns)")
                print(f"  Columns: {list(df.columns)}")
                
                # Check for missing values
                missing_values = df.isnull().sum()
                if missing_values.any():
                    print(f"  Missing values: {dict(missing_values[missing_values > 0])}")
                else:
                    print("  ✅ No missing values")
                    
                # Show sample data
                print(f"  Sample data:")
                for i, row in df.head(3).iterrows():
                    print(f"    Row {i}: {dict(row)}")
                    
            except Exception as e:
                print(f"❌ Error reading {filename}: {e}")
        else:
            print(f"❌ File not found: {filename}")
    
    print("\n" + "="*60)
    
    # Analyze JSON configuration
    print("⚙️  ANALYZING CONFIGURATION FILES")
    print("-" * 40)
    
    config_file = "stakeholder_routes.json"
    filepath = data_dir / config_file
    if filepath.exists():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print(f"\n📄 {config_file}:")
            print(f"  Routing version: {config.get('routing_version', 'N/A')}")
            print(f"  Stakeholders: {list(config.get('stakeholders', {}).keys())}")
            
            for stakeholder, assets in config.get('stakeholders', {}).items():
                print(f"    {stakeholder}: {assets}")
            
            default_broadcast = config.get('default_broadcast', [])
            print(f"  Default broadcast: {default_broadcast}")
            
        except Exception as e:
            print(f"❌ Error reading {config_file}: {e}")
    else:
        print(f"❌ File not found: {config_file}")
    
    print("\n" + "="*60)
    
    # Cross-reference analysis
    print("🔍 CROSS-REFERENCE ANALYSIS")
    print("-" * 40)
    
    # Check if export files are identical
    if "export (1).geojson" in geojson_data and "export (2).geojson" in geojson_data:
        export1 = geojson_data["export (1).geojson"]
        export2 = geojson_data["export (2).geojson"]
        
        if export1 == export2:
            print("✅ export (1).geojson and export (2).geojson are identical")
        else:
            print("⚠️  export (1).geojson and export (2).geojson differ")
            print(f"    Export 1 features: {len(export1.get('features', []))}")
            print(f"    Export 2 features: {len(export2.get('features', []))}")
    
    # Check assets at risk vs risk layer
    if "venice_assets_at_risk.geojson" in geojson_data and "venice_risk_layer.geojson" in geojson_data:
        assets = geojson_data["venice_assets_at_risk.geojson"]
        risk_layer = geojson_data["venice_risk_layer.geojson"]
        
        if assets == risk_layer:
            print("✅ venice_assets_at_risk.geojson and venice_risk_layer.geojson are identical")
        else:
            print("⚠️  venice_assets_at_risk.geojson and venice_risk_layer.geojson differ")
            print(f"    Assets features: {len(assets.get('features', []))}")
            print(f"    Risk layer features: {len(risk_layer.get('features', []))}")
    
    # Check CSV vs GeoJSON consistency
    if "venice_risk_table.csv" in csv_data and "venice_assets_at_risk.geojson" in geojson_data:
        risk_csv = csv_data["venice_risk_table.csv"]
        risk_geojson = geojson_data["venice_assets_at_risk.geojson"]
        
        csv_places = set(risk_csv['place_name'].tolist())
        geojson_places = set()
        
        for feature in risk_geojson['features']:
            if 'place_name' in feature['properties']:
                geojson_places.add(feature['properties']['place_name'])
        
        print(f"\n🔄 CSV vs GeoJSON place name comparison:")
        print(f"  CSV places: {len(csv_places)}")
        print(f"  GeoJSON places: {len(geojson_places)}")
        
        if csv_places == geojson_places:
            print("  ✅ Place names match perfectly")
        else:
            only_csv = csv_places - geojson_places
            only_geojson = geojson_places - csv_places
            
            if only_csv:
                print(f"  ⚠️  Places only in CSV: {len(only_csv)}")
                for place in list(only_csv)[:5]:
                    print(f"    - {place}")
                    
            if only_geojson:
                print(f"  ⚠️  Places only in GeoJSON: {len(only_geojson)}")
                for place in list(only_geojson)[:5]:
                    print(f"    - {place}")
    
    print("\n" + "="*60)
    print("📋 SUMMARY AND RECOMMENDATIONS")
    print("-" * 40)
    
    # Summarize findings
    issues_found = []
    recommendations = []
    
    # Check for coordinate validity (Venice should be around 12.3°E, 45.4°N)
    venice_lon_range = (12.0, 12.6)
    venice_lat_range = (45.0, 45.6)
    
    for filename, data in geojson_data.items():
        if 'features' in data:
            for feature in data['features']:
                if feature['geometry']['type'] == 'Point':
                    lon, lat = feature['geometry']['coordinates']
                    if not (venice_lon_range[0] <= lon <= venice_lon_range[1]) or \
                       not (venice_lat_range[0] <= lat <= venice_lat_range[1]):
                        issues_found.append(f"Coordinates outside Venice area in {filename}")
                        break
    
    if not issues_found:
        print("✅ All coordinates appear to be in Venice area")
        recommendations.append("Data appears geographically consistent")
    
    # Check file redundancy
    if len(geojson_data) >= 2:
        recommendations.append("Consider removing duplicate GeoJSON files to reduce redundancy")
    
    recommendations.extend([
        "Satellite imagery files (.tiff) could be analyzed for temporal consistency",
        "Consider adding data validation scripts to your workflow",
        "Document the relationship between different data sources"
    ])
    
    if issues_found:
        print("\n⚠️  Issues Found:")
        for issue in issues_found:
            print(f"  - {issue}")
    
    print(f"\n💡 Recommendations:")
    for rec in recommendations:
        print(f"  - {rec}")
    
    print(f"\n🎯 Overall Assessment:")
    if not issues_found:
        print("  ✅ Data appears consistent and well-structured for Venice")
        print("  ✅ Geographic coordinates are appropriate for Venice area")
        print("  ✅ File formats are suitable for GIS/mapping applications")
    else:
        print(f"  ⚠️  Found {len(issues_found)} potential issues to investigate")

if __name__ == "__main__":
    analyze_venice_data()
