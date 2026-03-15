"""
pytest tests for fmt_num helper function
"""
import sys
sys.path.insert(0, ".")   # look in root

from src.fmt_num import fmt_num

def test_millions():
    """ Test that numbers in the miliions are formatted correctly"""
    assert fmt_num(2_500_000) == "2.5M"

def test_thousands():
    """ Test that numbers in the thousands are formatted correctly"""
    assert fmt_num(18_000) == "18.0K"
 
def test_sub_thousand():
    """ Test that numbers < 1000 are formatted correctly"""
    assert fmt_num(42) == "42"
