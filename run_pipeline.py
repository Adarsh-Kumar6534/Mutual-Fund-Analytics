"""
Master execution script for the Bluestock Mutual Fund Analytics ETL Pipeline.
This script utilizes pathlib to dynamically locate and execute the ingestion,
cleaning, and database loading modules in sequence.
"""

import subprocess
from pathlib import Path
import sys

def run_pipeline():
    """
    Executes the full ETL pipeline by sequentially calling:
    1. data_ingestion.py
    2. data_cleaning.py
    3. db_loader.py
    
    If any script fails, the pipeline halts and returns the exit code.
    """
    print("🚀 Starting ETL Pipeline...")
    base_dir = Path(__file__).resolve().parent
    
    scripts = [
        "data_ingestion.py",
        "data_cleaning.py",
        "db_loader.py"
    ]
    
    for script in scripts:
        script_path = base_dir / script
        print(f"\n▶ Running {script}...")
        try:
            subprocess.run([sys.executable, str(script_path)], check=True)
            print(f"✅ {script} completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Pipeline failed at {script}. Exit code: {e.returncode}")
            sys.exit(1)
            
    print("\n🎉 ETL Pipeline executed successfully! All data loaded into bluestock_mf.db.")

if __name__ == "__main__":
    run_pipeline()
