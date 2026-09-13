prices = [100.00, 105.00, 102.00, 108.00, 110.00]

returns = []

for i in range(1, len(prices)):
    previous_price = prices[i - 1]
    current_price = prices[i]

    daily_return = (current_price - previous_price) / previous_price

    returns.append(daily_return)

print(returns)
total_return = 0

for daily_return in returns:
    total_return = total_return + daily_return

average_return = total_return / len(returns)

print("Average daily return:", average_return)
deviations = []

for daily_return in returns:
    deviation = daily_return - average_return
    deviations.append(deviation)

print("Return deviations:", deviations)

squared_deviations = []

for deviation in deviations:
    squared_deviation = deviation ** 2
    squared_deviations.append(squared_deviation)

variance = sum(squared_deviations) / len(squared_deviations)

print("Squared deviations:", squared_deviations)
print("Variance:", variance)
volatility = variance ** 0.5

print("Daily volatility:", volatility)
print(f"Daily volatility (%): {volatility:.2%}")
