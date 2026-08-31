from agent import is_even

def test_is_even():
    assert is_even(2) is True
    assert is_even(10) is True
    assert is_even(7) is False
