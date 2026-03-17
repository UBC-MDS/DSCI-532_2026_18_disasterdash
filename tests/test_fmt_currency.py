"""
pytest tests for fmt_currency helper function 
"""
import sys                   
sys.path.insert(0, ".")  # look in root

from src.fmt_currency import fmt_currency

def test_billions():
    """ Test that figures in the billions are formatted correctly"""
    assert fmt_currency(2_300_000_000) == "$2.3B"

def test_millions():
    """ Test that figures in the millions are formatted correctly"""
    assert fmt_currency(450_000_000) == "$450.0M"

def test_thousands():
    """ Test that figures in the thoudands are formatted correctly"""
    assert fmt_currency(7_500) == "$7.5K"

def test_zero():
    """ Test that a figure of zero is formatted correctly"""
    assert fmt_currency(0) == "$0"

def test_negative():
    """ Test that negative figures are formatted correctly"""
    assert fmt_currency(-2_300_000_000) == "-$2.3B"