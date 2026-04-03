import os
import smtplib
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
import yagmail
from fpdf import FPDF


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
DATA_DIR = BASE_DIR / "data"


class InvoicePDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def format_naira(amount) -> str:
    return f"NGN {float(amount):,.0f}"


def create_pdf() -> InvoicePDF:
    pdf = InvoicePDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    return pdf


def safe_cell(pdf: FPDF, w: float, h: float, text: str = "", **kwargs):
    clean_text = str(text).replace("₦", "NGN ")
    pdf.cell(w, h, clean_text, **kwargs)


st.set_page_config(page_title="Automation Hub", layout="wide", page_icon="📧")

st.title("📧 Automated Report & Invoice Generator")
st.markdown("**Portfolio Project 6** — Generate invoices, reports, and send them automatically via email.")

tab1, tab2 = st.tabs(["🧾 Invoice Generator", "📊 Report Sender"])


if "report_path" not in st.session_state:
    st.session_state.report_path = None


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
        use_container_width=True,
    )

    if st.button("Generate Invoice PDF"):
        try:
            items = items.copy()
            items["Quantity"] = pd.to_numeric(items["Quantity"], errors="coerce").fillna(0)
            items["Price"] = pd.to_numeric(items["Price"], errors="coerce").fillna(0)
            items["Line Total"] = items["Quantity"] * items["Price"]
            total = items["Line Total"].sum()

            pdf = create_pdf()
            pdf.set_font("Helvetica", "B", 16)
            safe_cell(pdf, 0, 10, "INVOICE", new_x="LMARGIN", new_y="NEXT", align="C")

            pdf.set_font("Helvetica", "", 12)
            safe_cell(
                pdf,
                0,
                10,
                f"Invoice #: {invoice_number} | Date: {datetime.now().strftime('%Y-%m-%d')}",
                new_x="LMARGIN",
                new_y="NEXT",
                align="C",
            )
            pdf.ln(10)

            safe_cell(pdf, 0, 10, f"Bill To: {client_name}", new_x="LMARGIN", new_y="NEXT")
            safe_cell(pdf, 0, 10, f"From: {your_name}", new_x="LMARGIN", new_y="NEXT")
            safe_cell(pdf, 0, 10, f"Due Date: {due_date}", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(10)

            pdf.set_font("Helvetica", "B", 12)
            safe_cell(pdf, 80, 10, "Item", border=1)
            safe_cell(pdf, 30, 10, "Qty", border=1)
            safe_cell(pdf, 40, 10, "Price (NGN)", border=1)
            safe_cell(pdf, 40, 10, "Total (NGN)", border=1, new_x="LMARGIN", new_y="NEXT")

            pdf.set_font("Helvetica", "", 10)
            for _, row in items.iterrows():
                safe_cell(pdf, 80, 10, row["Item"], border=1)
                safe_cell(pdf, 30, 10, f"{int(row['Quantity'])}", border=1)
                safe_cell(pdf, 40, 10, f"{row['Price']:,.0f}", border=1)
                safe_cell(pdf, 40, 10, f"{row['Line Total']:,.0f}", border=1, new_x="LMARGIN", new_y="NEXT")

            pdf.ln(5)
            pdf.set_font("Helvetica", "B", 12)
            safe_cell(
                pdf,
                0,
                10,
                f"Grand Total: {format_naira(total)}",
                new_x="LMARGIN",
                new_y="NEXT",
                align="R",
            )

            OUTPUT_DIR.mkdir(exist_ok=True)
            invoice_path = OUTPUT_DIR / f"invoice_{invoice_number}.pdf"
            pdf.output(str(invoice_path))

            with open(invoice_path, "rb") as f:
                st.download_button(
                    "📥 Download Invoice PDF",
                    f,
                    file_name=invoice_path.name,
                    mime="application/pdf",
                )

            st.success(f"Invoice generated: {invoice_path}")

        except Exception as e:
            st.error(f"Invoice generation failed: {e}")


with tab2:
    st.subheader("Generate & Email Report")

    data_source = st.radio("Data Source", ["Use sample sales_data.csv", "Upload CSV/Excel"])

    if data_source == "Use sample sales_data.csv":
        sample_path = DATA_DIR / "sales_data.csv"
        if sample_path.exists():
            df = pd.read_csv(sample_path)
        else:
            st.warning(f"Sample file not found: {sample_path}")
            df = pd.DataFrame()
    else:
        uploaded = st.file_uploader("Upload file", type=["csv", "xlsx"])
        if uploaded:
            df = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
        else:
            df = pd.DataFrame()

    if not df.empty:
        st.dataframe(df, use_container_width=True)

        required_columns = {"Client", "Total"}
        if not required_columns.issubset(df.columns):
            st.error("Your data must contain 'Client' and 'Total' columns.")
        else:
            df = df.copy()
            df["Total"] = pd.to_numeric(df["Total"], errors="coerce").fillna(0)
            summary = df.groupby("Client", dropna=False)["Total"].sum().reset_index()
            total_revenue = df["Total"].sum()

            st.write(f"**Total Revenue: {format_naira(total_revenue)}**")

            st.subheader("Email Settings")
            recipient = st.text_input("Recipient Email", key="recipient_email")
            st.caption("Sender email and app password are loaded from Streamlit secrets.")

            # with st.expander("How to set Streamlit secrets"):
            #     st.code(
            #         'EMAIL_ADDRESS = "yourgmail@gmail.com"\n'
            #         'EMAIL_APP_PASSWORD = "your16characterapppassword"',
            #         language="toml",
            #     )

            if st.button("Generate Summary Report PDF"):
                try:
                    pdf = create_pdf()
                    pdf.set_font("Helvetica", "B", 16)
                    safe_cell(pdf, 0, 10, "Monthly Sales Report", new_x="LMARGIN", new_y="NEXT", align="C")

                    pdf.set_font("Helvetica", "", 12)
                    safe_cell(
                        pdf,
                        0,
                        10,
                        f"Generated: {datetime.now().strftime('%Y-%m-%d')}",
                        new_x="LMARGIN",
                        new_y="NEXT",
                        align="C",
                    )
                    pdf.ln(10)
                    safe_cell(
                        pdf,
                        0,
                        10,
                        f"Total Revenue: {format_naira(total_revenue)}",
                        new_x="LMARGIN",
                        new_y="NEXT",
                    )
                    pdf.ln(5)

                    for _, row in summary.iterrows():
                        safe_cell(
                            pdf,
                            0,
                            10,
                            f"{row['Client']}: {format_naira(row['Total'])}",
                            new_x="LMARGIN",
                            new_y="NEXT",
                        )

                    OUTPUT_DIR.mkdir(exist_ok=True)
                    report_path = OUTPUT_DIR / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    pdf.output(str(report_path))

                    st.session_state.report_path = str(report_path)
                    st.success("Report PDF generated successfully!")

                except Exception as e:
                    st.error(f"Report PDF generation failed: {e}")

            if st.session_state.report_path:
                st.info(f"Report ready: {st.session_state.report_path}")

                if st.button("Send Email with Attachment"):
                    try:
                        sender_email = st.secrets["EMAIL_ADDRESS"]
                        app_password = st.secrets["EMAIL_APP_PASSWORD"]

                        if not recipient:
                            st.error("Please enter a recipient email.")
                        elif not os.path.exists(st.session_state.report_path):
                            st.error("Attachment file was not found. Generate the report again.")
                        else:
                            with st.expander("Debug info"):
                                st.write("Sender:", sender_email)
                                st.write("Recipient:", recipient)
                                st.write("Attachment path:", st.session_state.report_path)
                                st.write("Attachment exists:", os.path.exists(st.session_state.report_path))

                            yag = yagmail.SMTP(user=sender_email, password=app_password)
                            subject = f"Sales Report - {datetime.now().strftime('%Y-%m-%d')}"
                            body = "Please find the attached automated report."

                            yag.send(
                                to=recipient,
                                subject=subject,
                                contents=body,
                                attachments=st.session_state.report_path,
                            )

                            st.success(f"✅ Email sent successfully to {recipient}")

                    except KeyError:
                        st.error("Missing EMAIL_ADDRESS or EMAIL_APP_PASSWORD in Streamlit secrets.")
                    except smtplib.SMTPAuthenticationError as e:
                        st.error(f"SMTP authentication failed: {e}")
                    except smtplib.SMTPException as e:
                        st.error(f"SMTP error: {e}")
                    except Exception as e:
                        st.error(f"Unexpected email error: {type(e).__name__}: {e}")

    else:
        st.info("Load data to generate report.")
        st.success("✅ Automation Hub ready! Extend with Google Sheets (gspread) or scheduling for production use.")
