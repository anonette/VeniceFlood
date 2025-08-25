import csv
import json
from pathlib import Path

# Converts venice_risk_table.csv into a GeoJSON by matching place_name to venice_risk_layer.geojson coordinates.
# Writes data/venice_assets_at_risk.geojson

root = Path("c:/dev/VeniceData")
data_dir = root / 'data'
csv_path = data_dir / 'venice_risk_table.csv'
layer_path = data_dir / 'venice_risk_layer.geojson'
out_path = data_dir / 'venice_assets_at_risk.geojson'

# load geojson layer into dict by place_name -> coordinates
place_coords = {}
if layer_path.exists():
    with open(layer_path, 'r', encoding='utf-8') as f:
        gj = json.load(f)
        for feat in gj.get('features', []):
            props = feat.get('properties', {})
            name = props.get('place_name') or props.get('name')
            geom = feat.get('geometry')
            if name and geom and geom.get('type') == 'Point':
                place_coords[name.strip().lower()] = geom.get('coordinates')

features = []
with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        name = row.get('place_name') or row.get('place') or row.get('Place')
        if not name:
            continue
        key = name.strip().lower()
        coords = place_coords.get(key)
        feat = {
            'type': 'Feature',
            'properties': row,
            'geometry': None
        }
        if coords:
            feat['geometry'] = { 'type': 'Point', 'coordinates': coords }
        features.append(feat)

geo = { 'type': 'FeatureCollection', 'features': features }
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(geo, f, ensure_ascii=False, indent=2)
print(f'Wrote {out_path} with {len(features)} features ({sum(1 for f in features if f["geometry"]) } with geometry)')
