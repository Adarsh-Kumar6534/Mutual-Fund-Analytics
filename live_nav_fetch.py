import requests
import pandas as pd
import os

def fetch_and_save_nav(scheme_code, name):
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    print(f"Fetching {name} ({scheme_code})...")
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'data' in data:
            df = pd.DataFrame(data['data'])
            # Add scheme metadata
            df['scheme_code'] = scheme_code
            df['scheme_name'] = name
            
            output_file = f"data/raw/{scheme_code}_{name.replace(' ', '_')}_nav.csv"
            df.to_csv(output_file, index=False)
            print(f"Saved {len(df)} records to {output_file}")
        else:
            print(f"No data found for {scheme_code}")
    else:
        print(f"Failed to fetch data for {scheme_code}, status code: {response.status_code}")

def main():
    schemes_to_fetch = [
        (125497, "HDFC Top 100 Direct"),
        (119551, "SBI Bluechip"),
        (120503, "ICICI Bluechip"),
        (118632, "Nippon Large Cap"),
        (119092, "Axis Bluechip"),
        (120841, "Kotak Bluechip")
    ]
    
    # Ensure raw data directory exists
    os.makedirs("data/raw", exist_ok=True)
    
    for scheme_code, name in schemes_to_fetch:
        fetch_and_save_nav(scheme_code, name)

if __name__ == "__main__":
    main()
