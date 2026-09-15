def calculate_returns(prices):
    if len(prices) < 2:
        raise ValueError("At least two prices are required.")

    returns = []

    for i in range(1, len(prices)):
        previous_price = prices[i - 1]
        current_price = prices[i]

        if previous_price == 0:
            raise ValueError("Cannot calculate a return from a zero price.")

        daily_return = (current_price - previous_price) / previous_price
        returns.append(daily_return)

    return returns


def calculate_mean(values):
    if len(values) == 0:
        raise ValueError("Cannot calculate the mean of an empty list.")

    total = 0

    for value in values:
        total = total + value

    return total / len(values)


def calculate_deviations(values):
    # Deviation of each value from the mean:  d_i = x_i - x_bar
    mean = calculate_mean(values)
    deviations = []

    for value in values:
        deviations.append(value - mean)

    return deviations


def calculate_squared_deviations(values):
    # Squared deviation of each value:  d_i^2 = (x_i - x_bar)^2
    squared_deviations = []

    for deviation in calculate_deviations(values):
        squared_deviations.append(deviation ** 2)

    return squared_deviations


def calculate_variance(values):
    # POPULATION variance: divide the sum of squared deviations by n.
    #   sigma^2 = (1 / n) * sum((x_i - x_bar)^2)
    # Averaging the squared deviations with calculate_mean divides by n.
    squared_deviations = calculate_squared_deviations(values)
    return calculate_mean(squared_deviations)


def calculate_volatility(values):
    # POPULATION standard deviation: the square root of the population variance.
    return calculate_variance(values) ** 0.5


def calculate_annualized_volatility(values):
    daily_volatility = calculate_volatility(values)
    return daily_volatility * (252 ** 0.5)


def calculate_sample_variance(values):
    # SAMPLE variance: divide the sum of squared deviations by n - 1
    # (Bessel's correction), which gives an unbiased estimate of the
    # variance of the underlying population from a finite sample.
    #   s^2 = (1 / (n - 1)) * sum((x_i - x_bar)^2)
    # Dividing by n - 1 means at least two observations are required.
    if len(values) < 2:
        raise ValueError("Sample variance requires at least two observations.")

    squared_deviations = calculate_squared_deviations(values)

    total = 0
    for squared_deviation in squared_deviations:
        total = total + squared_deviation

    return total / (len(values) - 1)


def calculate_sample_standard_deviation(values):
    # SAMPLE standard deviation: the square root of the sample variance.
    return calculate_sample_variance(values) ** 0.5


def convert_annual_rate_to_daily(annual_rate, periods_per_year=252):
    # Convert an annual (decimal) rate into an equivalent per-period rate,
    # assuming it compounds over `periods_per_year` trading days:
    #   (1 + daily_rate) ** periods_per_year = 1 + annual_rate
    #   => daily_rate = (1 + annual_rate) ** (1 / periods_per_year) - 1
    # This compounding conversion is used instead of the rough approximation
    # annual_rate / periods_per_year so the frequencies stay consistent.
    return (1 + annual_rate) ** (1 / periods_per_year) - 1


def calculate_excess_returns(returns, daily_risk_free_rate):
    # Excess return = asset return above the risk-free rate for the SAME period.
    #   excess_i = r_i - rf_daily
    # Both inputs must be daily decimal rates (e.g. 5% is 0.05, not 5).
    excess_returns = []

    for daily_return in returns:
        excess_returns.append(daily_return - daily_risk_free_rate)

    return excess_returns


def calculate_sharpe_ratio(returns, annual_risk_free_rate):
    # Basic (per-period) Sharpe ratio from first principles.
    #
    # Frequency assumptions:
    #   * `returns` are DAILY decimal returns (0.05 means +5%).
    #   * `annual_risk_free_rate` is an ANNUAL decimal rate (0.02 means 2%).
    # The annual risk-free rate is converted to a daily rate so the numerator
    # and denominator both live on a daily frequency.
    #
    #   Sharpe = mean(excess returns) / std(excess returns)
    #
    # The denominator uses the SAMPLE standard deviation (divide by n - 1),
    # which is the usual convention when returns are treated as a sample.
    daily_risk_free_rate = convert_annual_rate_to_daily(annual_risk_free_rate)
    excess_returns = calculate_excess_returns(returns, daily_risk_free_rate)

    average_excess_return = calculate_mean(excess_returns)
    excess_standard_deviation = calculate_sample_standard_deviation(excess_returns)

    if excess_standard_deviation == 0:
        # With no variation in excess returns the ratio would divide by zero.
        raise ValueError(
            "Sharpe ratio is undefined when excess returns have zero "
            "standard deviation."
        )

    # A negative average excess return produces a valid negative Sharpe ratio.
    return average_excess_return / excess_standard_deviation


def calculate_annualized_sharpe_ratio(returns, annual_risk_free_rate, periods_per_year=252):
    # Annualize a daily Sharpe ratio by scaling with sqrt(periods_per_year).
    # This is the standard approximation: the mean excess return scales with
    # the number of periods while the standard deviation scales with its
    # square root, so their ratio scales with sqrt(periods_per_year).
    daily_sharpe_ratio = calculate_sharpe_ratio(returns, annual_risk_free_rate)
    return daily_sharpe_ratio * (periods_per_year ** 0.5)


def main():
    prices = [100.00, 105.00, 102.00, 108.00, 110.00]

    # An annual risk-free rate expressed as a decimal (2% -> 0.02).
    annual_risk_free_rate = 0.02

    # Build the pipeline one step at a time. Each value depends on the
    # previous one, so returns must exist before anything else is computed.
    returns = calculate_returns(prices)
    average_return = calculate_mean(returns)

    # Population statistics (divide by n).
    population_variance = calculate_variance(returns)
    daily_volatility = calculate_volatility(returns)
    annualized_volatility = calculate_annualized_volatility(returns)

    # Sample statistics (divide by n - 1).
    sample_variance = calculate_sample_variance(returns)
    sample_standard_deviation = calculate_sample_standard_deviation(returns)

    # Sharpe ratio (daily returns vs. an annual risk-free rate).
    daily_risk_free_rate = convert_annual_rate_to_daily(annual_risk_free_rate)
    excess_returns = calculate_excess_returns(returns, daily_risk_free_rate)
    sharpe_ratio = calculate_sharpe_ratio(returns, annual_risk_free_rate)
    annualized_sharpe_ratio = calculate_annualized_sharpe_ratio(
        returns, annual_risk_free_rate
    )

    print("Prices:", prices)
    print("Daily returns:", returns)
    print(f"Average daily return: {average_return:.4%}")

    print()
    print("--- Population statistics (divide by n) ---")
    print("Population variance:", population_variance)
    print(f"Daily volatility (population std): {daily_volatility:.4%}")
    print(f"Annualized volatility: {annualized_volatility:.4%}")

    print()
    print("--- Sample statistics (divide by n - 1) ---")
    print("Sample variance:", sample_variance)
    print(f"Sample standard deviation: {sample_standard_deviation:.4%}")

    print()
    print("--- Sharpe ratio ---")
    print(f"Annual risk-free rate: {annual_risk_free_rate:.4%}")
    print(f"Daily risk-free rate: {daily_risk_free_rate:.6%}")
    print("Excess returns:", excess_returns)
    print(f"Sharpe ratio (daily): {sharpe_ratio:.4f}")
    print(f"Annualized Sharpe ratio: {annualized_sharpe_ratio:.4f}")


if __name__ == "__main__":
    main()
