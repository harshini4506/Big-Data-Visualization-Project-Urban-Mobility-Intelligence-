from datetime import date

from src.filters import _safe_date_bounds


class FakeConnection:
    def __init__(self, bounds):
        self.bounds = bounds

    def execute(self, query):
        return self

    def fetchone(self):
        return self.bounds


def test_safe_date_bounds_uses_dataset_dates():
    connection = FakeConnection((date(2025, 1, 1), date(2025, 1, 31)))

    assert _safe_date_bounds(connection) == (date(2025, 1, 1), date(2025, 1, 31))


def test_safe_date_bounds_handles_empty_dataset():
    fallback = date.today()

    assert _safe_date_bounds(FakeConnection((None, None))) == (fallback, fallback)
