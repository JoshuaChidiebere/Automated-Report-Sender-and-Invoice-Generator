# Automated Report Sender & Invoice Generator

**Portfolio Project 6** — Full automation suite: Generate professional PDF invoices and send scheduled reports via email.

## Features
- Dynamic PDF Invoice creation with itemized billing
- Sales/report summarization with pandas
- One-click PDF report generation
- Email sending with attachments (yagmail)
- Streamlit interface for easy client demo

## Technologies
Python • pandas • fpdf2 • yagmail • Streamlit

## How to Run
1. `pip install -r requirements.txt`
2. `streamlit run app.py`
3. For email: Use Gmail + App Password (not your regular password)

## Screenshots
(Add screenshots of generated invoice PDF, report tab, and successful email confirmation)

## Extensions
- Connect to Google Sheets with gspread for live data
- Add scheduling with `schedule` library
- Deploy on Streamlit Cloud or Render for client access