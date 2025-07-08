# data/fetch_sentiment.py

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from config import RSS_FEEDS, USE_FINBERT, SYMBOL_NAME_MAP
from data.fetch_news_utils import fetch_rss_headlines

def get_sentiment_score(symbol, print_news=True):
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    from config import RSS_FEEDS, SYMBOL_NAME_MAP
    from data.fetch_news_utils import fetch_rss_headlines

    coin_symbol = symbol.replace("USDT", "")
    coin_name, coin_code = SYMBOL_NAME_MAP.get(coin_symbol, (None, None))

    headlines = fetch_rss_headlines(RSS_FEEDS, coin_name, coin_code)
    if not headlines:
        print("\nUsing 0 news headlines for sentiment.\n")
        return "neutral", []

    analyzer = SentimentIntensityAnalyzer()
    scored_headlines = []
    total_score = 0

    for item in headlines:
        vs = analyzer.polarity_scores(item['text'])
        compound = vs["compound"]
        item["score"] = compound
        total_score += compound
        scored_headlines.append(item)

    avg_score = total_score / len(scored_headlines)

    if print_news:
        print(f"\nUsing {len(scored_headlines)} headlines:")
        for i, item in enumerate(scored_headlines[:10], 1):
            print(f"\n{i}. {item['title']} ({item['score']:.2f})")
            print(f"   Source: {item['source']} | Published: {item['published']}")
            print(f"   Link: {item['link']}")


    if avg_score >= 0.25:
        sentiment = "bullish"
    elif avg_score <= -0.25:
        sentiment = "bearish"
    else:
        sentiment = "neutral"

    return sentiment, scored_headlines
