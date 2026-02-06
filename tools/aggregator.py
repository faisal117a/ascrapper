import json
import os
import datetime
from scrape_bensbytes import scrape_bensbytes
from scrape_rundown import scrape_rundown
from scrape_reddit import scrape_reddit

# Path configuration
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
OUTPUT_FILE = os.path.join(DATA_DIR, 'articles.json')

def load_existing():
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_articles(articles):
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(articles, f, indent=2)

def aggregate():
    print("Starting aggregation...")
    
    # 1. Load existing (optional, if we want to merge. For now, let's refresh list but keep architecture ready)
    existing = load_existing()
    
    # 2. Run Scrapers
    bens = scrape_bensbytes()
    rundown = scrape_rundown()
    reddit = scrape_reddit()
    
    all_new = bens + rundown + reddit
    
    # 3. Filter 24h (Simple check)
    # TODO: rigorous date parsing. For now, rely on scraper's "recent" logic or just saving all for MVP UI.
    
    # 4. Save
    # We overwrite with fresh data for the "Daily Dashboard" concept, 
    # but in a real app we'd merge and dedupe IDs.
    # The requirement: "If there's new data, show them. If not, forget about it."
    # AND "I'd like the ability to save those articles." (Saved state is client-side for now, or separate file)
    
    print(f"Collected {len(all_new)} articles.")
    save_articles(all_new)
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    aggregate()
