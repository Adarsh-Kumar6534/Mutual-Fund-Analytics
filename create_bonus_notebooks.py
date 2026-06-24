import nbformat as nbf
import os

def create_monte_carlo():
    nb = nbf.v4.new_notebook()
    
    cells = []
    
    cells.append(nbf.v4.new_markdown_cell("# Bonus 3: Monte Carlo Simulation (5-Year NAV Projection)"))
    cells.append(nbf.v4.new_markdown_cell("Projecting NAV growth over 5 years (1260 trading days) with uncertainty bands using Geometric Brownian Motion."))
    
    code1 = """import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

conn = sqlite3.connect('../bluestock_mf.db')

# Fetch NAV for a top fund
df_nav = pd.read_sql("SELECT date, nav FROM fact_nav WHERE amfi_code = 119598 ORDER BY date", conn)
df_nav['date'] = pd.to_datetime(df_nav['date'])
df_nav.set_index('date', inplace=True)
df_nav['daily_return'] = df_nav['nav'].pct_change()
df_nav.dropna(inplace=True)

# Parameters
mu = df_nav['daily_return'].mean()
sigma = df_nav['daily_return'].std()
days = 1260  # 5 years (252 * 5)
simulations = 1000
start_nav = df_nav['nav'].iloc[-1]

np.random.seed(42)
sim_returns = np.random.normal(mu, sigma, (days, simulations))
sim_navs = np.zeros_like(sim_returns)
sim_navs[0] = start_nav

for t in range(1, days):
    sim_navs[t] = sim_navs[t-1] * (1 + sim_returns[t])

plt.figure(figsize=(12, 6))
plt.plot(sim_navs, color='blue', alpha=0.01)
plt.title('Monte Carlo Simulation of NAV for Next 5 Years (1000 Scenarios)')
plt.xlabel('Trading Days')
plt.ylabel('Projected NAV')
plt.grid(True, alpha=0.3)
plt.savefig('../reports/charts/monte_carlo_nav.png', dpi=300)
plt.show()"""
    cells.append(nbf.v4.new_code_cell(code1))
    
    code2 = """# Calculate Percentiles
final_navs = sim_navs[-1, :]
print(f"Current NAV: {start_nav:.2f}")
print(f"Median Expected NAV (5 yrs): {np.percentile(final_navs, 50):.2f}")
print(f"95% Confidence Interval: [{np.percentile(final_navs, 2.5):.2f}, {np.percentile(final_navs, 97.5):.2f}]")"""
    cells.append(nbf.v4.new_code_cell(code2))
    
    nb['cells'] = cells
    with open('notebooks/Monte_Carlo_Simulation.ipynb', 'w') as f:
        nbf.write(nb, f)

def create_markowitz():
    nb = nbf.v4.new_notebook()
    
    cells = []
    
    cells.append(nbf.v4.new_markdown_cell("# Bonus 4: Markowitz Efficient Frontier (Portfolio Optimization)"))
    cells.append(nbf.v4.new_markdown_cell("Optimizing weights for 5 selected funds to maximize the Sharpe Ratio."))
    
    code1 = """import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import scipy.optimize as sco

conn = sqlite3.connect('../bluestock_mf.db')

# Selected Top 5 Equity Funds
funds = {
    119598: 'SBI Small Cap',
    112268: 'Nippon India Large Cap',
    120465: 'HDFC Mid-Cap Opportunities',
    118989: 'ICICI Pru Value Discovery',
    122639: 'Parag Parikh Flexi Cap'
}

df_list = []
for code in funds.keys():
    df = pd.read_sql(f"SELECT date, nav FROM fact_nav WHERE amfi_code = {code}", conn)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df.rename(columns={'nav': funds[code]}, inplace=True)
    df_list.append(df)

df_all = pd.concat(df_list, axis=1).dropna()
returns = df_all.pct_change().dropna()

mean_returns = returns.mean() * 252
cov_matrix = returns.cov() * 252
num_portfolios = 10000
risk_free_rate = 0.065

results = np.zeros((3, num_portfolios))
weights_record = []

np.random.seed(42)
for i in range(num_portfolios):
    weights = np.random.random(5)
    weights /= np.sum(weights)
    weights_record.append(weights)
    
    port_return = np.sum(mean_returns * weights)
    port_stddev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    
    results[0,i] = port_return
    results[1,i] = port_stddev
    results[2,i] = (port_return - risk_free_rate) / port_stddev

max_sharpe_idx = np.argmax(results[2])
optimal_weights = weights_record[max_sharpe_idx]

plt.figure(figsize=(10, 6))
plt.scatter(results[1,:], results[0,:], c=results[2,:], cmap='viridis', marker='o')
plt.title('Markowitz Efficient Frontier')
plt.xlabel('Expected Volatility')
plt.ylabel('Expected Return')
plt.colorbar(label='Sharpe Ratio')
plt.scatter(results[1, max_sharpe_idx], results[0, max_sharpe_idx], marker='*', color='r', s=500, label='Maximum Sharpe Ratio')
plt.legend()
plt.savefig('../reports/charts/efficient_frontier.png', dpi=300)
plt.show()

print("Optimal Weights:")
for i, fund in enumerate(funds.values()):
    print(f"{fund}: {optimal_weights[i]*100:.2f}%")"""
    cells.append(nbf.v4.new_code_cell(code1))
    
    nb['cells'] = cells
    with open('notebooks/Portfolio_Optimization.ipynb', 'w') as f:
        nbf.write(nb, f)

if __name__ == "__main__":
    create_monte_carlo()
    create_markowitz()
    print("Notebooks generated successfully.")
