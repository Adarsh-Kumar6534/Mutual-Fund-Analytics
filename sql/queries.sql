-- 1. Top 5 funds by AUM
SELECT scheme_name, fund_house, aum_crore
FROM fact_performance
ORDER BY aum_crore DESC
LIMIT 5;

-- 2. Average NAV per month for a specific fund (e.g. AMFI 119551 - SBI)
SELECT 
    d.year, 
    d.month, 
    AVG(n.nav) as avg_nav
FROM fact_nav n
JOIN dim_date d ON n.date = d.date
WHERE n.amfi_code = 119551
GROUP BY d.year, d.month
ORDER BY d.year, d.month;

-- 3. Total SIP inflows by Year (proxy for YoY growth)
SELECT 
    d.year, 
    SUM(t.amount_inr) as total_sip_inflow
FROM fact_transactions t
JOIN dim_date d ON t.transaction_date = d.date
WHERE t.transaction_type = 'Sip'
GROUP BY d.year
ORDER BY d.year;

-- 4. Total transaction amount by State
SELECT 
    state, 
    SUM(amount_inr) as total_amount
FROM fact_transactions
GROUP BY state
ORDER BY total_amount DESC;

-- 5. Funds with expense ratio < 1%
SELECT 
    amfi_code, 
    scheme_name, 
    expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;

-- 6. Total SIP amount grouped by Age Group
SELECT 
    age_group, 
    SUM(amount_inr) as total_sip_amount
FROM fact_transactions
WHERE transaction_type = 'Sip'
GROUP BY age_group
ORDER BY total_sip_amount DESC;

-- 7. Top 5 fund houses by total number of schemes (from latest AUM record)
SELECT 
    fund_house, 
    MAX(num_schemes) as max_schemes
FROM fact_aum
GROUP BY fund_house
ORDER BY max_schemes DESC
LIMIT 5;

-- 8. Funds with 5-year return > 15% and Morningstar rating >= 4
SELECT 
    scheme_name, 
    return_5yr_pct, 
    morningstar_rating
FROM fact_performance
WHERE return_5yr_pct > 15.0 AND morningstar_rating >= 4
ORDER BY return_5yr_pct DESC;

-- 9. Total transaction count by gender for Lumpsum
SELECT 
    gender, 
    COUNT(transaction_id) as txn_count
FROM fact_transactions
WHERE transaction_type = 'Lumpsum'
GROUP BY gender;

-- 10. Daily NAV growth for a specific scheme (e.g. 119551)
SELECT 
    date, 
    nav,
    LAG(nav) OVER(ORDER BY date) as prev_nav,
    ((nav - LAG(nav) OVER(ORDER BY date)) / LAG(nav) OVER(ORDER BY date)) * 100 as daily_growth_pct
FROM fact_nav
WHERE amfi_code = 119551
ORDER BY date
LIMIT 20;
