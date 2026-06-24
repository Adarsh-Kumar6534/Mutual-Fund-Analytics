import nbformat as nbf
import os

nb = nbf.v4.new_notebook()
cells = []

# Title
cells.append(nbf.v4.new_markdown_cell("# Mutual Fund Analytics - Performance Analytics"))

# Setup
cells.append(nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import sqlite3
import os

os.makedirs('../reports/charts', exist_ok=True)
os.makedirs('../reports', exist_ok=True)

# Connect to database
conn = sqlite3.connect('../bluestock_mf.db')

# Load dim_fund
df_fund = pd.read_sql('SELECT amfi_code, scheme_name, expense_ratio_pct FROM dim_fund', conn)
fund_dict = dict(zip(df_fund['amfi_code'], df_fund['scheme_name']))

# Load NAV
df_nav = pd.read_sql('SELECT amfi_code, date, nav FROM fact_nav ORDER BY date', conn)
df_nav['date'] = pd.to_datetime(df_nav['date'])

# Pivot NAV
nav_pivot = df_nav.pivot(index='date', columns='amfi_code', values='nav')

# Load Benchmarks
df_bench = pd.read_csv('../data/processed/10_benchmark_indices.csv')
df_bench['date'] = pd.to_datetime(df_bench['date'])
bench_pivot = df_bench.pivot(index='date', columns='index_name', values='close_value')

# Keep matching dates
common_dates = nav_pivot.index.intersection(bench_pivot.index)
nav_pivot = nav_pivot.loc[common_dates]
bench_pivot = bench_pivot.loc[common_dates]

print("Data loaded successfully.")"""))

# 1. Daily Returns
cells.append(nbf.v4.new_markdown_cell("""## 1. Daily Returns
Compute daily returns for all schemes and benchmark indices."""))
cells.append(nbf.v4.new_code_cell("""fund_returns = nav_pivot.pct_change().dropna()
bench_returns = bench_pivot.pct_change().dropna()

display(fund_returns.head())"""))

# 2. CAGR Calculation
cells.append(nbf.v4.new_markdown_cell("""## 2. CAGR (1yr, 3yr, 5yr)
Calculate Compound Annual Growth Rate."""))
cells.append(nbf.v4.new_code_cell("""def calc_cagr(series, years):
    # Get NAV start and end for the required window
    # Assuming 252 trading days per year
    days = years * 252
    if len(series) <= days:
        return np.nan
    nav_end = series.iloc[-1]
    nav_start = series.iloc[-days]
    return ((nav_end / nav_start) ** (1/years)) - 1

cagr_data = []
for col in nav_pivot.columns:
    cagr_data.append({
        'amfi_code': col,
        'CAGR_1Yr': calc_cagr(nav_pivot[col].dropna(), 1),
        'CAGR_3Yr': calc_cagr(nav_pivot[col].dropna(), 3),
        'CAGR_5Yr': calc_cagr(nav_pivot[col].dropna(), 5) # Note: dataset might be <5 yrs, will return NaN
    })
df_cagr = pd.DataFrame(cagr_data)
display(df_cagr.head())"""))

# 3. Sharpe & Sortino Ratios
cells.append(nbf.v4.new_markdown_cell("""## 3. Sharpe & Sortino Ratios
Compute Sharpe and Sortino ratios. Risk-free rate (Rf) = 6.5%"""))
cells.append(nbf.v4.new_code_cell("""rf_daily = 0.065 / 252

ratios_data = []
for col in fund_returns.columns:
    rets = fund_returns[col]
    excess_rets = rets - rf_daily
    
    # Sharpe
    ann_ret = rets.mean() * 252
    ann_vol = rets.std() * np.sqrt(252)
    sharpe = (ann_ret - 0.065) / ann_vol if ann_vol > 0 else np.nan
    
    # Sortino
    downside = excess_rets[excess_rets < 0]
    down_vol = downside.std() * np.sqrt(252) if len(downside) > 0 else np.nan
    sortino = (ann_ret - 0.065) / down_vol if down_vol > 0 else np.nan
    
    ratios_data.append({
        'amfi_code': col,
        'Sharpe_Ratio': sharpe,
        'Sortino_Ratio': sortino
    })

df_ratios = pd.DataFrame(ratios_data)
display(df_ratios.sort_values('Sharpe_Ratio', ascending=False).head())"""))

# 4. Alpha & Beta
cells.append(nbf.v4.new_markdown_cell("""## 4. Alpha & Beta
OLS regression of fund returns vs Nifty 100."""))
cells.append(nbf.v4.new_code_cell("""nifty100_rets = bench_returns['NIFTY100']

alpha_beta_data = []
for col in fund_returns.columns:
    rets = fund_returns[col]
    # Align dates
    df_reg = pd.concat([rets, nifty100_rets], axis=1).dropna()
    df_reg.columns = ['fund', 'bench']
    
    if len(df_reg) > 30:
        slope, intercept, r_value, p_value, std_err = stats.linregress(df_reg['bench'], df_reg['fund'])
        alpha_ann = intercept * 252
        beta = slope
    else:
        alpha_ann = np.nan
        beta = np.nan
        
    alpha_beta_data.append({
        'amfi_code': col,
        'Alpha': alpha_ann,
        'Beta': beta
    })

df_ab = pd.DataFrame(alpha_beta_data)
df_ab.to_csv('../reports/alpha_beta.csv', index=False)
display(df_ab.head())"""))

# 5. Maximum Drawdown
cells.append(nbf.v4.new_markdown_cell("""## 5. Maximum Drawdown
Calculate the maximum peak-to-trough drop."""))
cells.append(nbf.v4.new_code_cell("""dd_data = []
for col in nav_pivot.columns:
    series = nav_pivot[col].dropna()
    roll_max = series.cummax()
    drawdown = (series / roll_max) - 1
    max_dd = drawdown.min()
    worst_date = drawdown.idxmin()
    
    dd_data.append({
        'amfi_code': col,
        'Max_Drawdown': max_dd,
        'Worst_Date': worst_date
    })

df_dd = pd.DataFrame(dd_data)
display(df_dd.head())"""))

# 6. Fund Scorecard
cells.append(nbf.v4.new_markdown_cell("""## 6. Composite Fund Scorecard
Rank calculation (0-100) based on multiple metrics."""))
cells.append(nbf.v4.new_code_cell("""df_score = df_fund.merge(df_cagr, on='amfi_code')
df_score = df_score.merge(df_ratios, on='amfi_code')
df_score = df_score.merge(df_ab, on='amfi_code')
df_score = df_score.merge(df_dd, on='amfi_code')

# Handle NaNs for ranking
for col in ['CAGR_3Yr', 'Sharpe_Ratio', 'Alpha']:
    df_score[col] = df_score[col].fillna(df_score[col].median())

# Rankings (percentiles 0 to 1)
rank_3yr = df_score['CAGR_3Yr'].rank(pct=True)
rank_sharpe = df_score['Sharpe_Ratio'].rank(pct=True)
rank_alpha = df_score['Alpha'].rank(pct=True)
# Inverse rankings (lower is better)
rank_er = df_score['expense_ratio_pct'].rank(pct=True, ascending=False)
rank_dd = df_score['Max_Drawdown'].rank(pct=True) # Max_Drawdown is negative, so higher rank is better, wait, closer to 0 is better, so min() is worst. 
# Rank ascending=False means the highest (closest to 0) gets top score.
rank_dd = df_score['Max_Drawdown'].rank(pct=True, ascending=False)

# Composite Score
df_score['Scorecard'] = (0.30 * rank_3yr + 
                         0.25 * rank_sharpe + 
                         0.20 * rank_alpha + 
                         0.15 * rank_er + 
                         0.10 * rank_dd) * 100

df_score = df_score.sort_values('Scorecard', ascending=False)
df_score.to_csv('../reports/fund_scorecard.csv', index=False)
print("Scorecard saved to reports/fund_scorecard.csv")
display(df_score[['scheme_name', 'Scorecard', 'CAGR_3Yr', 'Sharpe_Ratio', 'Alpha', 'Max_Drawdown']].head(10))"""))

# 7. Benchmark Chart
cells.append(nbf.v4.new_markdown_cell("""## 7. Benchmark Comparison & Tracking Error
Plot top 5 funds vs Nifty 50 and Nifty 100."""))
cells.append(nbf.v4.new_code_cell("""top_5_codes = df_score['amfi_code'].head(5).tolist()

plt.figure(figsize=(14, 7))

# Rebase everything to 100 at the start of the common date window
start_date = nav_pivot.index.min()
nav_rebased = (nav_pivot[top_5_codes] / nav_pivot[top_5_codes].iloc[0]) * 100
bench_rebased = (bench_pivot[['NIFTY50', 'NIFTY100']] / bench_pivot[['NIFTY50', 'NIFTY100']].iloc[0]) * 100

for col in top_5_codes:
    plt.plot(nav_rebased.index, nav_rebased[col], label=fund_dict[col], alpha=0.8)

plt.plot(bench_rebased.index, bench_rebased['NIFTY50'], label='NIFTY 50', color='black', linewidth=2, linestyle='--')
plt.plot(bench_rebased.index, bench_rebased['NIFTY100'], label='NIFTY 100', color='red', linewidth=2, linestyle=':')

plt.title('Top 5 Funds vs Benchmarks (Rebased to 100)', fontsize=16)
plt.xlabel('Date', fontsize=12)
plt.ylabel('Growth', fontsize=12)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('../reports/charts/benchmark_comparison_chart.png')
plt.show()

# Calculate Tracking Error vs Nifty 50
print("Annualized Tracking Error vs NIFTY 50:")
for col in top_5_codes:
    te_daily = (fund_returns[col] - bench_returns['NIFTY50']).std()
    te_ann = te_daily * np.sqrt(252)
    print(f"{fund_dict[col]}: {te_ann:.2%}")"""))

nb['cells'] = cells
with open('notebooks/Performance_Analytics.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
print("Notebook generated successfully.")
