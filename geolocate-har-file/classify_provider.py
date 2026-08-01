"""
classify_provider.py

Takes a GeoJSON file of IP locations (the kind produced by scrape_har_locations.py)
and labels each point with its likely infrastructure provider (AWS, Cloudflare,
Google Cloud, or "Other/Unclassified") by checking the IP against each provider's
published public IP ranges.

Usage:
    python classify_provider.py ip_locations.geojson
"""

import ipaddress
import json
import sys
import requests

AWS_RANGES_URL = "https://ip-ranges.amazonaws.com/ip-ranges.json"
CLOUDFLARE_V4_URL = "https://www.cloudflare.com/ips-v4"
CLOUDFLARE_V6_URL = "https://www.cloudflare.com/ips-v6"
GOOGLE_CLOUD_RANGES_URL = "https://www.gstatic.com/ipranges/cloud.json"
AZURE_RANGES_URL = "https://download.microsoft.com/download/7/1/D/71D86715-5596-4529-9B13-DA13A5DE5B63/ServiceTags_Public_20240101.json"


def fetch_aws_ranges():
    resp = requests.get(AWS_RANGES_URL, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    networks = []
    for prefix in data.get("prefixes", []):
        networks.append(ipaddress.ip_network(prefix["ip_prefix"]))
    for prefix in data.get("ipv6_prefixes", []):
        networks.append(ipaddress.ip_network(prefix["ipv6_prefix"]))
    return networks


def fetch_cloudflare_ranges():
    networks = []
    for url in (CLOUDFLARE_V4_URL, CLOUDFLARE_V6_URL):
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        for line in resp.text.strip().splitlines():
            line = line.strip()
            if line:
                networks.append(ipaddress.ip_network(line))
    return networks


def fetch_google_cloud_ranges():
    resp = requests.get(GOOGLE_CLOUD_RANGES_URL, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    networks = []
    for entry in data.get("prefixes", []):
        prefix = entry.get("ipv4Prefix") or entry.get("ipv6Prefix")
        if prefix:
            networks.append(ipaddress.ip_network(prefix))
    return networks


def fetch_azure_ranges(local_path=None):
    if local_path:
        with open(local_path, "r") as f:
            data = json.load(f)
    else:
        resp = requests.get(AZURE_RANGES_URL, timeout=15)
        resp.raise_for_status()
        data = resp.json()

    networks = []
    for value in data.get("values", []):
        for prefix in value.get("properties", {}).get("addressPrefixes", []):
            try:
                networks.append(ipaddress.ip_network(prefix))
            except ValueError:
                continue
    return networks


def classify_ip(ip_str, provider_ranges):
    try:
        ip_obj = ipaddress.ip_address(ip_str)
    except ValueError:
        return "Invalid IP"

    for provider_name, networks in provider_ranges.items():
        for net in networks:
            if ip_obj in net:
                return provider_name
    return "Other/Unclassified"


def main():
    if len(sys.argv) not in (2, 3):
        print(
            "Usage: python classify_provider.py <path_to_geojson> [azure_ranges_file.json]"
        )
        sys.exit(1)

    input_path = sys.argv[1]

    print("Fetching provider IP ranges (this takes a few seconds)...")
    provider_ranges = {}
    try:
        provider_ranges["AWS"] = fetch_aws_ranges()
        print(f"  AWS: {len(provider_ranges['AWS'])} ranges loaded")
    except Exception as e:
        print(f"  Warning: could not fetch AWS ranges ({e})")
        provider_ranges["AWS"] = []

    try:
        provider_ranges["Cloudflare"] = fetch_cloudflare_ranges()
        print(f"  Cloudflare: {len(provider_ranges['Cloudflare'])} ranges loaded")
    except Exception as e:
        print(f"  Warning: could not fetch Cloudflare ranges ({e})")
        provider_ranges["Cloudflare"] = []

    try:
        provider_ranges["Google Cloud"] = fetch_google_cloud_ranges()
        print(f"  Google Cloud: {len(provider_ranges['Google Cloud'])} ranges loaded")
    except Exception as e:
        print(f"  Warning: could not fetch Google Cloud ranges ({e})")
        provider_ranges["Google Cloud"] = []

    azure_local_path = sys.argv[2] if len(sys.argv) > 2 else None
    try:
        provider_ranges["Azure"] = fetch_azure_ranges(local_path=azure_local_path)
        print(f"  Azure: {len(provider_ranges['Azure'])} ranges loaded")
    except Exception as e:
        print(f"  Warning: could not fetch Azure ranges ({e})")
        provider_ranges["Azure"] = []

    with open(input_path, "r") as f:
        geojson = json.load(f)

    counts = {}
    for feature in geojson.get("features", []):
        props = feature.get("properties", {})
        ip_str = props.get("ip") or props.get("IP") or props.get("ip_address")
        if not ip_str:
            provider = "No IP field found"
        else:
            provider = classify_ip(ip_str, provider_ranges)

        props["provider"] = provider
        feature["properties"] = props
        counts[provider] = counts.get(provider, 0) + 1

    output_path = input_path.replace(".geojson", "_classified.geojson")
    with open(output_path, "w") as f:
        json.dump(geojson, f, indent=2)

    print(f"\nWrote classified output to: {output_path}")
    print("\nProvider breakdown:")
    for provider, count in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {provider}: {count}")


if __name__ == "__main__":
    main()
