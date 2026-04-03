import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import yagmail
import os

st.set_page_config(page_title="Automation Hub", layout="wide", page_icon="📧")

st.title("📧 Automated Report & Invoice Generator")
st.markdown("**Portfolio Project 6** — Generate invoices, reports, and send them automatically via email.")

tab1, tab2 = st.tabs(["🧾 Invoice Generator", "📊 Report Sender"])

# INVOICE GENERATOR
with tab1:
    st.subheader("Create Professional Invoice")

    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("Client Name", "John Doe")
        invoice_number = st.text_input("Invoice Number", f"INV-{datetime.now().strftime('%Y%m%d')}")
    with col2:
        your_name = st.text_input("Your Company Name", "Your Freelance Services")
        due_date = st.date_input("Due Date", datetime.now().date())

    items = st.data_editor(
        pd.DataFrame([{"Item": "Python Automation Script", "Quantity": 1, "Price": 85000}]),
        num_rows="dynamic",
        use_container_width=True
    )

    if st.button("Generate Invoice PDF"):
        total = (items['Quantity'] * items['Price']).sum()

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "INVOICE", ln=True, align="C")
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Invoice #: {invoice_number} | Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True,
                 align="C")
        pdf.ln(10)

        pdf.cell(0, 10, f"Bill To: {client_name}", ln=True)
        pdf.cell(0, 10, f"From: {your_name}", ln=True)
        pdf.cell(0, 10, f"Due Date: {due_date}", ln=True)
        pdf.ln(10)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(80, 10, "Item", border=1)
        pdf.cell(30, 10, "Qty", border=1)
        pdf.cell(40, 10, "Price (₦)", border=1)
        pdf.cell(40, 10, "Total (₦)", border=1, ln=True)

        pdf.set_font("Arial", "", 10)
        for _, row in items.iterrows():
            pdf.cell(80, 10, str(row['Item']), border=1)
            pdf.cell(30, 10, str(row['Quantity']), border=1)
            pdf.cell(40, 10, f"{row['Price']:,.0f}", border=1)
            pdf.cell(40, 10, f"{row['Quantity'] * row['Price']:,.0f}", border=1, ln=True)

        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Grand Total: ₦{total:,.0f}", ln=True, align="R")

        os.makedirs("output", exist_ok=True)
        invoice_path = f"output/invoice_{invoice_number}.pdf"
        pdf.output(invoice_path)

        with open(invoice_path, "rb") as f:
            st.download_button("📥 Download Invoice PDF", f, invoice_path, "application/pdf")

        st.success(f"Invoice generated: {invoice_path}")

# REPORT SENDER
with tab2:
    st.subheader("Generate & Email Report")

    data_source = st.radio("Data Source", ["Use sample sales_data.csv", "Upload CSV/Excel"])

    if data_source == "Use sample sales_data.csv":
        df = pd.read_csv("data/sales_data.csv")
    else:
        uploaded = st.file_uploader("Upload file", type=["csv", "xlsx"])
        if uploaded:
            df = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
        else:
            df = pd.DataFrame()

    if not df.empty:
        st.dataframe(df, use_container_width=True)

        summary = df.groupby('Client')['Total'].sum().reset_index()
        total_revenue = df['Total'].sum()

        st.write(f"**Total Revenue: ₦{total_revenue:,.0f}**")

        # Generate summary PDF (simple version)
        if st.button("Generate Summary Report PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Monthly Sales Report", ln=True, align="C")
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d')}", ln=True, align="C")
            pdf.ln(10)
            pdf.cell(0, 10, f"Total Revenue: ₦{total_revenue:,.0f}", ln=True)
            pdf.ln(5)

            for _, row in summary.iterrows():
                pdf.cell(0, 10, f"{row['Client']}: ₦{row['Total']:,.0f}", ln=True)

            report_path = f"output/report_{datetime.now().strftime('%Y%m%d')}.pdf"
            os.makedirs("output", exist_ok=True)
            pdf.output(report_path)
            st.success("Report PDF generated!")

            # Email section
            st.subheader("Send via Email")
            sender_email = st.text_input("Your Gmail Address")
            app_password = st.text_input("Gmail App Password (not regular password)", type="password")
            recipient = st.text_input("Recipient Email")

            if st.button("Send Email with Attachment"):
                try:
                    yag = yagmail.SMTP(sender_email, app_password)
                    subject = f"Sales Report - {datetime.now().strftime('%Y-%m-%d')}"
                    body = "Please find the attached automated report."
                    yag.send(to=recipient, subject=subject, contents=body, attachments=report_path)
                    st.success(f"✅ Email sent successfully to {recipient}!")
                except Exception as e:
                    st.error(f"Email failed: {str(e)}. Make sure you use a Gmail App Password.")

    else:
        st.info("Load data to generate report.")
        st.success("✅ Automation Hub ready! Extend with Google Sheets (gspread) or scheduling for production use.")