import json
import requests
import folium
from folium.plugins import MarkerCluster
from pathlib import Path
from typing import List, Tuple

# === CONFIGURATION ===
HAR_FILE = "inputs/columbia.har"
PLATFORM = HAR_FILE.split("/")[-1].replace(".har", "")
OUTPUT_MAP = f"outputs/{PLATFORM}_ip_map.html"
MAX_IPS = 50  # Limit to avoid API rate limiting

# === FUNCTIONS ===


def load_ips_from_har(path: str) -> List[str]:
    """Extract unique IP addresses from a HAR file."""
    with open(path, "r", encoding="utf-8") as f:
        har = json.load(f)

    entries = har.get("log", {}).get("entries", [])
    ips = set()
    for entry in entries:
        ip = entry.get("serverIPAddress")
        url = entry.get("request", {}).get("url", "")
        print(f"Processing entry: {url} with IP: {ip}")
        if ip:
            ip = ip.strip("[]")
            ips.add((ip, url))
    return list(ips)


def geolocate_ip(ip_item: Tuple[str, str]):
    """Geolocate IP using ip-api.com API. Returns (ip, lat, lon, url, isp, org)."""
    ip, url = ip_item

    try:
        resp = requests.get(
            f"http://ip-api.com/json/{ip}?fields=status,lat,lon,isp,org",
            timeout=10,
        )
        data = resp.json()
        if data.get("status") == "success":
            lat = data.get("lat")
            lon = data.get("lon")
            isp = data.get("isp", "Unknown")
            org = data.get("org", "Unknown")
            if lat is not None and lon is not None:
                return ip, lat, lon, url, isp, org
    except Exception as e:
        print(f"Error locating {ip}: {e}")
    return ip, 0, 0, url, "Unknown", "Unknown"


def build_map(
    ip_locations: List[Tuple[str, float, float, str, str, str]], output_path: str
) -> None:
    """Generate Folium map from list of IP + lat/lon + isp/org tuples."""
    m = folium.Map(location=[20, 0], zoom_start=2)
    cluster = MarkerCluster().add_to(m)
    for ip, lat, lon, url, isp, org in ip_locations:
        if lat and lon:
            folium.Marker(
                location=[lat, lon],
                popup=f"IP: {ip}<br>ISP: {isp}<br>Org: {org}<br>URL: {url}",
                icon=folium.Icon(color="blue", icon="info-sign"),
            ).add_to(cluster)

    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"ip": ip, "url": url, "isp": isp, "org": org},
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat],
                },
            }
            for ip, lat, lon, url, isp, org in ip_locations
            if lat and lon
        ],
    }

    m.save(output_path)
    print(f"Map saved to: {output_path}")

    geojson_path = f"outputs/{PLATFORM}_ip_locations.geojson"
    with open(geojson_path, "w", encoding="utf-8") as f:
        json.dump(geojson_data, f)
    print(f"GeoJSON saved to: {geojson_path}")


# === RUN ===

if __name__ == "__main__":
    ip_list = load_ips_from_har(HAR_FILE)
    print(f"Found {len(ip_list)} IPs")

    ips_dict = {}
    for ip, url in ip_list:
        if ip not in ips_dict:
            ips_dict[ip] = url
    ips = list(ips_dict.items())
    print(f"Unique IPs: {len(ips)}")
    ip_locations = [geolocate_ip(ip) for ip in ips[:MAX_IPS]]
    build_map(ip_locations, OUTPUT_MAP)
