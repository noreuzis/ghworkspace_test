import imaplib
import email
from email.header import decode_header
import openai

# Email credentials
EMAIL = "your_email@example.com"
PASSWORD = "your_password"
IMAP_SERVER = "imap.example.com"

# OpenAI API key
OPENAI_API_KEY = "your_openai_api_key"

def connect_to_email():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")
    return mail

def fetch_emails(mail):
    status, messages = mail.search(None, "ALL")
    email_ids = messages[0].split()
    return email_ids

def get_email_content(mail, email_id):
    status, msg_data = mail.fetch(email_id, "(RFC822)")
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    if "attachment" not in content_disposition:
                        body = part.get_payload(decode=True).decode()
                        return subject, body
            else:
                body = msg.get_payload(decode=True).decode()
                return subject, body

def summarize_text(text):
    openai.api_key = OPENAI_API_KEY
    response = openai.Completion.create(
        engine="davinci",
        prompt=f"Summarize the following text by topics:\n\n{text}",
        max_tokens=150
    )
    summary = response.choices[0].text.strip()
    return summary

def main():
    mail = connect_to_email()
    email_ids = fetch_emails(mail)
    for email_id in email_ids:
        subject, body = get_email_content(mail, email_id)
        summary = summarize_text(body)
        print(f"Subject: {subject}\nSummary: {summary}\n")

if __name__ == "__main__":
    main()
