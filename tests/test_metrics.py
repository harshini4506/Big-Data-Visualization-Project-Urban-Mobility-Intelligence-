from src.metrics import percentage_change
def test_percentage_change_handles_zero_baseline():
    assert percentage_change(10, 0) is None
    assert percentage_change(110, 100) == 10

