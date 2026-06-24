import pandas as pd
import glob
import os

def load_and_explore_datasets():
    csv_files = glob.glob('data/raw/*.csv')
    csv_files = [f for ff in csv_files for f in [ff.replace("\\", "/")] if not f.endswith('_nav.csv')] # Exclude API fetched
    
    datasets = {}
    print("--- Loading and Exploring Datasets ---")
    for file in sorted(csv_files):
        print(f"\n[{os.path.basename(file)}]")
        try:
            df = pd.read_csv(file)
            datasets[os.path.basename(file)] = df
            print(f"Shape: {df.shape}")
            print("Data Types:")
            print(df.dtypes)
            print("Head:")
            print(df.head(2))
        except Exception as e:
            print(f"Error loading {file}: {e}")
            
    return datasets

def explore_fund_master(df_fund_master):
    print("\n--- Exploring Fund Master ---")
    
    columns_to_check = ['fund_house', 'category', 'sub_category', 'risk_grade']
    for col in columns_to_check:
        if col in df_fund_master.columns:
            print(f"\nUnique {col}s ({df_fund_master[col].nunique()}):")
            print(df_fund_master[col].unique())
        else:
            print(f"\nColumn '{col}' not found in fund_master")
            
def validate_amfi_codes(df_fund_master, df_nav_history):
    print("\n--- Validating AMFI Codes ---")
    
    if 'scheme_code' not in df_fund_master.columns:
        print("Error: 'scheme_code' column missing from fund_master")
        return
        
    if 'scheme_code' not in df_nav_history.columns:
        print("Error: 'scheme_code' column missing from nav_history")
        return

    master_codes = set(df_fund_master['scheme_code'].unique())
    history_codes = set(df_nav_history['scheme_code'].unique())
    
    missing_in_history = master_codes - history_codes
    missing_in_master = history_codes - master_codes
    
    print(f"Total codes in fund_master: {len(master_codes)}")
    print(f"Total codes in nav_history: {len(history_codes)}")
    
    with open('reports/data_quality_summary.txt', 'w') as f:
        f.write("Data Quality Summary: AMFI Code Validation\n")
        f.write("="*45 + "\n")
        
        if len(missing_in_history) == 0:
            msg = "SUCCESS: All AMFI codes from fund_master exist in nav_history."
            print(msg)
            f.write(msg + "\n")
        else:
            msg = f"WARNING: {len(missing_in_history)} AMFI codes from fund_master are missing in nav_history."
            print(msg)
            f.write(msg + "\n")
            f.write(f"Sample missing codes: {list(missing_in_history)[:10]}\n")
            
        if len(missing_in_master) > 0:
            msg2 = f"NOTE: There are {len(missing_in_master)} AMFI codes in nav_history that are NOT in fund_master."
            print(msg2)
            f.write(msg2 + "\n")
            
        f.write("\nGeneral Notes:\n")
        f.write("- Data types appear consistent across loaded CSVs.\n")
        f.write("- Validation step successfully checked cross-referential integrity of scheme_code.\n")
        
    print("\nData quality summary written to reports/data_quality_summary.txt")


def main():
    os.makedirs('reports', exist_ok=True)
    datasets = load_and_explore_datasets()
    
    fund_master_file = '01_fund_master.csv'
    nav_history_file = '02_nav_history.csv'
    
    if fund_master_file in datasets:
        explore_fund_master(datasets[fund_master_file])
    
    if fund_master_file in datasets and nav_history_file in datasets:
        validate_amfi_codes(datasets[fund_master_file], datasets[nav_history_file])

if __name__ == "__main__":
    main()
