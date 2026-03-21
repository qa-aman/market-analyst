import pandas as pd


def calc_sma(prices: pd.Series, window: int) -> pd.Series:
    """Simple Moving Average."""
    return prices.rolling(window=window).mean()


def calc_ema(prices: pd.Series, window: int) -> pd.Series:
    """Exponential Moving Average."""
    return prices.ewm(span=window, adjust=False).mean()


def calc_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """Relative Strength Index."""
    delta = prices.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calc_macd(
    prices: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> dict:
    """MACD (Moving Average Convergence Divergence).

    Returns dict with macd_line, signal_line, and histogram series.
    """
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line

    return {
        "macd_line": macd_line,
        "signal_line": signal_line,
        "histogram": histogram,
    }


def calc_volume_trend(volume: pd.Series, window: int = 20) -> str:
    """Compare recent average volume to longer-term average."""
    if len(volume) < window:
        return "insufficient_data"

    recent_avg = volume.tail(5).mean()
    longer_avg = volume.tail(window).mean()

    ratio = recent_avg / longer_avg if longer_avg > 0 else 1.0

    if ratio > 1.3:
        return "increasing"
    elif ratio < 0.7:
        return "decreasing"
    return "stable"
