import smtplib

# from email import encoders
# from email.header import Header
from email.mime.text import MIMEText

# from email.mime.base import MIMEBase
# from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

import os, sys
from dotenv import load_dotenv

load_dotenv()

import pathlib

here_dir = pathlib.Path(__file__).parent.resolve()

EMAIL_LOOKUP = {
    "pranav": os.getenv("PRANAV_MAIN_EMAIL"),
    "katey": os.getenv("KATEY_MAIN_EMAIL"),
}


def process_job(job_id: str):
    filename = here_dir / "scheduled_emails" / f"email_{job_id}.txt"
    if not os.path.isfile(filename):
        raise SystemExit(1)

    with open(filename, "r") as f:
        to_addr = EMAIL_LOOKUP[f.readline().strip()]
        subject = f.readline().strip()
        message = f.read()

    send_gmail(to_addr, subject, message)


def send_gmail(to_addr: str, subject: str, message: str):
    gmail_address = os.getenv("FROM_EMAIL")
    gmail_passwd = os.getenv("FROM_EMAIL_PASSWD")
    smtp = "smtp.gmail.com"

    msgRoot = MIMEMultipart("related")
    msgRoot["Subject"] = subject
    msgRoot["From"] = f"Pranav's Reminders <{os.getenv('FROM_EMAIL')}>"
    msgRoot["To"] = to_addr
    msgRoot.preamble = "This is a multi-part message in MIME format."

    msgAlternative = MIMEMultipart("alternative")
    msgRoot.attach(msgAlternative)

    msgText = MIMEText(message)
    msgAlternative.attach(msgText)

    msgText = MIMEText(message, "html")
    msgAlternative.attach(msgText)

    s = smtplib.SMTP(smtp, 587)
    s.starttls()
    s.login(gmail_address, gmail_passwd)
    s.sendmail(gmail_address, to_addr, msgRoot.as_string())
    s.quit()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_job(sys.argv[1])
    else:
        raise SystemExit(1)
