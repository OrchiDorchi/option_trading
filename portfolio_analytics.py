import pandas as pd
import numpy as np

def total_return(equity):
    return (equity[-1] - equity[0]) / equity[0]

def annualized_return(equity):
    total_return_ = total_return(equity)
    holding_period = len(equity) / 252
    annualized_return_ = (1 + total_return_) ** (1 / holding_period) - 1
    return annualized_return_

def drawdowns(equity:pd.Series):
    equity_array = equity.to_list()
    max_drawdown = 0
    peak = equity_array[0]

    drawdowns = []
    max_drawdowns = []

    for equity in equity_array:
        if equity > peak:
            peak = equity

        drawdown = (peak - equity) / peak
        drawdowns.append(drawdown)
        max_drawdown = max(max_drawdown, drawdown)
        max_drawdowns.append(max_drawdown)

    return np.array(max_drawdowns)*-100

def volatility(equity):
    daily_returns = equity.pct_change()
    return np.std(daily_returns)

def sharpe(equity):
    daily_returns = equity.pct_change()
    sharpe_ratio = np.mean(daily_returns) / np.std(daily_returns)
    sharpe_ratio = 252 ** 0.5 *sharpe_ratio
    return sharpe_ratio

def sortino(equity):
    daily_returns = equity.pct_change()
    mean = np.mean(daily_returns)
    std_neg = daily_returns[daily_returns<0].std()
    sortino_ratio = mean / std_neg
    sortino_ratio = 252 ** 0.5 *sortino_ratio
    return sortino_ratio