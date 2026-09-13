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


