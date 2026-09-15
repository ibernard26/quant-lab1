"""Tests for the first-principles volatility pipeline in main.py.

These tests use Python's built-in unittest framework so no extra
dependencies are required. Expected values are worked out by hand or with
an independent calculation, NOT by calling the functions under test, so the
tests actually check the mathematics rather than agreeing with themselves.

Run with:  python3 -m unittest -v
"""

import math
import unittest

from main import (
    calculate_returns,
    calculate_mean,
    calculate_variance,
    calculate_volatility,
    calculate_annualized_volatility,
)

# How close two floating-point numbers must be to count as equal.
TOLERANCE = 1e-12

# The primary example used throughout the project.
PRIMARY_PRICES = [100.00, 105.00, 102.00, 108.00, 110.00]

# Returns worked out independently from PRIMARY_PRICES:
#   (105-100)/100 =  0.05
#   (102-105)/105 = -0.0285714285714...
#   (108-102)/102 =  0.0588235294117...
#   (110-108)/108 =  0.0185185185185...
PRIMARY_RETURNS = [
    0.05,
    -3.0 / 105.0,
    6.0 / 102.0,
    2.0 / 108.0,
]


class TestCalculateReturns(unittest.TestCase):
    def test_known_returns(self):
        # Simple, hand-checkable case: 100 -> 110 -> 99.
        prices = [100.0, 110.0, 99.0]
        expected = [0.10, -0.10]  # +10%, then -10%
        result = calculate_returns(prices)
        self.assertEqual(len(result), len(expected))
        for got, want in zip(result, expected):
            self.assertAlmostEqual(got, want, delta=TOLERANCE)

    def test_primary_returns(self):
        result = calculate_returns(PRIMARY_PRICES)
        for got, want in zip(result, PRIMARY_RETURNS):
            self.assertAlmostEqual(got, want, delta=TOLERANCE)

    def test_negative_returns_are_allowed(self):
        # A falling price series must produce valid negative returns.
        result = calculate_returns([100.0, 90.0, 81.0])
        self.assertAlmostEqual(result[0], -0.10, delta=TOLERANCE)
        self.assertAlmostEqual(result[1], -0.10, delta=TOLERANCE)

    def test_fewer_than_two_prices_raises(self):
        with self.assertRaises(ValueError):
            calculate_returns([100.0])

    def test_empty_prices_raises(self):
        with self.assertRaises(ValueError):
            calculate_returns([])

    def test_zero_previous_price_raises(self):
        with self.assertRaises(ValueError):
            calculate_returns([0.0, 100.0])


class TestCalculateMean(unittest.TestCase):
    def test_known_mean(self):
        # (1 + 2 + 3 + 4) / 4 = 2.5
        self.assertAlmostEqual(calculate_mean([1, 2, 3, 4]), 2.5, delta=TOLERANCE)

    def test_single_value_mean(self):
        # Mean of one number is that number.
        self.assertAlmostEqual(calculate_mean([7.5]), 7.5, delta=TOLERANCE)

    def test_negative_values_mean(self):
        # (-2 + 2) / 2 = 0
        self.assertAlmostEqual(calculate_mean([-2, 2]), 0.0, delta=TOLERANCE)

    def test_empty_list_raises(self):
        with self.assertRaises(ValueError):
            calculate_mean([])


class TestCalculateVariance(unittest.TestCase):
    def test_known_population_variance(self):
        # Values [2, 4, 6]: mean = 4.
        # Squared deviations: 4, 0, 4 -> sum 8.
        # Population variance divides by n (=3): 8 / 3.
        self.assertAlmostEqual(
            calculate_variance([2, 4, 6]), 8.0 / 3.0, delta=TOLERANCE
        )

    def test_constant_values_have_zero_variance(self):
        # No spread means zero variance.
        self.assertAlmostEqual(calculate_variance([3, 3, 3, 3]), 0.0, delta=TOLERANCE)

    def test_divides_by_n_not_n_minus_1(self):
        # Values [0, 2]: mean = 1, squared deviations 1 and 1, sum = 2.
        # Population (divide by n=2) -> 1.0
        # Sample (divide by n-1=1) would be 2.0, which must NOT happen here.
        self.assertAlmostEqual(calculate_variance([0, 2]), 1.0, delta=TOLERANCE)


class TestCalculateVolatility(unittest.TestCase):
    def test_volatility_is_sqrt_of_variance(self):
        # Variance of [2, 4, 6] is 8/3, so volatility is sqrt(8/3).
        self.assertAlmostEqual(
            calculate_volatility([2, 4, 6]), math.sqrt(8.0 / 3.0), delta=TOLERANCE
        )

    def test_constant_values_have_zero_volatility(self):
        self.assertAlmostEqual(calculate_volatility([5, 5, 5]), 0.0, delta=TOLERANCE)


class TestCalculateAnnualizedVolatility(unittest.TestCase):
    def test_annualized_is_daily_times_sqrt_252(self):
        values = [2, 4, 6]
        daily = calculate_volatility(values)
        expected = daily * math.sqrt(252)
        self.assertAlmostEqual(
            calculate_annualized_volatility(values), expected, delta=TOLERANCE
        )

    def test_constant_values_have_zero_annualized_volatility(self):
        self.assertAlmostEqual(
            calculate_annualized_volatility([9, 9, 9]), 0.0, delta=TOLERANCE
        )


class TestPrimaryExampleEndToEnd(unittest.TestCase):
    """Cross-check the whole pipeline against independently computed numbers."""

    def test_full_pipeline_matches_independent_values(self):
        returns = calculate_returns(PRIMARY_PRICES)

        # Independently computed mean of PRIMARY_RETURNS.
        mean = sum(PRIMARY_RETURNS) / len(PRIMARY_RETURNS)
        self.assertAlmostEqual(calculate_mean(returns), mean, delta=TOLERANCE)

        # Independently computed population variance.
        squared_deviations = [(r - mean) ** 2 for r in PRIMARY_RETURNS]
        variance = sum(squared_deviations) / len(PRIMARY_RETURNS)
        self.assertAlmostEqual(calculate_variance(returns), variance, delta=TOLERANCE)

        # Daily volatility is the square root of variance.
        self.assertAlmostEqual(
            calculate_volatility(returns), math.sqrt(variance), delta=TOLERANCE
        )

        # Annualized volatility scales daily volatility by sqrt(252).
        self.assertAlmostEqual(
            calculate_annualized_volatility(returns),
            math.sqrt(variance) * math.sqrt(252),
            delta=TOLERANCE,
        )

    def test_known_annualized_value(self):
        # Hard-coded expected annualized volatility (~0.5430242481884),
        # computed once with an independent calculation and pinned here.
        result = calculate_annualized_volatility(calculate_returns(PRIMARY_PRICES))
        self.assertAlmostEqual(result, 0.5430242481883993, delta=1e-9)


if __name__ == "__main__":
    unittest.main()
