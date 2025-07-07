# data/fetch_news_utils.py

import feedparser
import re

def clean_text(text):
    """
    Cleans up text: removes HTML tags, extra whitespace, and special chars.
    """
    text = re.sub(r"<[^>]+>", "", text)  # remove HTML tags
    text = re.sub(r"http\S+", "", text)  # remove URLs
    text = re.sub(r"[^A-Za-z0-9\s.,!?']", "", text)  # keep basic punctuation
    text = re.sub(r"\s+", " ", text)  # normalize whitespace
    return text.strip()

def fetch_rss_headlines(rss_feeds, coin_name=None, coin_symbol=None):
    """
    Parses RSS feeds and filters news related to the given coin.
    """
    all_news = []

    for feed_url in rss_feeds:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                title = clean_text(entry.get("title", ""))
                summary = clean_text(entry.get("summary", ""))
                combined = f"{title}. {summary}"

                # Filter based on coin name or symbol
                if coin_name and coin_symbol:
                    if (coin_name.lower() in combined.lower()) or (coin_symbol.lower() in combined.lower()):
                        all_news.append(combined)
                else:
                    all_news.append(combined)
        except Exception as e:
            print(f"❌ Error parsing feed: {feed_url} - {e}")

    return all_news
