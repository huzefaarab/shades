from math_utils import multiply, add

def test_multiply():
    assert multiply(2,3)==6
    assert multiply(2,0)==0
    assert multiply(2,4)==8
    assert multiply(5,3)==15

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
    assert add(-2, -3) == -5
