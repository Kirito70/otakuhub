import httpx, json

url = "https://github.com/manami-project/anime-offline-database/releases/latest/download/anime-offline-database-minified.json"
resp = httpx.get(url, follow_redirects=True, timeout=120.0)
raw = resp.json()

print(f"type: {type(raw).__name__}")
if isinstance(raw, dict):
    print(f"keys: {list(raw.keys())}")
    for k, v in raw.items():
        if isinstance(v, list):
            print(f"  {k}: list of {len(v)} items")
            if v:
                item = v[0]
                print(f"  first item type: {type(item).__name__}")
                if isinstance(item, dict):
                    print(f"  first item keys: {list(item.keys())[:10]}")
        elif isinstance(v, dict):
            print(f"  {k}: dict with keys {list(v.keys())[:5]}")
        else:
            print(f"  {k}: {v}")
elif isinstance(raw, list):
    print(f"list of {len(raw)} items")
    if raw:
        item = raw[0]
        print(f"first item type: {type(item).__name__}")
        if isinstance(item, dict):
            print(f"first item keys: {list(item.keys())[:10]}")
