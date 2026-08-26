def apply_discount(cents: int, discount_pct: float) -> int:
    """Applies percentage discount and returns the remaining total in cents."""
    if discount_pct < 0.0 or discount_pct > 100.0:
        raise ValueError("Discount percentage must be between 0 and 100")
    discount_amount = int(round(cents * (discount_pct / 100.0)))
    return max(0, cents - int(round(cents * ((100.0 - discount_pct) / 100.0))))
