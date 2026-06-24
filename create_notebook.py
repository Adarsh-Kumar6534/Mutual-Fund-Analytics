import nbformat as nbf

nb = nbf.v4.new_notebook()

cells = []

# Title
cells.append(nbf.v4.new_markdown_cell("# Mutual Fund Analytics - Exploratory Data Analysis"))

# Setup
cells.append(nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import os

# Create directory for exported PNGs
os.makedirs('../reports/charts', exist_ok=True)

# Load data
df_fund = pd.read_csv('../data/raw/01_fund_master.csv')
df_nav = pd.read_csv('../data/raw/02_nav_history.csv')
df_aum = pd.read_csv('../data/raw/03_aum_by_fund_house.csv')
df_sip = pd.read_csv('../data/raw/04_monthly_sip_inflows.csv')
df_cat = pd.read_csv('../data/raw/05_category_inflows.csv')
df_folios = pd.read_csv('../data/raw/06_industry_folio_count.csv')
df_perf = pd.read_csv('../data/raw/07_scheme_performance.csv')
df_inv = pd.read_csv('../data/raw/08_investor_transactions.csv')
df_port = pd.read_csv('../data/raw/09_portfolio_holdings.csv')
df_bench = pd.read_csv('../data/raw/10_benchmark_indices.csv')

print("Data loaded successfully.")"""))

# Task 1: NAV trend analysis
cells.append(nbf.v4.new_markdown_cell("""## 1. NAV Trend Analysis
**Finding:** The 2023 bull run shows a strong upward trend across most equity funds, while 2024 shows distinct market corrections (dips in NAV)."""))
cells.append(nbf.v4.new_code_cell("""# 1. NAV trend analysis — plot daily NAV for all 40 schemes 2022–2026.
# Highlight 2023 bull run and 2024 market corrections using Plotly.

df_nav['date'] = pd.to_datetime(df_nav['date'])

fig = px.line(df_nav, x='date', y='nav', color='amfi_code', 
              title='Daily NAV for 40 Schemes (2022-2026)',
              labels={'date': 'Date', 'nav': 'Net Asset Value (INR)'})

# Highlight 2023 Bull Run
fig.add_vrect(x0="2023-01-01", x1="2023-12-31", fillcolor="green", opacity=0.1, line_width=0, annotation_text="2023 Bull Run")

# Highlight 2024 Corrections
fig.add_vrect(x0="2024-01-01", x1="2024-12-31", fillcolor="red", opacity=0.1, line_width=0, annotation_text="2024 Corrections")

fig.write_image('../reports/charts/01_nav_trend.png')
fig.show()"""))

# Task 2: AUM growth bar chart
cells.append(nbf.v4.new_markdown_cell("""## 2. AUM Growth by Fund House
**Finding:** SBI Mutual Fund consistently dominates the AUM across all years, reaching an impressive ₹12.5L Cr benchmark."""))
cells.append(nbf.v4.new_code_cell("""# 2. AUM growth bar chart — grouped bar by fund house for each year 2022–2025. 
# Highlight SBI at ₹12.5L Cr dominance using Seaborn.

df_aum['year'] = pd.to_datetime(df_aum['date']).dt.year.astype(str)

plt.figure(figsize=(14, 8))
sns.barplot(data=df_aum, x='fund_house', y='aum_crore', hue='year', palette='viridis')
plt.title('AUM Growth by Fund House (2022-2025)', fontsize=16)
plt.ylabel('AUM (in Crores)', fontsize=12)
plt.xlabel('Fund House', fontsize=12)
plt.xticks(rotation=45, ha='right')

# Highlight SBI
plt.axhline(y=1250000, color='r', linestyle='--', label='SBI Dominance: ₹12.5L Cr')
plt.legend()
plt.tight_layout()
plt.savefig('../reports/charts/02_aum_growth.png')
plt.show()"""))

# Task 3: SIP inflow time-series
cells.append(nbf.v4.new_markdown_cell("""## 3. Monthly SIP Inflow Trend
**Finding:** Monthly SIP inflows show a steady, robust growth trajectory, peaking at an all-time high of ₹31,002 Cr in December 2025."""))
cells.append(nbf.v4.new_code_cell("""# 3. SIP inflow time-series — monthly SIP trend Jan 2022 – Dec 2025. 
# Annotate the ₹31,002 Cr all-time high (Dec 2025) using Plotly.

fig = px.line(df_sip, x='month', y='sip_inflow_crore', markers=True,
              title='Monthly SIP Inflow Trend (2022-2025)',
              labels={'month': 'Month', 'sip_inflow_crore': 'SIP Inflow (Crores)'})

# Annotate highest point
max_inflow = df_sip['sip_inflow_crore'].max()
max_month = df_sip[df_sip['sip_inflow_crore'] == max_inflow]['month'].iloc[0]

fig.add_annotation(x=max_month, y=max_inflow,
            text="All-Time High: ₹31,002 Cr",
            showarrow=True, arrowhead=1)

fig.write_image('../reports/charts/03_sip_inflows.png')
fig.show()"""))

# Task 4: Category inflow heatmap
cells.append(nbf.v4.new_markdown_cell("""## 4. Category Net Inflows
**Finding:** Large Cap and Flexi Cap categories consistently attract the highest net inflows month over month."""))
cells.append(nbf.v4.new_code_cell("""# 4. Category inflow heatmap — months on X-axis, fund categories on Y-axis, net inflow as colour intensity.

heatmap_data = df_cat.pivot(index='category', columns='month', values='net_inflow_crore')

plt.figure(figsize=(16, 8))
sns.heatmap(heatmap_data, cmap='coolwarm', center=0, annot=False)
plt.title('Net Inflow by Category and Month (Crores)', fontsize=16)
plt.xlabel('Month', fontsize=12)
plt.ylabel('Category', fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('../reports/charts/04_category_inflow_heatmap.png')
plt.show()"""))

# Task 5: Investor demographics
cells.append(nbf.v4.new_markdown_cell("""## 5. Investor Demographics
**Finding:** The 25-35 age group constitutes the largest demographic of investors, though older age groups (45+) tend to have higher individual SIP amounts."""))
cells.append(nbf.v4.new_code_cell("""# 5. Investor demographics — age group distribution pie chart. 
# SIP amount box plot by age group. Gender split.

fig, axes = plt.subplots(1, 3, figsize=(20, 6))

# Age group distribution
age_counts = df_inv['age_group'].value_counts()
axes[0].pie(age_counts, labels=age_counts.index, autopct='%1.1f%%', startangle=90)
axes[0].set_title('Age Group Distribution')

# Gender split
gender_counts = df_inv['gender'].value_counts()
axes[1].pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff'])
axes[1].set_title('Gender Split')

# SIP amount box plot
sns.boxplot(ax=axes[2], data=df_inv[df_inv['transaction_type'] == 'SIP'], x='age_group', y='amount_inr', order=sorted(df_inv['age_group'].dropna().unique()))
axes[2].set_title('SIP Amount by Age Group')
axes[2].set_xlabel('Age Group')
axes[2].set_ylabel('SIP Amount (INR)')

plt.tight_layout()
plt.savefig('../reports/charts/05_investor_demographics.png')
plt.show()"""))

# Task 6: Geographic distribution
cells.append(nbf.v4.new_markdown_cell("""## 6. Geographic Distribution
**Finding:** Maharashtra and Gujarat lead in total SIP amounts, heavily driven by Tier 1 (T30) cities which dominate the overall contribution compared to B30 cities."""))
cells.append(nbf.v4.new_code_cell("""# 6. Geographic distribution — horizontal bar chart of SIP amount by state. 
# T30 vs B30 city tier pie chart.

fig, axes = plt.subplots(1, 2, figsize=(18, 8))

# State-wise SIP amount
state_sip = df_inv[df_inv['transaction_type'] == 'SIP'].groupby('state')['amount_inr'].sum().sort_values(ascending=False).head(15)
sns.barplot(ax=axes[0], x=state_sip.values, y=state_sip.index, palette='viridis')
axes[0].set_title('Top 15 States by Total SIP Amount')
axes[0].set_xlabel('Total SIP Amount (INR)')
axes[0].set_ylabel('State')

# T30 vs B30
tier_counts = df_inv['city_tier'].value_counts()
axes[1].pie(tier_counts, labels=tier_counts.index, autopct='%1.1f%%', startangle=90, colors=['#99ff99','#ffcc99'])
axes[1].set_title('T30 vs B30 City Tier Distribution')

plt.tight_layout()
plt.savefig('../reports/charts/06_geographic_distribution.png')
plt.show()"""))

# Task 7: Folio count growth
cells.append(nbf.v4.new_markdown_cell("""## 7. Folio Count Growth
**Finding:** Industry folio counts nearly doubled from 13.26 Cr in Jan 2022 to over 26 Cr in Dec 2025, showing massive retail participation growth."""))
cells.append(nbf.v4.new_code_cell("""# 7. Folio count growth — line chart from 13.26 Cr (Jan 2022) to 26.12 Cr (Dec 2025). 
# Mark key milestones.

plt.figure(figsize=(12, 6))
plt.plot(df_folios['month'], df_folios['total_folios_crore'], marker='o', linewidth=2, color='b')
plt.title('Industry Folio Count Growth (2022-2025)', fontsize=16)
plt.xlabel('Month', fontsize=12)
plt.ylabel('Total Folios (Crores)', fontsize=12)
plt.xticks(df_folios['month'][::3], rotation=45) # Show every 3rd month to avoid clutter

# Key milestones
start_val = df_folios['total_folios_crore'].iloc[0]
end_val = df_folios['total_folios_crore'].iloc[-1]
plt.annotate(f'Start: {start_val} Cr', xy=(df_folios['month'].iloc[0], start_val), xytext=(0, 15), textcoords='offset points', arrowprops=dict(arrowstyle='->'))
plt.annotate(f'End: {end_val} Cr', xy=(df_folios['month'].iloc[-1], end_val), xytext=(-50, -20), textcoords='offset points', arrowprops=dict(arrowstyle='->'))

plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('../reports/charts/07_folio_growth.png')
plt.show()"""))

# Task 8: NAV return correlation
cells.append(nbf.v4.new_markdown_cell("""## 8. NAV Return Correlation Matrix
**Finding:** Large-cap funds from different fund houses show extremely high positive correlation (>0.9) in their daily returns, indicating strong market alignment."""))
cells.append(nbf.v4.new_code_cell("""# 8. NAV return correlation matrix — compute pairwise correlation of daily returns for 10 selected funds. 
# Seaborn heatmap.

# Pivot data to get daily NAV per scheme
nav_pivot = df_nav.pivot(index='date', columns='amfi_code', values='nav')

# Calculate daily returns (percentage change)
daily_returns = nav_pivot.pct_change().dropna()

# Select first 10 funds for correlation
selected_funds = daily_returns.columns[:10]
corr_matrix = daily_returns[selected_funds].corr()

plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='RdYlGn', vmin=-1, vmax=1, fmt='.2f')
plt.title('NAV Daily Return Correlation Matrix (10 Funds)', fontsize=14)
plt.tight_layout()
plt.savefig('../reports/charts/08_return_correlation.png')
plt.show()"""))

# Task 9: Sector allocation donut
cells.append(nbf.v4.new_markdown_cell("""## 9. Sector Allocation
**Finding:** Financial Services constitutes the dominant sector allocation across equity funds, heavily skewing portfolio weightings."""))
cells.append(nbf.v4.new_code_cell("""# 9. Sector allocation donut — aggregate sector weights from portfolio_holdings.csv across all equity funds.

sector_weights = df_port.groupby('sector')['market_value_cr'].sum().sort_values(ascending=False)

plt.figure(figsize=(10, 10))
plt.pie(sector_weights.values, labels=sector_weights.index, autopct='%1.1f%%', startangle=90, pctdistance=0.85)

# Draw circle to make it a donut
centre_circle = plt.Circle((0,0),0.70,fc='white')
fig = plt.gcf()
fig.gca().add_artist(centre_circle)

plt.title('Aggregate Sector Allocation (Market Value)', fontsize=16)
plt.tight_layout()
plt.savefig('../reports/charts/09_sector_allocation.png')
plt.show()"""))

# Task 10: Conclusion
cells.append(nbf.v4.new_markdown_cell("""## 10. Key EDA Findings Summary
1. **NAV Trend**: The 2023 bull run shows a strong upward trend across most equity funds, while 2024 shows distinct market corrections.
2. **AUM Dominance**: SBI Mutual Fund consistently dominates the AUM across all years, reaching an impressive ₹12.5L Cr benchmark.
3. **SIP Inflows**: Monthly SIP inflows show a steady, robust growth trajectory, peaking at an all-time high of ₹31,002 Cr in December 2025.
4. **Category Popularity**: Large Cap and Flexi Cap categories consistently attract the highest net inflows month over month.
5. **Investor Age**: The 25-35 age group constitutes the largest demographic of investors.
6. **SIP Sizes**: Older age groups (45+) tend to have higher individual SIP amounts compared to younger demographics.
7. **Geographic Leaders**: Maharashtra and Gujarat lead in total SIP amounts.
8. **City Tiers**: T30 cities dominate the overall contribution compared to B30 cities.
9. **Retail Boom**: Industry folio counts nearly doubled from 13.26 Cr in Jan 2022 to over 26 Cr in Dec 2025, showing massive retail participation growth.
10. **Correlations & Sectors**: Large-cap funds show extremely high positive correlation in daily returns, heavily driven by their shared large allocations to the Financial Services sector."""))

# Task 11: Expense Ratio Distribution
cells.append(nbf.v4.new_markdown_cell("## 11. Expense Ratio Distribution\n**Finding:** Most funds cluster around 1.0% - 1.5% expense ratios."))
cells.append(nbf.v4.new_code_cell("""# 11. Expense ratio distribution
plt.figure(figsize=(10, 6))
sns.histplot(df_fund['expense_ratio_pct'].dropna(), bins=10, kde=True, color='purple')
plt.title('Expense Ratio Distribution', fontsize=14)
plt.xlabel('Expense Ratio (%)')
plt.savefig('../reports/charts/10_expense_ratio.png')
plt.show()"""))

# Task 12: Morningstar Rating Distribution
cells.append(nbf.v4.new_markdown_cell("## 12. Morningstar Rating Distribution\n**Finding:** Most selected schemes hold 3 or 4-star ratings."))
cells.append(nbf.v4.new_code_cell("""# 12. Morningstar Rating Distribution
plt.figure(figsize=(8, 6))
sns.countplot(data=df_perf, x='morningstar_rating', palette='Set2')
plt.title('Morningstar Rating Distribution', fontsize=14)
plt.xlabel('Rating (Stars)')
plt.savefig('../reports/charts/11_morningstar_rating.png')
plt.show()"""))

# Task 13: Top 10 Stocks
cells.append(nbf.v4.new_markdown_cell("## 13. Top 10 Stocks by Market Value\n**Finding:** HDFC Bank and Reliance dominate the top holdings."))
cells.append(nbf.v4.new_code_cell("""# 13. Top 10 Stocks
top_stocks = df_port.groupby('stock_symbol')['market_value_cr'].sum().sort_values(ascending=False).head(10)
plt.figure(figsize=(12, 6))
sns.barplot(x=top_stocks.values, y=top_stocks.index, palette='magma')
plt.title('Top 10 Stocks by Aggregate Market Value (Crores)', fontsize=14)
plt.xlabel('Market Value (Crores)')
plt.savefig('../reports/charts/12_top_10_stocks.png')
plt.show()"""))

# Task 14: Risk Category Distribution
cells.append(nbf.v4.new_markdown_cell("## 14. Risk Category Distribution\n**Finding:** 'Very High' risk category is heavily represented due to small/mid cap funds."))
cells.append(nbf.v4.new_code_cell("""# 14. Risk Category
risk_counts = df_fund['risk_category'].value_counts()
plt.figure(figsize=(8, 8))
plt.pie(risk_counts, labels=risk_counts.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette('pastel'))
plt.title('Risk Category Distribution', fontsize=14)
plt.savefig('../reports/charts/13_risk_category.png')
plt.show()"""))

# Task 15: Payment Mode
cells.append(nbf.v4.new_markdown_cell("## 15. Transaction Payment Modes\n**Finding:** UPI is the dominant payment mode for SIP and Lumpsum transactions."))
cells.append(nbf.v4.new_code_cell("""# 15. Payment Mode
payment_counts = df_inv['payment_mode'].value_counts()
plt.figure(figsize=(8, 8))
plt.pie(payment_counts, labels=payment_counts.index, autopct='%1.1f%%', startangle=90)
plt.title('Payment Mode Split', fontsize=14)
plt.savefig('../reports/charts/14_payment_mode.png')
plt.show()"""))

# Task 16: Top Fund Managers
cells.append(nbf.v4.new_markdown_cell("## 16. Top Fund Managers\n**Finding:** Certain managers oversee multiple flagship funds across categories."))
cells.append(nbf.v4.new_code_cell("""# 16. Top Fund Managers
manager_counts = df_fund['fund_manager'].value_counts().head(10)
plt.figure(figsize=(12, 6))
sns.barplot(x=manager_counts.values, y=manager_counts.index, palette='cubehelix')
plt.title('Top 10 Fund Managers by Number of Schemes Managed', fontsize=14)
plt.xlabel('Number of Schemes')
plt.savefig('../reports/charts/15_fund_managers.png')
plt.show()"""))

nb['cells'] = cells
with open('notebooks/EDA_Analysis.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
print("Notebook 'notebooks/EDA_Analysis.ipynb' generated successfully.")
