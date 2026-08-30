from positive_checker import is_positive

def test_positive_number():
    assert is_positive(5) is True

def test_negative_number():
    assert is_positive(-5) is False

def test_zero():
    assert is_positive(0) is False
