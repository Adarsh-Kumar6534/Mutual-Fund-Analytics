import sys
import sqlite3
import pandas as pd

def main():
    if len(sys.argv) < 2:
        print("Usage: python recommender.py [Low/Moderate/High]")
        return
        
    risk_appetite = sys.argv[1].title()
    if risk_appetite not in ['Low', 'Moderate', 'High', 'Very High', 'Moderately High']:
        print("Invalid risk appetite. Please choose from: Low, Moderate, High, Very High, Moderately High.")
        return

    conn = sqlite3.connect('bluestock_mf.db')
    
    query = f"""
    SELECT 
        f.amfi_code,
        f.scheme_name,
        f.fund_house,
        f.category,
        p.sharpe_ratio,
        p.return_3yr_pct,
        p.risk_grade
    FROM dim_fund f
    JOIN fact_performance p ON f.amfi_code = p.amfi_code
    WHERE f.risk_category = '{risk_appetite}'
    ORDER BY p.sharpe_ratio DESC
    LIMIT 3
    """
    
    try:
        df = pd.read_sql(query, conn)
        print("="*80)
        print(f"  TOP 3 RECOMMENDED FUNDS FOR '{risk_appetite.upper()}' RISK APPETITE  ")
        print("="*80)
        if df.empty:
            print("No funds found matching this risk profile.")
        else:
            for i, row in df.iterrows():
                print(f"{i+1}. {row['scheme_name']}")
                print(f"   Fund House  : {row['fund_house']}")
                print(f"   Category    : {row['category']}")
                print(f"   Sharpe Ratio: {row['sharpe_ratio']:.2f}")
                print(f"   3Yr Return  : {row['return_3yr_pct']:.2f}%\n")
    finally:
        conn.close()

if __name__ == '__main__':
    main()
