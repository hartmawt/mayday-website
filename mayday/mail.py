import email.utils
import os
import smtplib

import jinja2
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from mayday.logger import logger


GMAIL_USERNAME = os.environ.get("GMAIL_USERNAME", "")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD", "")
MAILER = os.environ.get("MAILER", "help@maydayplumbingservice.com")


def render_email_template(path="/app/templates", **kwargs):
    templateLoader = jinja2.FileSystemLoader(searchpath=path)
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "email.htm"
    template = templateEnv.get_template(TEMPLATE_FILE)
    return template.render(**kwargs)


def send_mail(customer_email, name, message):
    custom_message = f"Name: {name}\nEmail: {customer_email}\nInquiry: {message}"
    msg = MIMEMultipart()
    msg.attach(MIMEText(render_email_template(message=custom_message), 'html'))
    msg['Subject'] = "New Customer Inquiry"
    msg['From'] = email.utils.formataddr(("booking@maydayplumbingservice.com", f"{GMAIL_USERNAME}@gmail.com"))
    msg['To'] = MAILER

    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.ehlo()
        s.starttls()
        s.login(GMAIL_USERNAME, GMAIL_PASSWORD)
        s.sendmail("booking@maydayplumbingservice.com", [MAILER], msg.as_string())
        s.quit()

        result = "Your email was successfully sent to Mayday Plumbing! We look forward to working with you in the future", "info"

    except Exception as e:
        logger.error(f"Failed to send email. Error: {e}")

        result = ("Unfortunately we were unable to send your email due to a technical issue."
                 f" Please reach out to us via {MAILER} and we would happy assist you!", "error")
    
    finally:
        return result