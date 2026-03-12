def fmt_currency(v: float) -> str:
    """Return a compact, human-readable currency string.
 
    Examples
    --------
    >>> fmt_currency(1_500_000_000_000)
    '$1.50T'
    >>> fmt_currency(2_300_000_000)
    '$2.3B'
    >>> fmt_currency(-450_000)
    '-$450.0K'
    >>> fmt_currency(0)
    '$0'
    """
    sign = "-" if v < 0 else ""
    v = abs(v)
    if v >= 1e12:
        return f"{sign}${v / 1e12:.2f}T"
    if v >= 1e9:
        return f"{sign}${v / 1e9:.1f}B"
    if v >= 1e6:
        return f"{sign}${v / 1e6:.1f}M"
    if v >= 1e3:
        return f"{sign}${v / 1e3:.1f}K"
    return f"{sign}${v:.0f}"