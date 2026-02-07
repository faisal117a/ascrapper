"""
Modal Scheduled Scraper
Runs the article aggregator every 24 hours and pushes to GitHub.
"""
import modal
import subprocess
import os

# Create a Modal app
app = modal.App("tech-updates-scraper")

# Define the image with required dependencies
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "requests",
    "feedparser", 
    "beautifulsoup4",
    "lxml"
)

@app.function(
    image=image,
    schedule=modal.Cron("0 8 * * *"),  # Run daily at 8 AM UTC
)
def scrape_and_update():
    """Scrape all sources and generate articles.json"""
    import json
    import uuid
    import datetime
    import requests
    import feedparser
    from bs4 import BeautifulSoup
    
    articles = []
    
    # === Ben's Bites ===
    print("Scraping Ben's Bites...")
    try:
        feed = feedparser.parse("https://bensbites.substack.com/feed")
        for entry in feed.entries[:20]:
            title = entry.get('title', 'No Title')
            link = entry.get('link', '')
            published = entry.get('published', datetime.datetime.now().isoformat())
            summary = entry.get('summary', '')[:200] + "..."
            
            # Try to extract image from summary
            image_url = ""
            try:
                soup = BeautifulSoup(summary, 'lxml')
                img = soup.find('img')
                if img and img.get('src'):
                    image_url = img['src']
            except:
                pass
            
            articles.append({
                "id": str(uuid.uuid4()),
                "title": title,
                "url": link,
                "source": "BensBytes",
                "published_at": published,
                "scraped_at": datetime.datetime.now().isoformat(),
                "summary": BeautifulSoup(summary, 'lxml').get_text()[:200] + "...",
                "image_url": image_url,
                "tags": ["AI", "Newsletter"]
            })
        print(f"  Got {len([a for a in articles if a['source'] == 'BensBytes'])} from Ben's Bites")
    except Exception as e:
        print(f"  Error: {e}")
    
    # === Reddit r/ArtificialIntelligence ===
    print("Scraping Reddit...")
    try:
        headers = {'User-Agent': 'TechUpdates/1.0'}
        resp = requests.get(
            "https://www.reddit.com/r/ArtificialIntelligence/top.rss?t=day",
            headers=headers,
            timeout=10
        )
        
        import xml.etree.ElementTree as ET
        root = ET.fromstring(resp.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        for entry in root.findall('.//atom:entry', ns)[:25]:
            title = entry.find('atom:title', ns)
            link = entry.find('atom:link', ns)
            updated = entry.find('atom:updated', ns)
            content = entry.find('atom:content', ns)
            
            title_text = title.text if title is not None else "No Title"
            link_href = link.get('href') if link is not None else ""
            updated_text = updated.text if updated is not None else datetime.datetime.now().isoformat()
            
            # Extract image from content
            image_url = ""
            summary = ""
            if content is not None and content.text:
                try:
                    soup = BeautifulSoup(content.text, 'lxml')
                    img = soup.find('img')
                    if img and img.get('src'):
                        image_url = img['src']
                    summary = soup.get_text()[:200] + "..."
                except:
                    summary = content.text[:200] + "..."
            
            articles.append({
                "id": str(uuid.uuid4()),
                "title": title_text,
                "url": link_href,
                "source": "Reddit",
                "published_at": updated_text,
                "scraped_at": datetime.datetime.now().isoformat(),
                "summary": summary,
                "image_url": image_url,
                "tags": ["Reddit", "AI"]
            })
        print(f"  Got {len([a for a in articles if a['source'] == 'Reddit'])} from Reddit")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Sort by date
    articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)
    
    print(f"\nTotal articles: {len(articles)}")
    
    # Return the JSON data
    return json.dumps(articles, indent=2)


@app.local_entrypoint()
def main():
    """Local test entrypoint"""
    result = scrape_and_update.remote()
    
    # Save locally
    with open("data/articles.json", "w", encoding="utf-8") as f:
        f.write(result)
    
    print("Saved to data/articles.json")
    print("To deploy: modal deploy modal_scraper.py")


# To test locally: modal run modal_scraper.py
# To deploy scheduled: modal deploy modal_scraper.py
