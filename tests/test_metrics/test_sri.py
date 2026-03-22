"""Tests for SRI aggregation."""
from stress.metrics.sri import compute_sri


def test_perfect_sri():
    proxies = {"gds": 1.0, "arr": 1.0, "ist": 1.0, "rec": 1.0, "cfr": 1.0}
    result = compute_sri(proxies)
    assert result.sri == 100.0


def test_partial_na_makes_sri_na():
    proxies = {"gds": 1.0, "arr": None, "ist": 1.0, "rec": 1.0, "cfr": 1.0}
    result = compute_sri(proxies)
    assert result.sri is None
    assert result.na_reason is not None


def test_all_na():
    proxies = {"gds": None, "arr": None, "ist": None, "rec": None, "cfr": None}
    result = compute_sri(proxies)
    assert result.sri is None


def test_average():
    proxies = {"gds": 0.8, "arr": 0.6, "ist": 1.0, "rec": 0.4, "cfr": 0.2}
    result = compute_sri(proxies)
    expected = ((0.8 + 0.6 + 1.0 + 0.4 + 0.2) / 5.0) * 100.0
    assert abs(result.sri - expected) < 0.1
