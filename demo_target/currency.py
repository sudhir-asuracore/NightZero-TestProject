def convert_currency(cents: int, fx_rate: float) -> int:
    """Converts currency amount in cents using given foreign exchange rate."""
    if fx_rate <= 0:
        raise ValueError("FX rate must be positive")
    return int(cents * int(fx_rate))
