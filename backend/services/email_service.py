import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import re
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def send_rfq_email(vendor_name: str, vendor_email: str, category: str, project_name: str, excel_content: bytes, custom_body: str = None, filename: str = None):
    """
    Sends an RFQ email to the vendor with the Excel attachment.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = vendor_email
        msg['Subject'] = f"Request for Quotation – {category} Materials"

        if custom_body:
            # Robust placeholder replacement
            body = custom_body
            body = re.sub(r"\{\{\s*Vendor Name\s*\}\}", vendor_name, body, flags=re.IGNORECASE)
            body = re.sub(r"\{\{\s*Category\s*\}\}", category, body, flags=re.IGNORECASE)
            body = re.sub(r"\{\{\s*Project Name\s*\}\}", project_name, body, flags=re.IGNORECASE)
        else:
            body = f"""Dear {vendor_name},

We are requesting a quotation for the materials listed in the attached RFQ document.

Project: {project_name}
Category: {category}

Please provide your quotation including:

* Unit price
* Delivery timeline
* Payment terms

Kindly respond with your quotation at the earliest.

Best regards
Procurement Team"""

        msg.attach(MIMEText(body, 'plain'))

        # Attachment
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(excel_content)
        encoders.encode_base64(part)
        if not filename:
            filename = f"RFQ_{category}_{project_name.replace(' ', '_')}.xlsx"
            
        part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
        msg.attach(part)

        # Connect and send
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls() # Enable security for Gmail
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {vendor_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {vendor_email}: {e}")
        return False
