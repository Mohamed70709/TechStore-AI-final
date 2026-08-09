import os
from dotenv import load_dotenv
import resend

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

params = {
    "from": "onboarding@resend.dev",
    "to": ["mohamed.mm70765@gmail.com"],
    "subject": "TechStore Test Email",
    "html": "<h1>Hello!</h1><p>This is a test email from TechStore.</p>",
}

email = resend.Emails.send(params)

print(email)