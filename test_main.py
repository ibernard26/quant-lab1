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
    calculate_deviations,
    calculate_squared_deviations,
    calculate_sample_variance,
    calculate_sample_standard_deviation,
    convert_annual_rate_to_daily,
    calculate_excess_returns,
    calculate_sharpe_ratio,
    calculate_annualized_sharpe_ratio,
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


class TestDeviationHelpers(unittest.TestCase):
    def test_known_deviations(self):
        # Values [2, 4, 6]: mean = 4, so deviations are -2, 0, 2.
        result = calculate_deviations([2, 4, 6])
        for got, want in zip(result, [-2.0, 0.0, 2.0]):
            self.assertAlmostEqual(got, want, delta=TOLERANCE)

    def test_known_squared_deviations(self):
        # Squares of -2, 0, 2 are 4, 0, 4.
        result = calculate_squared_deviations([2, 4, 6])
        for got, want in zip(result, [4.0, 0.0, 4.0]):
            self.assertAlmostEqual(got, want, delta=TOLERANCE)

    def test_deviations_sum_to_zero(self):
        # By definition the deviations from the mean always sum to zero.
        result = calculate_deviations([1.0, 2.5, 3.0, 9.5])
        self.assertAlmostEqual(sum(result), 0.0, delta=TOLERANCE)


class TestCalculateSampleVariance(unittest.TestCase):
    def test_known_sample_variance(self):
        # Values [2, 4, 6]: mean = 4, squared deviations 4, 0, 4 -> sum 8.
        # Sample variance divides by n - 1 (= 2): 8 / 2 = 4.0.
        self.assertAlmostEqual(calculate_sample_variance([2, 4, 6]), 4.0, delta=TOLERANCE)

    def test_sample_differs_from_population_by_n_over_n_minus_1(self):
        # For the same data, sample variance = population variance * n / (n - 1).
        values = PRIMARY_RETURNS
        n = len(values)
        population = calculate_variance(values)
        expected_sample = population * n / (n - 1)
        self.assertAlmostEqual(
            calculate_sample_variance(values), expected_sample, delta=TOLERANCE
        )

    def test_explicit_n_vs_n_minus_1_distinction(self):
        # Values [0, 2]: mean = 1, squared deviations 1 and 1, sum = 2.
        # Population (divide by n = 2) -> 1.0
        # Sample (divide by n - 1 = 1) -> 2.0
        self.assertAlmostEqual(calculate_variance([0, 2]), 1.0, delta=TOLERANCE)
        self.assertAlmostEqual(calculate_sample_variance([0, 2]), 2.0, delta=TOLERANCE)

    def test_one_observation_raises(self):
        # Sample variance is undefined for a single observation (n - 1 = 0).
        with self.assertRaises(ValueError):
            calculate_sample_variance([5.0])

    def test_empty_list_raises(self):
        with self.assertRaises(ValueError):
            calculate_sample_variance([])


class TestCalculateSampleStandardDeviation(unittest.TestCase):
    def test_sample_std_is_sqrt_of_sample_variance(self):
        # Sample variance of [2, 4, 6] is 4.0, so sample std is 2.0.
        self.assertAlmostEqual(
            calculate_sample_standard_deviation([2, 4, 6]), 2.0, delta=TOLERANCE
        )

    def test_one_observation_raises(self):
        with self.assertRaises(ValueError):
            calculate_sample_standard_deviation([5.0])


class TestConvertAnnualRateToDaily(unittest.TestCase):
    def test_zero_rate_maps_to_zero(self):
        self.assertAlmostEqual(convert_annual_rate_to_daily(0.0), 0.0, delta=TOLERANCE)

    def test_compounds_back_to_annual_rate(self):
        # The defining property: compounding the daily rate over 252 trading
        # days must reproduce the annual rate. This checks the conversion
        # against its own definition, independently of the implementation.
        annual = 0.02
        daily = convert_annual_rate_to_daily(annual)
        self.assertAlmostEqual((1 + daily) ** 252 - 1, annual, delta=1e-12)

    def test_custom_periods_per_year(self):
        # With 12 periods, compounding 12 times must reproduce the annual rate.
        annual = 0.06
        daily = convert_annual_rate_to_daily(annual, periods_per_year=12)
        self.assertAlmostEqual((1 + daily) ** 12 - 1, annual, delta=1e-12)


class TestCalculateExcessReturns(unittest.TestCase):
    def test_known_excess_returns(self):
        # Subtracting a constant daily risk-free rate of 0.005 from each return.
        result = calculate_excess_returns([0.01, 0.02, 0.03], 0.005)
        for got, want in zip(result, [0.005, 0.015, 0.025]):
            self.assertAlmostEqual(got, want, delta=TOLERANCE)

    def test_zero_rate_leaves_returns_unchanged(self):
        result = calculate_excess_returns([0.01, -0.02], 0.0)
        for got, want in zip(result, [0.01, -0.02]):
            self.assertAlmostEqual(got, want, delta=TOLERANCE)


class TestSharpeRatio(unittest.TestCase):
    def test_known_positive_sharpe(self):
        # returns [0.01, 0.02, 0.03] with a 0% risk-free rate.
        # Excess returns equal the returns; mean = 0.02.
        # Sample variance = ((0.01)^2 + 0 + (0.01)^2) / (3 - 1) = 0.0001.
        # Sample std = 0.01, so Sharpe = 0.02 / 0.01 = 2.0.
        result = calculate_sharpe_ratio([0.01, 0.02, 0.03], 0.0)
        self.assertAlmostEqual(result, 2.0, delta=1e-12)

    def test_known_negative_sharpe(self):
        # returns [-0.03, -0.01, -0.02] with a 0% risk-free rate.
        # mean = -0.02, sample std = 0.01, so Sharpe = -2.0.
        result = calculate_sharpe_ratio([-0.03, -0.01, -0.02], 0.0)
        self.assertAlmostEqual(result, -2.0, delta=1e-12)

    def test_higher_risk_free_rate_lowers_sharpe(self):
        # A positive risk-free rate reduces excess returns (numerator) while
        # leaving their spread unchanged, so the Sharpe ratio must fall.
        base = calculate_sharpe_ratio([0.01, 0.02, 0.03], 0.0)
        with_rf = calculate_sharpe_ratio([0.01, 0.02, 0.03], 0.02)
        self.assertLess(with_rf, base)

    def test_zero_volatility_raises(self):
        # Constant returns give zero-spread excess returns; the Sharpe ratio
        # is undefined and must raise rather than divide by zero.
        with self.assertRaises(ValueError):
            calculate_sharpe_ratio([0.01, 0.01, 0.01], 0.0)

    def test_too_few_returns_raise(self):
        # The sample standard deviation in the denominator needs >= 2 points.
        with self.assertRaises(ValueError):
            calculate_sharpe_ratio([0.01], 0.0)


class TestAnnualizedSharpeRatio(unittest.TestCase):
    def test_annualized_is_daily_times_sqrt_252(self):
        returns = [0.01, 0.02, 0.03]
        daily = calculate_sharpe_ratio(returns, 0.0)  # = 2.0
        expected = daily * math.sqrt(252)
        self.assertAlmostEqual(
            calculate_annualized_sharpe_ratio(returns, 0.0), expected, delta=1e-9
        )

    def test_negative_annualized_sharpe(self):
        # A negative daily Sharpe stays negative after annualization.
        result = calculate_annualized_sharpe_ratio([-0.03, -0.01, -0.02], 0.0)
        self.assertLess(result, 0.0)
        self.assertAlmostEqual(result, -2.0 * math.sqrt(252), delta=1e-9)


class TestSharpePrimaryExample(unittest.TestCase):
    """Cross-check the Sharpe pipeline on the primary prices with an
    independent, self-contained calculation (no functions under test)."""

    def test_primary_sharpe_matches_independent_value(self):
        returns = calculate_returns(PRIMARY_PRICES)
        annual_rf = 0.02

        # Independent recomputation.
        daily_rf = (1 + annual_rf) ** (1 / 252) - 1
        excess = [r - daily_rf for r in returns]
        n = len(excess)
        mean_excess = sum(excess) / n
        sample_var = sum((e - mean_excess) ** 2 for e in excess) / (n - 1)
        sample_std = math.sqrt(sample_var)
        expected_sharpe = mean_excess / sample_std

        self.assertAlmostEqual(
            calculate_sharpe_ratio(returns, annual_rf), expected_sharpe, delta=1e-12
        )
        self.assertAlmostEqual(
            calculate_annualized_sharpe_ratio(returns, annual_rf),
            expected_sharpe * math.sqrt(252),
            delta=1e-9,
        )


if __name__ == "__main__":
    unittest.main()
