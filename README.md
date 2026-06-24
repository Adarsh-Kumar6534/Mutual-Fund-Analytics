# Bluestock Mutual Fund Analytics 🚀
*An End-to-End Data Engineering & Quantitative Analysis Capstone Project*

**Version:** 1.0  
**Author:** Bluestock AI

---

## 📌 Project Overview
The Indian Mutual Fund industry manages over ₹81 Lakh Crores. This project builds a robust, automated analytics pipeline to extract daily mutual fund NAV data, cleanse historical transaction records, and deploy advanced quantitative mathematical models (Sharpe, Alpha, Beta, Monte Carlo, Markowitz).

The findings are democratized through a highly interactive, aesthetic **Streamlit Glassmorphism Dashboard**.

---

## 📂 Repository Structure

```
├── .streamlit/                # Streamlit configuration (Dark Mode)
├── data/                      # Raw and Processed CSV data
├── notebooks/                 # Jupyter Notebooks for EDA and Quant Modeling
├── reports/                   # Exported PNG charts, CSV scorecards, HTML Emails
├── scripts/                   # Automation scripts (Cron jobs, PPTX generation)
├── sql/                       # Star Schema database models (SQLite)
├── dashboard.py               # Streamlit interactive web application
├── run_pipeline.py            # Master execution script for the ETL pipeline
├── README.md                  # This file
└── requirements.txt           # Python dependencies
```

*(Note: `bluestock_mf.db`, `Final_Presentation.pptx`, and `Final_Report.pdf` are intentionally excluded from GitHub tracking to maintain repository hygiene and adhere to strict commit requirements.)*

---

## 🛠️ Environment Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Adarsh-Kumar6534/Mutual-Fund-Analytics.git
   cd Mutual-Fund-Analytics
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```
3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 How to Run the Pipeline

### 1. Execute the ETL Pipeline
To extract fresh NAV data, clean it, and load it into the SQLite Data Warehouse (`bluestock_mf.db`), simply run the master pipeline script:
```bash
python run_pipeline.py
```
*This sequentially runs `data_ingestion.py`, `data_cleaning.py`, and `db_loader.py`.*

### 2. Launch the Interactive Dashboard
The fully functioning dashboard operates locally using Streamlit. To launch it:
```bash
streamlit run dashboard.py
```
Open your browser to `http://localhost:8501` to view the 4-page interactive visualization suite.

### 3. Generate Automated Reports
To re-generate the PowerPoint presentation or the PDF Report, navigate to the scripts folder:
```bash
python scripts/create_presentations.py
```

---

## 🏆 Bonus Challenges Mastered
This project successfully achieved 100% completion across all core deliverables and conquered all 5 Bonus Challenges:
1. **(B1) Cron Job Automation:** Added `scripts/schedule_etl.bat` for Windows Task Scheduler integration.
2. **(B2) Streamlit Alternative:** Deployed an advanced glassmorphic Streamlit web app in lieu of Power BI.
3. **(B3) Monte Carlo Simulation:** Implemented Geometric Brownian Motion to project 5-year NAV growth paths with uncertainty bands.
4. **(B4) Markowitz Portfolio Optimization:** Solved the Efficient Frontier to find maximum Sharpe Ratio weights.
5. **(B5) Automated HTML Email Reporting:** Created an automated script to distribute the weekly Top 10 fund scorecard.

---
*Developed for the Bluestock Mutual Fund Analytics Capstone Module.*
