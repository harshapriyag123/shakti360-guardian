from math import radians, cos, sin, asin, sqrt
import httpx

DEMO_RESOURCES = [
    {"id":"h1","name":"Demo General Hospital","type":"hospital","lat":32.9501,"lon":-97.2256},
    {"id":"p1","name":"Demo Police Station","type":"police","lat":32.9550,"lon":-97.2302},
    {"id":"ph1","name":"Demo 24-Hour Pharmacy","type":"pharmacy","lat":32.9485,"lon":-97.2190},
    {"id":"h2","name":"Demo Urgent Care","type":"hospital","lat":32.9440,"lon":-97.2350},
]

def _distance(lat1, lon1, lat2, lon2):
    r = 6371.0
    dlat, dlon = radians(lat2-lat1), radians(lon2-lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return 2*r*asin(sqrt(a))

def nearby(lat: float, lon: float, radius_km: float = 8.0, types=None):
    types = set(types or ["hospital", "police", "pharmacy"])
    out = []
    for r in DEMO_RESOURCES:
        if r["type"] not in types:
            continue
        d = _distance(lat, lon, r["lat"], r["lon"])
        if d <= radius_km:
            out.append({**r, "distance_km": round(d, 2)})
    return sorted(out, key=lambda x: x["distance_km"])

async def nearby_live(lat: float, lon: float, radius_km: float = 8.0):
    """Fetch current community-maintained support locations, with a labeled demo fallback."""
    radius_m = min(int(radius_km * 1000), 15000)
    query = f'''[out:json][timeout:3];(
      nwr["amenity"~"hospital|clinic|pharmacy|police"](around:{radius_m},{lat},{lon});
    );out center tags 30;'''
    try:
        # Stay well inside the browser's API timeout. Live community data is
        # optional; the endpoint must still answer when Overpass is busy.
        timeout = httpx.Timeout(4.0, connect=2.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post("https://overpass-api.de/api/interpreter", content=query, headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Shakti360Guardian/0.1"})
            response.raise_for_status()
        results = []
        for item in response.json().get("elements", []):
            tags = item.get("tags", {})
            item_lat = item.get("lat") or item.get("center", {}).get("lat")
            item_lon = item.get("lon") or item.get("center", {}).get("lon")
            if item_lat is None or item_lon is None:
                continue
            results.append({
                "id": f"osm-{item['type']}-{item['id']}", "name": tags.get("name", tags.get("amenity", "Support service").replace("_", " ").title()),
                "type": tags.get("amenity", "support"), "lat": item_lat, "lon": item_lon,
                "phone": tags.get("contact:phone") or tags.get("phone"), "website": tags.get("contact:website") or tags.get("website"),
                "distance_km": round(_distance(lat, lon, item_lat, item_lon), 2),
            })
        if results:
            return {"resources": sorted(results, key=lambda x: x["distance_km"]), "provider": "OpenStreetMap contributors", "is_live": True}
    except (httpx.HTTPError, ValueError, KeyError):
        pass
    return {"resources": nearby(lat, lon, radius_km), "provider": "Shakti360 offline demo data", "is_live": False}
