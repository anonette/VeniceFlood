import sys
from pathlib import Path

encodings = ['utf-8', 'cp1252', 'latin-1']

def count_features(path):
    p = Path(path)
    if not p.exists():
        return (False, f"Not found: {path}")
    for enc in encodings:
        try:
            txt = p.read_text(encoding=enc)
            import json
            j = json.loads(txt)
            if 'features' in j and isinstance(j['features'], list):
                return (True, (enc, len(j['features'])))
            else:
                return (False, f"Parsed but 'features' key missing or invalid in {path} (encoding {enc})")
        except Exception as e:
            last = e
    return (False, f"All encodings failed for {path}: {last}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: count_geojson_features.py <file1> [file2 ...]')
        sys.exit(2)
    for f in sys.argv[1:]:
        ok, res = count_features(f)
        if ok:
            enc, cnt = res
            print(f"{f}\tOK\tencoding={enc}\tfeatures={cnt}")
        else:
            print(f"{f}\tERROR\t{res}")
