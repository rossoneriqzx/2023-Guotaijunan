#!/usr/bin/env python3

import pandas as pd


# 读取Excel数据表

df = pd.read_excel('/Users/qiuzixiao/Downloads/离谱.xlsx')


# 提取所需的数据列
dates = df['日期'].tolist()
net_asset_values = df['单位净值'].tolist()

# 设置网格交易参数
num_levels = 5  # 网格级别数量
grid_spacing = 0.02  # 网格间距，根据实际情况调整
investment = 10000  # 初始投资金额

# 计算网格价格水平
grid_prices = [net_asset_values[0] * (1 - i * grid_spacing) for i in range(num_levels)]

# 执行网格交易
for i in range(1, len(net_asset_values)):
    for price in grid_prices:
        if net_asset_values[i] >= price:  # 当单位净值超过网格价格时执行买入操作
            buy_quantity = investment / num_levels / price
            investment -= buy_quantity * price
            print(f"买入 {buy_quantity:.2f} 份于价格 {price:.2f}，剩余投资额 {investment:.2f}")

    for price in grid_prices:
        if net_asset_values[i] <= price:  # 当单位净值低于网格价格时执行卖出操作
            sell_quantity = investment / num_levels / price
            investment += sell_quantity * price
            print(f"卖出 {sell_quantity:.2f} 份于价格 {price:.2f}，剩余投资额 {investment:.2f}")

# 打印最终投资额
print("最终投资额:", investment)
