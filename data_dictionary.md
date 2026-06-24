# Mutual Fund Analytics - Data Dictionary

This document outlines the Star Schema design used in the `bluestock_mf.db` SQLite database.

## Dimension Tables

### `dim_fund`
Primary dimension storing core details about each mutual fund scheme.
- **amfi_code** (INTEGER, Primary Key): Unique identifier for the fund.
- **fund_house** (TEXT): Name of the AMC (e.g., SBI Mutual Fund).
- **scheme_name** (TEXT): Full name of the mutual fund scheme.
- **category** (TEXT): Broad asset class (Equity, Debt, Hybrid).
- **sub_category** (TEXT): Specific category (Large Cap, Mid Cap, etc.).
- **plan** (TEXT): Direct or Regular plan.
- **launch_date** (TEXT): Inception date of the scheme.
- **benchmark** (TEXT): Benchmark index the scheme is tracked against.
- **expense_ratio_pct** (REAL): Annual expense ratio percentage.
- **exit_load_pct** (REAL): Penalty for early redemption.
- **min_sip_amount** (INTEGER): Minimum required amount for SIP.
- **min_lumpsum_amount** (INTEGER): Minimum required amount for Lumpsum.
- **fund_manager** (TEXT): Name of the primary fund manager.
- **risk_category** (TEXT): Risk grading (Low to Very High).
- **sebi_category_code** (TEXT): Regulatory SEBI classification code.

### `dim_date`
Calendar dimension generated to enable robust time-series analysis.
- **date** (TEXT, Primary Key): YYYY-MM-DD format.
- **year** (INTEGER): Year extracted from date.
- **month** (INTEGER): Month extracted from date.
- **day** (INTEGER): Day extracted from date.
- **quarter** (INTEGER): Quarter (1-4) extracted from date.
- **day_of_week** (INTEGER): Day of the week (0 = Monday, 6 = Sunday).
- **is_weekend** (INTEGER): Boolean flag (1 = Weekend, 0 = Weekday).

## Fact Tables

### `fact_nav`
Daily Net Asset Value records per scheme.
- **amfi_code** (INTEGER, Foreign Key to `dim_fund`): Identifier of the fund.
- **date** (TEXT, Foreign Key to `dim_date`): Date of the NAV record.
- **nav** (REAL): Net Asset Value for that day.
*(Composite Primary Key on `amfi_code` and `date`)*

### `fact_transactions`
Individual investor transactions tracking inflows/outflows.
- **transaction_id** (INTEGER, Primary Key): Autoincrement unique ID.
- **investor_id** (TEXT): Anonymized identifier for the investor.
- **transaction_date** (TEXT, Foreign Key to `dim_date`): Date of transaction.
- **amfi_code** (INTEGER, Foreign Key to `dim_fund`): Scheme involved.
- **transaction_type** (TEXT): Type of transaction (Sip, Lumpsum, Redemption).
- **amount_inr** (REAL): Transaction amount in INR.
- **state** (TEXT): Investor's state.
- **city** (TEXT): Investor's city.
- **city_tier** (TEXT): Tier classification of the city (T30, B30).
- **age_group** (TEXT): Demographic bracket of the investor.
- **gender** (TEXT): Investor gender.
- **annual_income_lakh** (REAL): Investor's annual income bracket.
- **payment_mode** (TEXT): Mode of payment (UPI, NetBanking, etc.).
- **kyc_status** (TEXT): KYC verification status (Verified, Pending, Rejected).

### `fact_performance`
Latest aggregated performance and risk metrics per scheme.
- **amfi_code** (INTEGER, Primary Key, Foreign Key to `dim_fund`): Fund identifier.
- **scheme_name, fund_house, category, plan** (TEXT): Denormalized labels for quick querying.
- **return_1yr_pct, return_3yr_pct, return_5yr_pct** (REAL): Historical returns.
- **benchmark_3yr_pct** (REAL): 3-year benchmark return.
- **alpha, beta, sharpe_ratio, sortino_ratio** (REAL): Risk-adjusted performance metrics.
- **std_dev_ann_pct, max_drawdown_pct** (REAL): Volatility metrics.
- **aum_crore** (INTEGER): Asset under management for the scheme.
- **expense_ratio_pct** (REAL): Expense ratio.
- **morningstar_rating** (INTEGER): Rating out of 5 stars.
- **risk_grade** (TEXT): Qualitative risk assessment.
- **anomaly_flag** (INTEGER): Boolean flag (1=Anomaly detected, 0=Normal).

### `fact_aum`
Monthly Asset Under Management aggregated by Fund House.
- **date** (TEXT, Foreign Key to `dim_date`): Month-end date.
- **fund_house** (TEXT): The AMC name.
- **aum_lakh_crore, aum_crore** (REAL/INTEGER): AUM size.
- **num_schemes** (INTEGER): Count of active schemes managed by the house.
*(Composite Primary Key on `date` and `fund_house`)*
