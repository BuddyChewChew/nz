import requests
import json
import gzip
from io import BytesIO

# Configuration: Integrated settings for separate headers
SERVICES = [
    {
        "name": "NZ",
        "json_url": "https://github.com/matthuisman/i.mjh.nz/raw/refs/heads/master/nz/tv.json.gz",
        "epg_url": "https://github.com/matthuisman/i.mjh.nz/raw/refs/heads/master/nz/epg.xml.gz",
        "filename": "nz.m3u8"
    },
    {
        "name": "NZAU",
        "json_url": "https://github.com/matthuisman/i.mjh.nz/raw/refs/heads/master/nzau/tv.json.gz",
        "epg_url": "https://github.com/matthuisman/i.mjh.nz/raw/refs/heads/master/nzau/epg.xml.gz",
        "filename": "nzau.m3u8"
    },
    {
        "name": "World",
        "json_url": "https://github.com/matthuisman/i.mjh.nz/raw/refs/heads/master/world/tv.json.gz",
        "epg_url": "https://github.com/matthuisman/i.mjh.nz/raw/refs/heads/master/world/epg.xml.gz",
        "filename": "world.m3u8"
    }
]

def fetch_json(url):
    """Fetches and decompresses .json.gz files from the source."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with gzip.GzipFile(fileobj=BytesIO(response.content)) as f:
            return json.load(f)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def generate_playlists():
    for service in SERVICES:
        print(f"Generating {service['filename']}...")
        data = fetch_json(service["json_url"])
        if not data:
            continue

        # Header contains ONLY the EPG URL specific to this service
        m3u_content = f'#EXTM3U x-tvg-url="{service["epg_url"]}"\n'
        
        for channel_id, info in data.items():
            name = info.get("name", "Unknown")
            logo = info.get("logo", "")
            url = info.get("mjh_master", "")
            chno = info.get("chno", "")
            group = service["name"]
            epg_id = info.get("epg_id", channel_id)
            
            if not url:
                continue

            # Build the #EXTINF line
            extinf = f'#EXTINF:-1 tvg-id="{epg_id}" tvg-name="{name}" tvg-logo="{logo}"'
            if chno:
                extinf += f' tvg-chno="{chno}"'
            extinf += f' group-title="{group}",{name}\n'
            
            m3u_content += extinf
            m3u_content += f'{url}\n'

        # Write the file
        with open(service["filename"], "w", encoding="utf-8") as f:
            f.write(m3u_content)
        
        print(f"Successfully saved {service['filename']}")

if __name__ == "__main__":
    generate_playlists()
