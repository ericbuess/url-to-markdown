import json
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin


def process_sitemaps(sitemaps_file):
    # Read the sitemaps.json file
    with open(sitemaps_file, 'r') as f:
        sitemap_urls = json.load(f)

    all_urls = []

    # Process each sitemap URL
    for sitemap_url in sitemap_urls:
        print(f"Processing sitemap: {sitemap_url}")
        response = requests.get(sitemap_url)

        if response.status_code == 200:
            # Parse the XML content
            root = ET.fromstring(response.content)

            # Extract URLs from the sitemap
            # Note: We're using the namespace prefix 'sm' here, as it's commonly used in sitemaps
            for url in root.findall('.//sm:url', namespaces={'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}):
                loc = url.find('sm:loc', namespaces={
                               'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'})
                if loc is not None:
                    all_urls.append(loc.text)
        else:
            print(f"Failed to fetch sitemap: {sitemap_url}")

    # Save all URLs to sitemap_queue.json
    with open('sitemap_queue.json', 'w') as f:
        json.dump(all_urls, f, indent=2)

    print(f"Processed {len(sitemap_urls)} sitemaps and saved {
          len(all_urls)} URLs to sitemap_queue.json")


if __name__ == "__main__":
    process_sitemaps('sitemaps.json')
