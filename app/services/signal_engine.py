from app.models.request import SignalRequest
from app.models.response import SignalResponse
from app.services.indicators import compute_indicators
from app.services.news_sentiment import get_news_sentiment


def generate_signal(request: SignalRequest) -> SignalResponse:
    candles = [c.model_dump() for c in request.candles]

    if len(candles) < 50:
        return SignalResponse(
            direction        = "Neutral",
            confidence_score = 0.10,
            reasoning        = "Insufficient candle data for reliable analysis."
        )

    ind = compute_indicators(candles)

    votes     = []
    reasoning = []

    # ── RSI Vote ──────────────────────────────────────────
    rsi = ind.get("rsi")
    if rsi is not None and not _is_nan(rsi):
        if rsi < 40:
            votes.append("Long")
            reasoning.append(f"RSI at {rsi:.1f} indicates oversold conditions.")
        elif rsi > 60:
            votes.append("Short")
            reasoning.append(f"RSI at {rsi:.1f} indicates overbought conditions.")
        else:
            votes.append("Neutral")
            reasoning.append(f"RSI at {rsi:.1f} shows no clear momentum bias.")

    # ── MACD Vote ─────────────────────────────────────────
    macd_v = ind.get("macd")
    macd_s = ind.get("macd_signal")
    if (macd_v is not None and macd_s is not None and
            not _is_nan(macd_v) and not _is_nan(macd_s)):
        if macd_v > macd_s:
            votes.append("Long")
            reasoning.append("MACD line crossed above signal line, bullish momentum.")
        else:
            votes.append("Short")
            reasoning.append("MACD line crossed below signal line, bearish momentum.")

    # ── EMA Vote ──────────────────────────────────────────
    ema20 = ind.get("ema20")
    ema50 = ind.get("ema50")
    if (ema20 is not None and ema50 is not None and
            not _is_nan(ema20) and not _is_nan(ema50)):
        if ema20 > ema50:
            votes.append("Long")
            reasoning.append("EMA20 above EMA50 supports upward trend bias.")
        else:
            votes.append("Short")
            reasoning.append("EMA20 below EMA50 supports downward trend bias.")

    # ── NEWS Vote (4th signal) ────────────────────────────
    news = get_news_sentiment(request.symbol)
    if news["vote"] != "Neutral":
        votes.append(news["vote"])
    reasoning.append(news["reasoning"])

    # ── Derive Direction + Confidence ─────────────────────
    if not votes:
        return SignalResponse(
            direction        = "Neutral",
            confidence_score = 0.20,
            reasoning        = " ".join(reasoning)
        )

    long_v  = votes.count("Long")
    short_v = votes.count("Short")
    total   = len(votes)

    if long_v == total:
        direction, confidence = "Long",    0.85  # all 4 agree
    elif short_v == total:
        direction, confidence = "Short",   0.85  # all 4 agree
    elif long_v > short_v:
        direction, confidence = "Long",    0.60
    elif short_v > long_v:
        direction, confidence = "Short",   0.60
    else:
        direction, confidence = "Neutral", 0.30

    # ── ATR Price Levels ──────────────────────────────────
    atr   = ind.get("atr")
    close = candles[-1]["close"]
    ezl = ezh = sl = tp1 = tp2 = None

    if atr and not _is_nan(atr) and direction != "Neutral":
        if direction == "Long":
            ezl = round(close - (atr * 0.3), 8)
            ezh = round(close + (atr * 0.3), 8)
            sl  = round(close - (atr * 1.5), 8)
            tp1 = round(close + (atr * 2.0), 8)
            tp2 = round(close + (atr * 3.5), 8)
        else:
            ezl = round(close - (atr * 0.3), 8)
            ezh = round(close + (atr * 0.3), 8)
            sl  = round(close + (atr * 1.5), 8)
            tp1 = round(close - (atr * 2.0), 8)
            tp2 = round(close - (atr * 3.5), 8)

    return SignalResponse(
        direction        = direction,
        confidence_score = round(confidence, 4),
        reasoning        = " ".join(reasoning),
        entry_zone_low   = ezl,
        entry_zone_high  = ezh,
        stop_loss        = sl,
        take_profit_one  = tp1,
        take_profit_two  = tp2,
    )


def _is_nan(value) -> bool:
    try:
        import math
        return math.isnan(float(value))
    except (TypeError, ValueError):
        return True