import requests
import datetime
import uuid
import json
import os
import xml.etree.ElementTree as ET

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def scrape_reddit():
    url = "https://www.reddit.com/r/ArtificialInteligence/top.rss?t=day"
    print(f"Scraping {url}...")
    try:
        response = requests.get(url, headers=HEADERS)
        # Reddit returns 429 often. If it fails, we might return empty list.
        if response.status_code == 429:
            print("Reddit Rate Limit (429). Skipping.")
            return []
            
        response.raise_for_status()
        
        # Parse XML
        root = ET.fromstring(response.content)
        
        articles = []
        # Atom feed standard
        # Namespace map might be needed
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        # Depending on feed, it might be <entry> or <item> (RSS vs Atom). Reddit usually returns Atom.
        entries = root.findall('{http://www.w3.org/2005/Atom}entry')
        
        for entry in entries:
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            link = entry.find('{http://www.w3.org/2005/Atom}link').attrib['href']
            updated = entry.find('{http://www.w3.org/2005/Atom}updated').text
            
            # Summary often contains HTML in Reddit feeds
            summary = ""
            content = entry.find('{http://www.w3.org/2005/Atom}content')
            if content is not None:
                content_html = content.text
                summary = content.text[:200] + "..." # Truncate but keep clean if possible
                image_url = extract_image(content_html)
            else:
                content_html = ""
                image_url = ""

            article = {
                "id": str(uuid.uuid4()),
                "title": title,
                "url": link,
                "source": "Reddit",
                "published_at": updated,
                "scraped_at": datetime.datetime.now().isoformat(),
                "summary": summary,
                "image_url": image_url,
                "tags": ["Reddit", "AI"]
            }
            articles.append(article)

        return articles

    except Exception as e:
        print(f"Failed to scrape Reddit: {e}")
        return []

def extract_image(content_html):
    if not content_html:
        return ""
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content_html, 'lxml')
        img = soup.find('img')
        if img and 'src' in img.attrs:
             # Often reddit puts preview images in content
             return img['src']
        return ""
    except:
        return ""

if __name__ == "__main__":
    data = scrape_reddit()
    print(json.dumps(data, indent=2))
