import requests
import os


def get_news_sentiment(symbol: str) -> dict:
    """
    Fetches latest crypto news and returns a sentiment vote.
    Returns: { vote: "Long"|"Short"|"Neutral", reasoning: str }
    """
    api_key = os.getenv("NEWS_API_KEY", "")

    if not api_key:
        return {
            "vote":      "Neutral",
            "reasoning": "News API key not configured."
        }

    # Strip the /USDT part — search for just "BTC" not "BTC/USDT"
    asset = symbol.split("/")[0]

    try:
        response = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q":        f"{asset} crypto",
                "language": "en",
                "sortBy":   "publishedAt",
                "pageSize": 10,
                "apiKey":   api_key
            },
            timeout=5
        )

        if response.status_code != 200:
            return {
                "vote":      "Neutral",
                "reasoning": "News API unavailable."
            }

        articles = response.json().get("articles", [])

        if not articles:
            return {
                "vote":      "Neutral",
                "reasoning": "No recent news found."
            }

        # Simple keyword sentiment scoring
        positive_words = [
            "surge", "rally", "bullish", "breakout", "gain",
            "rise", "pump", "adoption", "record", "high",
            "buy", "growth", "positive", "upward", "boost"
        ]
        negative_words = [
            "crash", "drop", "bearish", "dump", "fall",
            "plunge", "sell", "fear", "ban", "hack",
            "loss", "decline", "negative", "downward", "risk"
        ]

        positive_score = 0
        negative_score = 0

        for article in articles:
            text = (
                (article.get("title")       or "") + " " +
                (article.get("description") or "")
            ).lower()

            for word in positive_words:
                if word in text:
                    positive_score += 1

            for word in negative_words:
                if word in text:
                    negative_score += 1

        total = positive_score + negative_score

        if total == 0:
            return {
                "vote":      "Neutral",
                "reasoning": "News sentiment is neutral with no strong signals."
            }

        ratio = positive_score / total

        if ratio >= 0.65:
            return {
                "vote":      "Long",
                "reasoning": f"News sentiment is bullish ({positive_score} positive vs {negative_score} negative signals)."
            }
        elif ratio <= 0.35:
            return {
                "vote":      "Short",
                "reasoning": f"News sentiment is bearish ({negative_score} negative vs {positive_score} positive signals)."
            }
        else:
            return {
                "vote":      "Neutral",
                "reasoning": f"News sentiment is mixed ({positive_score} positive, {negative_score} negative signals)."
            }

    except Exception as e:
        return {
            "vote":      "Neutral",
            "reasoning": "News fetch failed — defaulting to neutral."
        }