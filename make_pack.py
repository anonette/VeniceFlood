import json, csv, math, sys, os
from datetime import datetime

# --- helpers ----------------------------------------------------
def load_geojson(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def feature_iter(geojson):
    if geojson.get("type") == "FeatureCollection":
        for ft in geojson["features"]:
            yield ft
    elif geojson.get("type") == "Feature":
        yield geojson
    else:
        # bare geometry — wrap
        yield {"type":"Feature", "properties":{}, "geometry":geojson}

def centroid_of_ring(coords):
    # simple polygon centroid (not geodesic) good enough for small AOIs
    # coords: [ [x0,y0], [x1,y1], ..., [x0,y0] ]
    area, cx, cy = 0.0, 0.0, 0.0
    for i in range(len(coords)-1):
        x1,y1 = coords[i]
        x2,y2 = coords[i+1]
        a = x1*y2 - x2*y1
        area += a
        cx += (x1 + x2) * a
        cy += (y1 + y2) * a
    if abs(area) < 1e-12:
        # fallback to average
        xs = [p[0] for p in coords]
        ys = [p[1] for p in coords]
        return sum(xs)/len(xs), sum(ys)/len(ys)
    area *= 0.5
    cx /= (6*area)
    cy /= (6*area)
    return cx, cy

def geom_point(geom):
    t = geom.get("type")
    if t == "Point":
        x,y = geom["coordinates"]
        return (x,y)
    if t == "MultiPoint":
        x,y = geom["coordinates"][0]
        return (x,y)
    if t == "Polygon":
        ring = geom["coordinates"][0]
        return centroid_of_ring(ring)
    if t == "MultiPolygon":
        # centroid of first polygon's exterior ring
        ring = geom["coordinates"][0][0]
        return centroid_of_ring(ring)
    # LineString, MultiLineString etc. -> mid-point as fallback
    if t == "LineString":
        coords = geom["coordinates"]
        mid = len(coords)//2
        return coords[mid]
    if t == "MultiLineString":
        coords = geom["coordinates"][0]
        mid = len(coords)//2
        return coords[mid]
    return None

def point_in_ring(pt, ring):
    x, y = pt
    inside = False
    for i in range(len(ring)-1):
        x1,y1 = ring[i]
        x2,y2 = ring[i+1]
        if ((y1 > y) != (y2 > y)) and (x < (x2-x1)*(y-y1)/(y2-y1 + 1e-15) + x1):
            inside = not inside
    return inside

def point_in_polygon(pt, poly):
    # poly: [ [ring0], [hole1], ... ]
    if not point_in_ring(pt, poly[0]):
        return False
    # holes
    for hole in poly[1:]:
        if point_in_ring(pt, hole):
            return False
    return True

def point_in_geometry(pt, geom):
    t = geom.get("type")
    if t == "Polygon":
        return point_in_polygon(pt, geom["coordinates"])
    if t == "MultiPolygon":
        return any(point_in_polygon(pt, poly) for poly in geom["coordinates"])
    if t == "GeometryCollection":
        return any(point_in_geometry(pt, g) for g in geom["geometries"])
    # if risk layer has points/lines, treat as not containing
    return False

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.atan2(math.sqrt(a), math.sqrt(1-a))

def guess_type(name, t):
    n = (name or "").lower()
    tl = (t or "").lower()
    if tl and tl != "asset": return tl
    if any(k in n for k in ["hospital","ospedale","clinic"]): return "hospital"
    if any(k in n for k in ["substation","electric","enel","terna","grid","transformer"]): return "power_substation"
    if any(k in n for k in ["pump","pumping","impianto idrovoro"]): return "stormwater_pump"
    if any(k in n for k in ["school","liceo","scuola","universita","university"]): return "school"
    if any(k in n for k in ["bridge","ponte","ponte di","rialto"]): return "bridge"
    if any(k in n for k in ["station","stazione","vaporetto","actv","fermata"]): return "transport_stop"
    if any(k in n for k in ["church","chiesa","basilica","san marco"]): return "heritage_site"
    if any(k in n for k in ["museum","museo","galleria"]): return "museum"
    if any(k in n for k in ["water","well","cistern","fontana"]): return "water_asset"
    return "place"

# --- load inputs -------------------------------------------------
in_assets = "export (1).geojson"
in_risk   = "venice_risk_layer.geojson"
if not os.path.exists(in_assets) or not os.path.exists(in_risk):
    print("Put 'export (1).geojson' and 'venice_risk_layer.geojson' in this folder, then run again.")
    sys.exit(1)

assets_gj = load_geojson(in_assets)
risk_gj   = load_geojson(in_risk)

risk_polys = []
for ft in feature_iter(risk_gj):
    geom = ft.get("geometry") or {}
    if geom.get("type") in ("Polygon","MultiPolygon","GeometryCollection"):
        risk_polys.append((geom, (ft.get("properties") or {}).get("risk","high")))

# --- compute at-risk --------------------------------------------
at_risk = []
for ft in feature_iter(assets_gj):
    geom = ft.get("geometry") or {}
    pt = geom_point(geom)
    if not pt: 
        continue
    x, y = pt   # lon, lat
    hit = None
    for g, risk_val in risk_polys:
        if point_in_geometry(pt, g):
            hit = risk_val
            break
    if hit:
        props = ft.get("properties") or {}
        asset_id = props.get("id") or props.get("ID") or props.get("asset_id") or ft.get("id") or f"asset_{len(at_risk)}"
        name = props.get("name") or props.get("Name") or props.get("title") or str(asset_id)
        a_type = guess_type(name, props.get("type") or props.get("category") or "asset")
        at_risk.append({"id": str(asset_id), "name": str(name), "type": a_type, "lat": y, "lon": x, "risk": str(hit)})

# --- write CSV + GeoJSON ----------------------------------------
with open("venice_assets_at_risk.csv","w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["id","name","type","lat","lon","risk"])
    w.writeheader()
    for r in at_risk: w.writerow(r)

features = []
for r in at_risk:
    features.append({
        "type":"Feature",
        "geometry":{"type":"Point","coordinates":[r["lon"], r["lat"]]},
        "properties":{"id":r["id"],"name":r["name"],"type":r["type"],"risk":r["risk"]}
    })
with open("venice_assets_at_risk.geojson","w",encoding="utf-8") as f:
    json.dump({"type":"FeatureCollection","features":features}, f, ensure_ascii=False, indent=2)

# --- small reference files (scenario/schema/routes) --------------
tiny = {
  "meta":{"schema":"CascadingResilienceSim.v0.1","region":"Venice (example)","crs":"EPSG:4326","created_utc":datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")},
  "actors":[
    {"id":"eoc","label":"Municipal EOC","type":"coordination_center","capacity":{"boats":3,"ambulances":2,"pumps":1}},
    {"id":"hospital_ops","label":"Hospital Ops","type":"infrastructure_operator","capacity":{"portable_generators":1}}
  ],
  "assets":[
    {"id":"grid_sub1","label":"Low-lying Substation","type":"power_substation","loc":{"lat":45.44,"lon":12.34,"elev_m":1.2},
     "fragility":{"flood_depth_m_to_failure_prob":[[0.0,0.0],[0.3,0.15],[0.6,0.5],[1.0,0.9]]},"state":{"status":"up"}},
    {"id":"pump_p1","label":"District Pump P1","type":"stormwater_pump","loc":{"lat":45.441,"lon":12.341,"elev_m":1.1},"requires":["grid_sub1"],
     "fragility":{"flood_depth_m_to_failure_prob":[[0.0,0.0],[0.5,0.25],[0.8,0.7]]},"state":{"status":"up"}},
    {"id":"hospital_h1","label":"Hospital H1","type":"hospital","loc":{"lat":45.442,"lon":12.342,"elev_m":1.4},"requires":["grid_sub1","pump_p1"],
     "backup":{"generator_hours":8},"fragility":{"flood_depth_m_to_damage":[[0.0,0.0],[0.3,0.15],[0.7,0.45],[1.0,0.8]]},"state":{"status":"operational","patients":120}}
  ],
  "hazards":[{"id":"event_flood_001","type":"coastal_flood","description":"spring tide + storm surge (toy example)","start_utc":"2025-11-05T06:00:00Z","peak_utc":"2025-11-05T08:00:00Z","duration_h":6,
              "depth_by_asset_m":{"grid_sub1":0.7,"pump_p1":0.4,"hospital_h1":0.3}}],
  "dependencies":[
    {"from":"grid_sub1","to":"pump_p1","type":"power","critical":True},
    {"from":"grid_sub1","to":"hospital_h1","type":"power","critical":True},
    {"from":"pump_p1","to":"hospital_h1","type":"flood_mitigation","critical":True}
  ],
  "policies":[{"id":"rule_evacuate_icu","when":"hospital_h1.damage >= 0.30 || grid_sub1.status == 'down'","then":[
    {"action":"dispatch","actor":"eoc","resource":"boats","qty":2,"to":"hospital_h1"},
    {"action":"evacuate","target":"hospital_h1","count":30,"priority":"ICU"},
    {"action":"start_backup_power","target":"hospital_h1"}]}],
  "sim_settings":{"time_step_min":10,"stochastic":True,"random_seed":42}
}
with open("venice_tiny_sim_scenario.json","w",encoding="utf-8") as f: json.dump(tiny,f,ensure_ascii=False,indent=2)

schema = {
  "$schema":"https://json-schema.org/draft/2020-12/schema","title":"CascadingResilienceSim.v0.1","type":"object",
  "required":["meta","actors","assets","hazards","dependencies","policies","sim_settings"],
  "properties":{"meta":{"type":"object"},"actors":{"type":"array"},"assets":{"type":"array"},"hazards":{"type":"array"},
               "dependencies":{"type":"array"},"policies":{"type":"array"},"sim_settings":{"type":"object"}}
}
with open("venice_tiny_sim_schema.json","w",encoding="utf-8") as f: json.dump(schema,f,ensure_ascii=False,indent=2)

routes = {
  "routing_version":"v0.1",
  "stakeholders":{
    "health_authority":["hospital"],
    "utility_power":["power_substation"],
    "stormwater_ops":["stormwater_pump","hospital","school"],
    "heritage_board":["heritage_site","museum"],
    "transport_ops":["bridge","transport_stop"]
  },
  "default_broadcast":["municipality_comms","public_alerts"]
}
with open("stakeholder_routes.json","w",encoding="utf-8") as f: json.dump(routes,f,ensure_ascii=False,indent=2)

# --- tailored scenario (top-5) ----------------------------------
# score by type + proximity to San Marco
san_marco = (45.4340, 12.3397)
type_weight = {"hospital":10,"power_substation":9,"stormwater_pump":8,"transport_stop":7,"bridge":6,"school":5,"water_asset":5,"heritage_site":4,"museum":4,"place":3}
for r in at_risk:
    w = type_weight.get(r["type"],2)
    d = haversine(r["lat"], r["lon"], san_marco[0], san_marco[1])
    prox = max(0.0, (3000.0 - min(d,3000.0)))/3000.0*3.0
    r["_score"] = w + prox

top5 = sorted(at_risk, key=lambda x: x["_score"], reverse=True)[:5]

def frag_by_type(t):
    if t in ["power_substation","stormwater_pump"]:
        return {"flood_depth_m_to_failure_prob":[[0.0,0.0],[0.3,0.15],[0.6,0.5],[1.0,0.9]]}
    elif t in ["hospital","school","museum","heritage_site"]:
        return {"flood_depth_m_to_damage":[[0.0,0.0],[0.3,0.2],[0.7,0.5],[1.0,0.8]]}
    else:
        return {"flood_depth_m_to_damage":[[0.0,0.0],[0.4,0.2],[0.8,0.6]]}

assets = []
haz_depth = {}
for r in top5:
    assets.append({"id":r["id"],"label":r["name"],"type":r["type"],"loc":{"lat":r["lat"],"lon":r["lon"],"elev_m":1.2},
                   "fragility":frag_by_type(r["type"]),"state":{"status":"up"}})
    haz_depth[r["id"]] = 0.3 + 0.1*(len(haz_depth)%4)

ids_by_type = {}
for r in top5:
    ids_by_type.setdefault(r["type"],[]).append(r["id"])

deps = []
power_ids = ids_by_type.get("power_substation",[])
pump_ids  = ids_by_type.get("stormwater_pump",[])
for a in assets:
    if a["id"] not in power_ids:
        for p in power_ids:
            deps.append({"from":p,"to":a["id"],"type":"power","critical":True})
    if a["type"] in ["hospital","school","museum","heritage_site"]:
        for p in pump_ids:
            deps.append({"from":p,"to":a["id"],"type":"flood_mitigation","critical":True})

tailored = {
  "meta":{"schema":"CascadingResilienceSim.v0.1","region":"Venice (top5 from data)","crs":"EPSG:4326",
          "created_utc":datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
          "notes":"Priority = type weight + proximity to Piazza San Marco (heuristic)"},
  "actors":[
    {"id":"eoc","label":"Municipal EOC","type":"coordination_center","capacity":{"boats":4,"ambulances":3,"pumps":2}},
    {"id":"utilities","label":"Utilities Ops","type":"infra_operator","capacity":{"portable_generators":2,"mobile_pumps":2}}
  ],
  "assets": assets,
  "hazards":[{"id":"event_flood_realistic_001","type":"coastal_flood","description":"Acqua alta high-risk zone depth assignment (synthetic)",
              "start_utc":"2025-11-05T06:00:00Z","peak_utc":"2025-11-05T08:00:00Z","duration_h":8,
              "depth_by_asset_m": haz_depth}],
  "dependencies": deps,
  "policies":[
    {"id":"rule_start_pumps","when":"exists(type=='stormwater_pump') && event=='flood_onset'",
     "then":[{"action":"dispatch","actor":"utilities","resource":"mobile_pumps","qty":1,"to":"*"}]},
    {"id":"rule_power_backup","when":"any(asset.type in ['hospital','school'] && asset.power=='down')",
     "then":[{"action":"dispatch","actor":"utilities","resource":"portable_generators","qty":1,"to":"asset"}]},
    {"id":"rule_evacuate_high_risk","when":"asset.damage>=0.35 || asset.flood_depth>=0.6",
     "then":[{"action":"dispatch","actor":"eoc","resource":"boats","qty":2,"to":"asset"},
             {"action":"evacuate","target":"asset","count":25}]}
  ],
  "sim_settings":{"time_step_min":10,"stochastic":True,"random_seed":7}
}
with open("venice_top5_tailored_scenario.json","w",encoding="utf-8") as f: json.dump(tailored,f,ensure_ascii=False,indent=2)

# --- NDJSON alerts for ALL at-risk ------------------------------
rows = []
now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
for i, r in enumerate(at_risk, start=1):
    # routing
    targets = []
    for k, v in routes["stakeholders"].items():
        if r["type"] in v:
            targets.append(k)
    if not targets:
        targets = ["municipality_comms"]
    rows.append({
        "msg_id": f"alert_{i:04d}",
        "t": now,
        "from": f"place_agent_{r['id']}",
        "to": targets + routes["default_broadcast"],
        "asset_id": r["id"],
        "asset_name": r["name"],
        "asset_type": r["type"],
        "severity": "high",
        "risk": r["risk"],
        "content": f"'{r['name']}' intersects HIGH flood-risk polygon; prep mitigation and continuity actions.",
        "lat": r["lat"],
        "lon": r["lon"],
        "confidence": 0.9
    })

with open("venice_all_alerts.ndjson","w",encoding="utf-8") as f:
    for row in rows:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

# --- README ------------------------------------------------------
readme = f"""Venice Cascading Flood Mini-Pack
=================================

Generated: {datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")} UTC

Files:
- venice_assets_at_risk.csv
- venice_assets_at_risk.geojson
- venice_tiny_sim_scenario.json
- venice_tiny_sim_schema.json
- stakeholder_routes.json
- venice_top5_tailored_scenario.json
- venice_all_alerts.ndjson

Notes:
- 'assets_at_risk' computed via point-in-polygon (polygon centroid for non-point assets).
- Tailored scenario: picks top-5 by (critical type weight + proximity to Piazza San Marco).
- Alerts NDJSON: one alert per at-risk asset routed to stakeholders from stakeholder_routes.json.
"""
with open("README_venice_sim_pack.txt","w",encoding="utf-8") as f:
    f.write(readme)

print(f"Done. At-risk assets: {len(at_risk)}. Wrote pack files to: {os.getcwd()}")
