import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import os

def generate_email():
    print("Generating Weekly Performance Email Report...")
    
    # Check if scorecard exists
    if not os.path.exists('../reports/fund_scorecard.csv'):
        print("Scorecard not found! Run the Performance Analytics notebook first.")
        return
        
    df = pd.read_csv('../reports/fund_scorecard.csv')
    top_10 = df.head(10).copy()
    
    # Format columns for display
    top_10['CAGR_3Yr'] = top_10['CAGR_3Yr'].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A")
    top_10['Sharpe_Ratio'] = top_10['Sharpe_Ratio'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "N/A")
    top_10['Scorecard'] = top_10['Scorecard'].apply(lambda x: f"{x:.1f}/100")
    
    html_table = top_10[['scheme_name', 'Scorecard', 'CAGR_3Yr', 'Sharpe_Ratio']].to_html(index=False, classes='styled-table')
    
    html_content = f"""
    <html>
    <head>
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #f4f7f6; color: #333; }}
        .container {{ width: 80%; margin: auto; padding: 20px; background-color: #fff; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
        h2 {{ color: #003366; }}
        .styled-table {{ border-collapse: collapse; margin: 25px 0; font-size: 0.9em; font-family: sans-serif; width: 100%; box-shadow: 0 0 20px rgba(0, 0, 0, 0.15); }}
        .styled-table thead tr {{ background-color: #00d2ff; color: #ffffff; text-align: left; }}
        .styled-table th, .styled-table td {{ padding: 12px 15px; }}
        .styled-table tbody tr {{ border-bottom: 1px solid #dddddd; }}
        .styled-table tbody tr:nth-of-type(even) {{ background-color: #f3f3f3; }}
        .styled-table tbody tr:last-of-type {{ border-bottom: 2px solid #00d2ff; }}
        .footer {{ margin-top: 20px; font-size: 12px; color: #777; text-align: center; }}
    </style>
    </head>
    <body>
        <div class="container">
            <h2>📈 Bluestock Weekly Mutual Fund Performance Report</h2>
            <p>Here are the Top 10 Elite Funds for the week ending {datetime.now().strftime('%Y-%m-%d')}:</p>
            {html_table}
            <p>Log in to your Bluestock interactive dashboard for full details!</p>
            <div class="footer">Automated Report Generation - Python Email Script</div>
        </div>
    </body>
    </html>
    """
    
    # Save the HTML for review instead of actually sending (since we don't have SMTP credentials)
    with open('../reports/Weekly_Email_Preview.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print("Email HTML template generated and saved to reports/Weekly_Email_Preview.html")
    
    # Note: To actually send, you would uncomment and configure the below:
    """
    msg = MIMEMultipart()
    msg['From'] = "admin@bluestock.in"
    msg['To'] = "investor@bluestock.in"
    msg['Subject'] = "Weekly Top 10 Mutual Funds"
    msg.attach(MIMEText(html_content, 'html'))
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("your_email", "your_password")
    server.send_message(msg)
    server.quit()
    """

if __name__ == "__main__":
    generate_email()
