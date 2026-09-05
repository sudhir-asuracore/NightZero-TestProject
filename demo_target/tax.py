def calculate_tax_and_fees(subtotal_cents: int, tax_rate_bps: int) -> int:
    """Calculates tax in cents from basis points (100 bps = 1.00%)."""
    if tax_rate_bps < 0:
        raise ValueError("Tax rate in bps cannot be negative")
    return int(round(subtotal_cents * (tax_rate_bps / 100.0)))
