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

## Live Demo
https://automated-report-sender-and-invoice-generator-9dze32wf2mpwhdre.streamlit.app/

## Screenshots
<img width="1920" height="1080" alt="Screenshot (106)" src="https://github.com/user-attachments/assets/a5a8d212-b441-47d9-a31d-4511cce346e7" />
<img width="1920" height="1080" alt="Screenshot (107)" src="https://github.com/user-attachments/assets/1209ae29-c663-492a-9941-59d1f3bbaf00" />

## Extensions
- Connect to Google Sheets with gspread for live data
- Add scheduling with `schedule` library (or contact me to do that for you)
- Deploy on Streamlit Cloud or Render for client access
