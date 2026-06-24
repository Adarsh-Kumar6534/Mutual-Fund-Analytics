from playwright.sync_api import sync_playwright
import time
from PIL import Image
import os

def run():
    print("Starting Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a large 1080p viewport so the dashboard is spacious
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        print("Navigating to Streamlit Dashboard...")
        page.goto("http://localhost:8501", wait_until="networkidle")
        time.sleep(10) # wait for all Plotly charts to render
        
        # 1. Industry Overview
        print("Capturing Page 1: Industry Overview...")
        page.screenshot(path="reports/charts/01_Dashboard_Industry_Overview.png", full_page=True)
        
        # 2. Fund Performance
        print("Navigating to Page 2...")
        # In Streamlit sidebar, radio buttons can be clicked by their label
        page.locator("text=Fund Performance").click()
        time.sleep(8)
        print("Capturing Page 2: Fund Performance...")
        page.screenshot(path="reports/charts/02_Dashboard_Fund_Performance.png", full_page=True)
        
        # 3. Investor Analytics
        print("Navigating to Page 3...")
        page.locator("text=Investor Analytics").click()
        time.sleep(8)
        print("Capturing Page 3: Investor Analytics...")
        page.screenshot(path="reports/charts/03_Dashboard_Investor_Analytics.png", full_page=True)
        
        # 4. SIP & Market Trends
        print("Navigating to Page 4...")
        page.locator("text=SIP & Market Trends").click()
        time.sleep(8)
        print("Capturing Page 4: SIP & Market Trends...")
        page.screenshot(path="reports/charts/04_Dashboard_SIP_Trends.png", full_page=True)
        
        browser.close()
        
    print("Combining PNGs into a single PDF report...")
    images = [
        Image.open("reports/charts/01_Dashboard_Industry_Overview.png").convert('RGB'),
        Image.open("reports/charts/02_Dashboard_Fund_Performance.png").convert('RGB'),
        Image.open("reports/charts/03_Dashboard_Investor_Analytics.png").convert('RGB'),
        Image.open("reports/charts/04_Dashboard_SIP_Trends.png").convert('RGB')
    ]
    images[0].save("reports/Dashboard.pdf", save_all=True, append_images=images[1:])
    print("Dashboard.pdf created successfully!")

if __name__ == "__main__":
    run()
