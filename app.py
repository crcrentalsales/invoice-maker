import json
import os
from datetime import date
from io import BytesIO

import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


st.set_page_config(page_title="Invoice Maker", page_icon="🧾")

st.title("🧾 Multi-Business Invoice Maker")


def load_businesses():
    with open("businesses.json", "r") as file:
        return json.load(file)


def create_invoice_pdf(business_name, business, client_name, description, price):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    logo_path = business.get("logo", "")

    if logo_path and os.path.exists(logo_path):
        c.drawImage(
            logo_path,
            50,
            height - 130,
            width=100,
            height=80,
            preserveAspectRatio=True,
            mask="auto"
        )

    c.setFont("Helvetica-Bold", 20)
    c.drawString(180, height - 70, business_name)

    c.setFont("Helvetica", 10)
    c.drawString(180, height - 90, business["address"])
    c.drawString(180, height - 105, f"Phone: {business['phone']}")
    c.drawString(180, height - 120, f"Email: {business['email']}")

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 180, "INVOICE")

    c.setFont("Helvetica", 11)
    c.drawString(50, height - 210, f"Date: {date.today()}")
    c.drawString(50, height - 230, f"Bill To: {client_name}")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 280, "Description")
    c.drawString(450, height - 280, "Price")

    c.line(50, height - 290, 550, height - 290)

    c.setFont("Helvetica", 11)
    c.drawString(50, height - 320, description[:80])
    c.drawString(450, height - 320, f"${price:,.2f}")

    c.line(50, height - 350, 550, height - 350)

    c.setFont("Helvetica-Bold", 13)
    c.drawString(380, height - 390, "Total:")
    c.drawString(450, height - 390, f"${price:,.2f}")

    c.save()
    buffer.seek(0)
    return buffer


businesses = load_businesses()

business_name = st.selectbox("Choose your business", list(businesses.keys()))
business = businesses[business_name]

st.subheader("Business Details")
st.write(business["address"])
st.write(business["phone"])
st.write(business["email"])

client_name = st.text_input("Client Name")
description = st.text_area("What is this invoice for?")
price = st.number_input("Price", min_value=0.0, step=1.0)

if st.button("Create Invoice"):
    if not client_name or not description or price <= 0:
        st.error("Please fill in the client name, description, and price.")
    else:
        pdf = create_invoice_pdf(
            business_name,
            business,
            client_name,
            description,
            price
        )

        st.success("Invoice created!")

        st.download_button(
            label="Download Invoice PDF",
            data=pdf,
            file_name=f"invoice_{client_name.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
