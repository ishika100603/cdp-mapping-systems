"""
build_combined_map_v2.py - colors points by owning company, clusters overlapping
points, and includes a color legend.
"""

import json
import folium
from folium.plugins import MarkerCluster

PLATFORM_FILES = {
    "Amazon": "outputs/amazon_ip_locations.geojson",
    "Columbia": "outputs/columbia_ip_locations.geojson",
    "Instagram": "outputs/instagram_ip_locations.geojson",
    "Reddit": "outputs/reddit_ip_locations.geojson",
    "YouTube Music": "outputs/youtube_ip_locations.geojson",
}

ISP_COLORS = {
    "Facebook": "purple",
    "Google": "green",
    "Amazon": "orange",
    "Fastly": "red",
    "Cloudflare": "blue",
    "Akamai": "darkred",
    "Other": "gray",
}


def classify_isp(isp: str, org: str) -> str:
    text = f"{isp} {org}".lower()
    if "facebook" in text or "meta" in text:
        return "Facebook"
    if "google" in text:
        return "Google"
    if "amazon" in text or "aws" in text:
        return "Amazon"
    if "fastly" in text:
        return "Fastly"
    if "cloudflare" in text:
        return "Cloudflare"
    if "akamai" in text:
        return "Akamai"
    return "Other"


def load_platform_points(platform, path):
    points = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"  Warning: {path} not found, skipping {platform}")
        return points

    for feature in data.get("features", []):
        coords = feature.get("geometry", {}).get("coordinates")
        props = feature.get("properties", {})
        if coords and len(coords) == 2:
            lon, lat = coords
            ip = props.get("ip", "unknown")
            url = props.get("url", "")
            isp = props.get("isp", "Unknown")
            org = props.get("org", "Unknown")
            owner = classify_isp(isp, org)
            points.append((lat, lon, ip, url, isp, org, owner))
    return points


def main():
    m = folium.Map(location=[20, 0], zoom_start=2)

    legend_html = """
    <div style="position: fixed; bottom: 200px; left: 20px; z-index: 9999;
                background: white; padding: 10px 14px; border: 2px solid #444;
                border-radius: 6px; font-size: 12px; font-family: sans-serif;">
    <b>Owner Legend</b><br>
    <span style="color:purple;">&#9679;</span> Facebook<br>
    <span style="color:green;">&#9679;</span> Google<br>
    <span style="color:orange;">&#9679;</span> Amazon<br>
    <span style="color:red;">&#9679;</span> Fastly<br>
    <span style="color:blue;">&#9679;</span> Cloudflare<br>
    <span style="color:darkred;">&#9679;</span> Akamai<br>
    <span style="color:gray;">&#9679;</span> Other
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    caveat_html = """
    <div style="position: fixed; bottom: 20px; left: 20px; z-index: 9999;
                background: white; padding: 10px 14px; border: 2px solid #444;
                border-radius: 6px; max-width: 340px; font-size: 12px; font-family: sans-serif;">
    <b>Note:</b> Marker colors show the company that owns the IP address
    (via ISP/org lookup), not the platform being visited. Numbered circles
    are clusters of multiple points sharing the same registered location -
    click to expand. For CDN-fronted sites, location reflects the registered
    IP block address, not necessarily the physical server location.
    </div>
    """
    m.get_root().html.add_child(folium.Element(caveat_html))

    owner_counts = {}

    for platform, path in PLATFORM_FILES.items():
        points = load_platform_points(platform, path)
        print(f"{platform}: {len(points)} points loaded")

        fg = folium.FeatureGroup(name=f"{platform} ({len(points)})")
        cluster = MarkerCluster().add_to(fg)

        for lat, lon, ip, url, isp, org, owner in points:
            if lat and lon:
                owner_counts[owner] = owner_counts.get(owner, 0) + 1
                color = ISP_COLORS.get(owner, "gray")
                popup_text = (
                    f"<b>Platform:</b> {platform}<br>"
                    f"<b>Owner:</b> {owner}<br>"
                    f"IP: {ip}<br>"
                    f"ISP: {isp}<br>"
                    f"Org: {org}<br>"
                    f"URL: {url[:80]}{'...' if len(url) > 80 else ''}"
                )
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=6,
                    popup=folium.Popup(popup_text, max_width=320),
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.85,
                ).add_to(cluster)

        fg.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    output_path = "outputs/combined_ip_map.html"
    m.save(output_path)
    print(f"\nCombined map saved to: {output_path}")
    print("\nOwner breakdown (across all platforms):")
    for owner, count in sorted(owner_counts.items(), key=lambda x: -x[1]):
        print(f"  {owner}: {count}")


if __name__ == "__main__":
    main()
