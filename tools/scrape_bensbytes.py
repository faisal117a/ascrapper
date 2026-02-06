import feedparser
import datetime
import uuid
import json
import os

def scrape_bensbytes():
    url = "https://bensbites.substack.com/feed"
    print(f"Scraping RSS {url}...")
    try:
        feed = feedparser.parse(url)
        
        if hasattr(feed, 'status') and feed.status != 200:
             print(f"Error fetching feed: Status {feed.status}")
             if feed.status == 301 or feed.status == 302:
                 print(f"Redirected to: {feed.href}")
        
        articles = []
        print(f"Found {len(feed.entries)} entries in feed.")

        for entry in feed.entries:
            try:
                title = entry.title
                link = entry.link
                
                # Published date handling
                if hasattr(entry, 'published'):
                    published_at = entry.published
                elif hasattr(entry, 'updated'):
                    published_at = entry.updated
                else:
                     published_at = datetime.datetime.now().isoformat()

                summary = ""
                if hasattr(entry, 'summary'):
                    summary = entry.summary
                elif hasattr(entry, 'description'):
                     summary = entry.description

                # Try to find image in summary
                image_url = ""
                if summary:
                    try:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(summary, 'lxml')
                        img = soup.find('img')
                        if img and 'src' in img['src']:
                            image_url = img['src']
                    except:
                        pass

                article = {
                    "id": str(uuid.uuid4()),
                    "title": title,
                    "url": link,
                    "source": "BensBytes",
                    "published_at": published_at,
                    "scraped_at": datetime.datetime.now().isoformat(),
                    "summary": summary[:200] + "...",
                    "image_url": image_url, 
                    "tags": ["AI", "Newsletter"]
                }
                
                articles.append(article)
                
            except Exception as e:
                print(f"Error parsing entry: {e}")
                continue
                
        return articles

    except Exception as e:
        print(f"Failed to scrape Ben's Bytes RSS: {e}")
        return []

if __name__ == "__main__":
    data = scrape_bensbytes()
    print(json.dumps(data, indent=2))
