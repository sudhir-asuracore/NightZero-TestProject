def calculate_proration(monthly_cents: int, days_used: int, total_days: int = 30) -> int:
    """Calculates prorated billing charge for partial cycle usage in cents."""
    if total_days <= 0 or days_used < 0:
        raise ValueError("Invalid days parameter for proration")
    return int(round((monthly_cents * days_used) / total_days))
