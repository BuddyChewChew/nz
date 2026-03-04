import requests
import json
import gzip
from io import BytesIO

# Configuration: Integrated settings for all three services
SERVICES = [
    {
        "name": "NZ",
        "json_url": "https://i.mjh.nz/nz/tv.json",
        "epg_url": "https://github.com/matthuisman/i.mjh.nz/raw/refs/heads/master/nz/epg.xml.gz"
    },
    {
        "name": "NZAU",
        "json_url": "https://github.com/matthuisman/i.mjh.nz/raw/refs/heads/master/nzau/tv.json.gz",
        "epg_url": "https://github.com/matthuisman/i.mjh.nz/raw/refs/heads/master/nzau/epg.xml.gz"
    },
    {
        "name": "World",
        "json_url": "https://github.com/matthuisman/i.mjh.nz/raw/refs/heads/master/world/tv.json.gz",
        "epg_url": "https://github.com/matthuisman/i.mjh.nz/raw/refs/heads/master/world/epg.xml.gz"
    }
]

OUTPUT_FILE = "nz_all.m3u8"

def fetch_json(url):
    """Helper to handle both standard and gzipped JSON files."""
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    
    # If the URL ends in .gz or the response is compressed, decompress it
    if url.endswith('.gz') or response.headers.get('Content-Encoding') == 'gzip':
        with gzip.GzipFile(fileobj=BytesIO(response.content)) as f:
            return json.load(f)
    return response.json()

def generate_consolidated_m3u():
    # Build the M3U header with all EPG URLs separated by commas
    epg_list = ",".join([s["epg_url"] for s in SERVICES])
    m3u_content = f'#EXTM3U x-tvg-url="{epg_list}"\n'
    
    for service in SERVICES:
        try:
            print(f"Processing {service['name']}...")
            data = fetch_json(service["json_url"])

            for channel_id, info in data.items():
                name = info.get("name", "Unknown")
                logo = info.get("logo", "")
                url = info.get("mjh_master", "")
                chno = info.get("chno", "")
                # Set the group-title strictly to the service name for categorization
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

        except Exception as e:
            print(f"Failed to process {service['name']}: {e}")

    # Write the full, final version of the integrated code
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u_content)
    
    print(f"Successfully generated {OUTPUT_FILE} with channels grouped by service.")

if __name__ == "__main__":
    generate_consolidated_m3u()
