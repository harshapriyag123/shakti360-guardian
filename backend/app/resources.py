from math import radians, cos, sin, asin, sqrt

# Demo dataset. Replace with verified provider/API before real launch.
DEMO_RESOURCES = [
    {"id":"h1","name":"City General Hospital","type":"hospital","lat":32.9501,"lon":-97.2256,"phone":"demo"},
    {"id":"p1","name":"Central Police Station","type":"police","lat":32.9550,"lon":-97.2302,"phone":"demo"},
    {"id":"ph1","name":"24 Hour Pharmacy","type":"pharmacy","lat":32.9485,"lon":-97.2190,"phone":"demo"},
]

def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    dlat = radians(lat2-lat1)
    dlon = radians(lon2-lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return 2*r*asin(sqrt(a))

def nearby(lat, lon, radius_km=5.0):
    results = []
    for item in DEMO_RESOURCES:
        d = haversine_km(lat, lon, item["lat"], item["lon"])
        if d <= radius_km:
            results.append({**item, "distance_km": round(d, 2)})
    return sorted(results, key=lambda x: x["distance_km"])
