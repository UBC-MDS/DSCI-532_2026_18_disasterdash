"""
pytest tests for fmt_currency helper function 
"""
import sys                   
sys.path.insert(0, ".")  # look in root

from src.fmt_currency import fmt_currency

def test_billions():
    assert fmt_currency(2_300_000_000) == "$2.3B"

def test_millions():
    assert fmt_currency(450_000_000) == "$450.0M"

def test_thousands():
    assert fmt_currency(7_500) == "$7.5K"

def test_zero():
    assert fmt_currency(0) == "$0"

def test_negative():
    assert fmt_currency(-2_300_000_000) == "-$2.3B"