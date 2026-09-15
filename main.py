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


def calculate_variance(values):
    mean = calculate_mean(values)
    squared_deviations = []

    for value in values:
        deviation = value - mean
        squared_deviations.append(deviation ** 2)

    # Population variance: divide by n, not n - 1.
    return calculate_mean(squared_deviations)


def calculate_volatility(values):
    return calculate_variance(values) ** 0.5


def calculate_annualized_volatility(values):
    daily_volatility = calculate_volatility(values)
    return daily_volatility * (252 ** 0.5)


def main():
    prices = [100.00, 105.00, 102.00, 108.00, 110.00]

    # Build the pipeline one step at a time. Each value depends on the
    # previous one, so returns must exist before anything else is computed.
    returns = calculate_returns(prices)
    average_return = calculate_mean(returns)
    variance = calculate_variance(returns)
    volatility = calculate_volatility(returns)
    annualized_volatility = calculate_annualized_volatility(returns)

    print("Prices:", prices)
    print("Daily returns:", returns)
    print(f"Average daily return: {average_return:.4%}")
    print("Population variance:", variance)
    print(f"Daily volatility: {volatility:.4%}")
    print(f"Annualized volatility: {annualized_volatility:.4%}")


if __name__ == "__main__":
    main()
