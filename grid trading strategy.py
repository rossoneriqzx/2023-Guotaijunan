import pandas as pd

# Read the Excel file
df = pd.read_excel('/Users/qiuzixiao/Downloads/Wind.xlsx')

# Extract the required data columns
dates = df['日期'].tolist()  # '日期' means 'Date'
net_asset_values = df['单位净值'].tolist()  # '单位净值' means 'Net Asset Value'

# Set grid trading parameters
num_levels = 5  # Number of grid levels
grid_spacing = 0.02  # Grid spacing, adjust based on actual situation
initial_investment = 10000  # Initial investment amount

# Calculate grid price levels
grid_prices = [net_asset_values[0] * (1 - i * grid_spacing) for i in range(num_levels)]

# Initialize investment and holdings
investment = initial_investment
holdings = 0  # Number of units held

# Execute grid trading
for i in range(1, len(net_asset_values)):
    for price in grid_prices:
        if net_asset_values[i] <= price:  # Buy when net asset value is less than or equal to the grid price
            buy_quantity = (investment / num_levels) / price
            investment -= buy_quantity * price
            holdings += buy_quantity
            print(f"Bought {buy_quantity:.2f} units at price {price:.2f}, remaining investment {investment:.2f}")

    for price in grid_prices:
        if net_asset_values[i] >= price:  # Sell when net asset value is greater than or equal to the grid price
            sell_quantity = (holdings / num_levels)
            investment += sell_quantity * price
            holdings -= sell_quantity
            print(f"Sold {sell_quantity:.2f} units at price {price:.2f}, remaining investment {investment:.2f}")

# Print the final investment amount
final_investment_value = investment + holdings * net_asset_values[-1]
print("Final investment value:", final_investment_value)
