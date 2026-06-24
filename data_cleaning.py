import pandas as pd
import numpy as np
import os

os.makedirs('data/processed', exist_ok=True)

print("Starting data cleaning...")

# 1. nav_history.csv
print("Cleaning 02_nav_history.csv...")
df_nav = pd.read_csv('data/raw/02_nav_history.csv')
df_nav['date'] = pd.to_datetime(df_nav['date'])
df_nav = df_nav.sort_values(['amfi_code', 'date'])
df_nav = df_nav.drop_duplicates(subset=['amfi_code', 'date'])

# Forward fill missing NAV for weekends/holidays
amfi_codes = df_nav['amfi_code'].unique()
dates = pd.date_range(df_nav['date'].min(), df_nav['date'].max())
mux = pd.MultiIndex.from_product([amfi_codes, dates], names=['amfi_code', 'date'])

df_nav = df_nav.set_index(['amfi_code', 'date']).reindex(mux).reset_index()
df_nav['nav'] = df_nav.groupby('amfi_code')['nav'].ffill()

# Validate NAV > 0
df_nav = df_nav.dropna(subset=['nav'])
df_nav = df_nav[df_nav['nav'] > 0]
df_nav.to_csv('data/processed/02_nav_history.csv', index=False)

# 2. investor_transactions.csv
print("Cleaning 08_investor_transactions.csv...")
df_inv = pd.read_csv('data/raw/08_investor_transactions.csv')
df_inv['transaction_date'] = pd.to_datetime(df_inv['transaction_date']).dt.strftime('%Y-%m-%d')
df_inv['transaction_type'] = df_inv['transaction_type'].str.strip().str.title()
df_inv = df_inv[df_inv['amount_inr'] > 0]
valid_kyc = ['Verified', 'Pending', 'Rejected']
df_inv = df_inv[df_inv['kyc_status'].isin(valid_kyc)]
df_inv.to_csv('data/processed/08_investor_transactions.csv', index=False)

# 3. scheme_performance.csv
print("Cleaning 07_scheme_performance.csv...")
df_perf = pd.read_csv('data/raw/07_scheme_performance.csv')
return_cols = ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct']
for col in return_cols:
    df_perf[col] = pd.to_numeric(df_perf[col], errors='coerce')

df_perf = df_perf[(df_perf['expense_ratio_pct'] >= 0.1) & (df_perf['expense_ratio_pct'] <= 2.5)]

df_perf['anomaly_flag'] = False
for col in return_cols:
    df_perf.loc[(df_perf[col] > 150) | (df_perf[col] < -90), 'anomaly_flag'] = True

df_perf.to_csv('data/processed/07_scheme_performance.csv', index=False)

# Other files to copy over
files_to_copy = [
    '01_fund_master.csv', '03_aum_by_fund_house.csv', '04_monthly_sip_inflows.csv',
    '05_category_inflows.csv', '06_industry_folio_count.csv', '09_portfolio_holdings.csv',
    '10_benchmark_indices.csv'
]
for file in files_to_copy:
    df = pd.read_csv(f'data/raw/{file}')
    df.to_csv(f'data/processed/{file}', index=False)
    print(f"Copied {file}")

print("Data cleaning complete. 10 files saved to data/processed/")
