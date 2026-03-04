import json
import requests

# Configuration
JSON_URL = "https://i.mjh.nz/nz/tv.json"
EPG_URL = "https://github.com/matthuisman/i.mjh.nz/raw/refs/heads/master/nz/epg.xml.gz"
OUTPUT_FILE = "playlist.m3u"

def generate_m3u():
    try:
        # Fetch the JSON data from the live link
        response = requests.get(JSON_URL)
        response.raise_for_status()
        data = response.json()

        # Build M3U header with the provided EPG link
        m3u_content = f'#EXTM3U x-tvg-url="{EPG_URL}"\n'

        for channel_id, info in data.items():
            name = info.get("name", "Unknown")
            logo = info.get("logo", "")
            url = info.get("mjh_master", "")
            chno = info.get("chno", "")
            group = info.get("network", "Other")
            epg_id = info.get("epg_id", channel_id)
            
            # Skip if there is no stream URL available
            if not url:
                continue

            # Build the #EXTINF line
            extinf = f'#EXTINF:-1 tvg-id="{epg_id}" tvg-name="{name}" tvg-logo="{logo}"'
            if chno:
                extinf += f' tvg-chno="{chno}"'
            extinf += f' group-title="{group}",{name}\n'
            
            m3u_content += extinf
            m3u_content += f'{url}\n'

        # Write the final file
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(m3u_content)
        
        print(f"Successfully generated {OUTPUT_FILE}")

    except Exception as e:
        print(f"Error during scraping: {e}")

if __name__ == "__main__":
    generate_m3u()
