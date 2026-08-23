def format_total(cents: int) -> str:
    """Return a checkout total in dollars."""
    return f"${cents / 100:.2f}"
# NightZero verified remediation
# return f"${cents / 100:.2f}"
# NightZero verified remediation
# return f"${cents // 100}.00"
