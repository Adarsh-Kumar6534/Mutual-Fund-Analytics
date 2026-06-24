import os
from pptx import Presentation
from pptx.util import Inches, Pt
from fpdf import FPDF
import datetime

def create_pptx():
    print("Generating Final_Presentation.pptx...")
    prs = Presentation()
    
    # Title Slide
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    title.text = "Mutual Fund Analytics Capstone"
    subtitle.text = "Data Engineering & Quantitative Analysis\nPrepared by Bluestock AI"
    
    # Exec Summary Slide
    bullet_slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes
    title_shape = shapes.title
    body_shape = shapes.placeholders[1]
    title_shape.text = "Executive Summary"
    tf = body_shape.text_frame
    tf.text = "End-to-End Analytics Architecture"
    p = tf.add_paragraph()
    p.text = "ETL Pipeline: Scraped, cleaned, and warehoused 1M+ rows of NAV and transaction data into a SQLite Star Schema."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "Quantitative Engine: Computed CAGR, Sharpe, Alpha, Beta, VaR, and executed Monte Carlo simulations."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "Dashboarding: Built a live, interactive Streamlit Glassmorphism application."
    p.level = 1
    
    # Chart Slide (Industry Overview)
    img_path = 'reports/charts/01_Dashboard_Industry_Overview.png'
    if os.path.exists(img_path):
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        slide.shapes.title.text = "Industry Overview Dashboard"
        # center image
        slide.shapes.add_picture(img_path, Inches(0.5), Inches(1.5), width=Inches(9))
        
    prs.save('reports/Final_Presentation.pptx')
    print("Successfully saved Final_Presentation.pptx")

def create_pdf():
    print("Generating Final_Report.pdf...")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Bluestock Mutual Fund Analytics", ln=True, align='C')
    
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, txt=f"Date: {datetime.date.today().strftime('%B %d, %Y')}", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="1. Project Scope & Architecture", ln=True)
    pdf.set_font("Arial", '', 11)
    arch_text = (
        "The mutual fund analytics engine was designed using a robust ETL pipeline. "
        "Data was ingested from raw CSVs, rigorously cleaned (forward-filling NAV holidays, "
        "validating numeric constraints), and loaded into a 6-table SQLite Star Schema. "
        "The dimensional model separates fact tables (NAV, transactions, AUM, performance) "
        "from dimensions (fund, date) to optimize query performance."
    )
    pdf.multi_cell(0, 7, txt=arch_text)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="2. Quantitative Metrics & Optimization", ln=True)
    pdf.set_font("Arial", '', 11)
    quant_text = (
        "Advanced financial models were deployed to assess fund viability. We computed "
        "annualized risk-adjusted returns using the Sharpe and Sortino ratios, derived Alpha/Beta "
        "via OLS regression against the Nifty 50, and measured downside risk using 95% Historical VaR.\n"
        "Furthermore, we executed 1,000-scenario Monte Carlo simulations using Geometric Brownian Motion "
        "to project 5-year NAV growth, and solved for the Markowitz Efficient Frontier to find the "
        "optimal maximum Sharpe ratio weights for our top 5 funds."
    )
    pdf.multi_cell(0, 7, txt=quant_text)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="3. Deliverables Status", ln=True)
    pdf.set_font("Arial", '', 11)
    deliv_text = (
        "- D1 ETL Pipeline: Completed (etl_pipeline.py)\n"
        "- D2 SQLite Database: Completed (bluestock_mf.db, strictly .gitignored)\n"
        "- D3 EDA Notebook: Completed\n"
        "- D4 Performance Metrics: Completed\n"
        "- D5 Interactive Dashboard: Completed (Streamlit Web App)\n"
        "- D6 Advanced Analytics: Completed\n"
        "- D7 Presentations: Completed (This Report & PPTX)\n"
        "- Bonus 1: Cron Job Batch Script (schedule_etl.bat)\n"
        "- Bonus 2: Streamlit Dashboard Overhaul\n"
        "- Bonus 3: Monte Carlo Simulation (Notebook generated)\n"
        "- Bonus 4: Markowitz Portfolio Optimization (Notebook generated)\n"
        "- Bonus 5: Automated HTML Email Report Script"
    )
    pdf.multi_cell(0, 7, txt=deliv_text)
    
    pdf.output("reports/Final_Report.pdf")
    print("Successfully saved Final_Report.pdf")

if __name__ == "__main__":
    create_pptx()
    create_pdf()
