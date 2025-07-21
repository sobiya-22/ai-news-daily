import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
from services.query_data import fetch_subscriber_emails

load_dotenv()

EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

recipients = fetch_subscriber_emails()

def send_digest_email(digest_text: str):
    html_digest = format_digest_as_html(digest_text)
    
    for recipient in recipients:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "📰 Weekly AI News Digest"
        msg["From"] = EMAIL
        msg["To"] = recipient

        msg.attach(MIMEText(digest_text, "plain"))
        msg.attach(MIMEText(html_digest, "html"))

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(EMAIL, APP_PASSWORD)
                server.send_message(msg)
                print(f"Digest sent to {recipient}")
        except Exception as e:
            print(f"Failed to send to {recipient}: {e}")

def format_digest_as_html(digest_text: str) -> str:
    digest_html = digest_text.replace("**", "<b>").replace("\n\n", "<br><br>").replace("\n- ", "<li>").replace("\n", "<br>")
    return f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f9f9f9;
                padding: 20px;
                color: #333;
            }}
            .container {{
                background: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            h2 {{
                color: #0066cc;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>📰 AI News Digest</h2>
            <p>{digest_html}</p>
        </div>
    </body>
    </html>
    """

