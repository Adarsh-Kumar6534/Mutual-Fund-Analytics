import pandas as pd
import sqlite3
import sqlalchemy
import os

print("Creating database and loading schema...")

# SQLAlchemy engine
engine = sqlalchemy.create_engine('sqlite:///bluestock_mf.db')

# Execute schema.sql to create tables
with open('sql/schema.sql', 'r') as f:
    schema = f.read()

with sqlite3.connect('bluestock_mf.db') as conn:
    conn.executescript(schema)

print("Schema created. Loading processed data...")

# 1. Load dim_fund
df_fund = pd.read_csv('data/processed/01_fund_master.csv')
df_fund.to_sql('dim_fund', con=engine, if_exists='append', index=False)

# 2. Generate and load dim_date
dates = set()
df_nav = pd.read_csv('data/processed/02_nav_history.csv')
dates.update(df_nav['date'].unique())

df_inv = pd.read_csv('data/processed/08_investor_transactions.csv')
dates.update(df_inv['transaction_date'].unique())

df_aum = pd.read_csv('data/processed/03_aum_by_fund_house.csv')
dates.update(df_aum['date'].unique())

dates = list(dates)
df_date = pd.DataFrame({'date': pd.to_datetime(dates)})
df_date['year'] = df_date['date'].dt.year
df_date['month'] = df_date['date'].dt.month
df_date['day'] = df_date['date'].dt.day
df_date['quarter'] = df_date['date'].dt.quarter
df_date['day_of_week'] = df_date['date'].dt.dayofweek
df_date['is_weekend'] = df_date['day_of_week'].isin([5, 6]).astype(int)
df_date['date'] = df_date['date'].dt.strftime('%Y-%m-%d')
df_date.to_sql('dim_date', con=engine, if_exists='append', index=False)

# 3. Load fact_nav
df_nav.to_sql('fact_nav', con=engine, if_exists='append', index=False)

# 4. Load fact_transactions
df_inv.to_sql('fact_transactions', con=engine, if_exists='append', index=False)

# 5. Load fact_performance
df_perf = pd.read_csv('data/processed/07_scheme_performance.csv')
df_perf.to_sql('fact_performance', con=engine, if_exists='append', index=False)

# 6. Load fact_aum
df_aum.to_sql('fact_aum', con=engine, if_exists='append', index=False)

print("Data loaded successfully!")

# Verify row counts
queries = {
    'dim_fund': len(df_fund),
    'dim_date': len(df_date),
    'fact_nav': len(df_nav),
    'fact_transactions': len(df_inv),
    'fact_performance': len(df_perf),
    'fact_aum': len(df_aum)
}

with engine.connect() as conn:
    for table, expected in queries.items():
        result = conn.execute(sqlalchemy.text(f"SELECT COUNT(*) FROM {table}")).scalar()
        print(f"Table {table}: Expected={expected}, Actual={result} -> {'OK' if expected == result else 'MISMATCH'}")
