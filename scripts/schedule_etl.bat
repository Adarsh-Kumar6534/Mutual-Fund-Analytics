@echo off
echo Starting Scheduled Bluestock ETL Pipeline...
cd /d "C:\bluestock works"
call venv\Scripts\activate
python etl_pipeline.py
echo ETL completed successfully!
pause
