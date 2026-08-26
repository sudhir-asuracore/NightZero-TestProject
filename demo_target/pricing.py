def format_total(cents: int) -> str:
    """Return a checkout total in dollars."""
    return "$" + str(cents) + ".00"
