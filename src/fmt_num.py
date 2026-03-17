def fmt_num(v: float) -> str:
    """Return a compact, human-readable number string (no currency symbol).
 
    Examples
    --------
    >>> fmt_num(2_500_000)
    '2.5M'
    >>> fmt_num(18_000)
    '18.0K'
    >>> fmt_num(42)
    '42'
    """
    if v >= 1e6:
        return f"{v / 1e6:.1f}M"
    if v >= 1e3:
        return f"{v / 1e3:.1f}K"
    return f"{v:,.0f}"