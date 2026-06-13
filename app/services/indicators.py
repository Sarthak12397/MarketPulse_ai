import pandas as pd
import pandas_ta as ta


def compute_indicators(candles: list[dict]) -> dict:
    df = pd.DataFrame(candles)

    # Use open_time_utc as index — matches .NET field name
    df["open_time_utc"] = pd.to_datetime(df["open_time_utc"])
    df.set_index("open_time_utc", inplace=True)
    df.sort_index(inplace=True)

    # Ensure numeric columns
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col])

    # ── RSI ───────────────────────────────────────────────
    df["rsi"] = ta.rsi(df["close"], length=14)

    # ── MACD ──────────────────────────────────────────────
    macd = ta.macd(df["close"])
    if macd is not None:
        df["macd"]        = macd["MACD_12_26_9"]
        df["macd_signal"] = macd["MACDs_12_26_9"]
    else:
        df["macd"]        = None
        df["macd_signal"] = None

    # ── EMA Crossover ─────────────────────────────────────
    df["ema20"] = ta.ema(df["close"], length=20)
    df["ema50"] = ta.ema(df["close"], length=50)

    # ── ATR (for entry zones / stop loss / take profit) ───
    df["atr"] = ta.atr(df["high"], df["low"], df["close"], length=14)

    # Return latest bar only as dict
    latest = df.iloc[-1].to_dict()
    return latest