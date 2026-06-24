# Bonus Challenge 1: ETL Scheduling Instructions

To fully satisfy the requirement to schedule the ETL pipeline to run every weekday at 8 PM, follow these steps using Windows Task Scheduler.

## Instructions
1. Open **Task Scheduler** from the Windows Start menu.
2. Click **Create Basic Task...** in the Actions pane.
3. **Name**: Enter `Bluestock_Daily_ETL` and click Next.
4. **Trigger**: Select `Weekly`.
5. **Schedule**: 
   - Set the start time to `20:00:00` (8:00 PM).
   - Check all weekdays: Monday, Tuesday, Wednesday, Thursday, Friday.
6. **Action**: Select `Start a program`.
7. **Program/script**: Browse and select `C:\bluestock works\scripts\schedule_etl.bat`.
8. **Finish**: Click Finish to save the task.

The script `schedule_etl.bat` will automatically activate the Python virtual environment and run the full `etl_pipeline.py` script, fetching new NAV data and updating the database every evening.
