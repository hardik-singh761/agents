import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class EmailFetcher:
    def __init__(self, email_address: str, app_password: str):
        self.email_address = email_address
        self.app_password = app_password
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993

    def _decode_str(self, header_value):
        if not header_value:
            return ""
        decoded_list = decode_header(header_value)
        result = ""
        for bytes_or_str, encoding in decoded_list:
            if isinstance(bytes_or_str, bytes):
                result += bytes_or_str.decode(encoding or "utf-8", errors="ignore")
            else:
                result += str(bytes_or_str)
        return result

    def _extract_body(self, msg) -> str:
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if "attachment" in content_disposition:
                    continue
                if content_type == "text/plain":
                    try:
                        body += part.get_payload(decode=True).decode("utf-8", errors="ignore")
                    except Exception:
                        pass
                elif content_type == "text/html" and not body:
                    try:
                        html = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                        soup = BeautifulSoup(html, "html.parser")
                        body = soup.get_text(separator=" ", strip=True)
                    except Exception:
                        pass
        else:
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode("utf-8", errors="ignore")
                    if msg.get_content_type() == "text/html":
                        soup = BeautifulSoup(body, "html.parser")
                        body = soup.get_text(separator=" ", strip=True)
            except Exception:
                pass
        return body.strip()

    def fetch_emails_last_24h(self, hours: int = 24) -> list[dict]:
        """
        Fetches all emails received in the specified hours back window (default 24h).
        """
        if not self.app_password:
            raise ValueError("GMAIL_APP_PASSWORD is not set in .env")

        logging.info(f"Connecting to Gmail IMAP for {self.email_address}...")
        mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
        pwd = self.app_password.replace(" ", "").strip()
        mail.login(self.email_address, pwd)
        mail.select("INBOX")

        now = datetime.now(timezone.utc)
        since_time = now - timedelta(hours=hours)
        since_date_str = since_time.strftime("%d-%b-%Y")

        logging.info(f"Searching INBOX for emails since {since_date_str}...")
        status, messages = mail.search(None, f'(SINCE "{since_date_str}")')

        if status != "OK":
            logging.warning("No emails found or search failed.")
            mail.logout()
            return []

        email_ids = messages[0].split()
        logging.info(f"Found {len(email_ids)} emails since {since_date_str}. Filtering exact 24h window...")

        emails_list = []
        for e_id in email_ids:
            res, msg_data = mail.fetch(e_id, "(RFC822)")
            if res != "OK":
                continue

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = self._decode_str(msg.get("Subject", "(No Subject)"))
                    sender = self._decode_str(msg.get("From", "(Unknown Sender)"))
                    date_header = msg.get("Date")

                    msg_datetime = None
                    if date_header:
                        try:
                            msg_datetime = parsedate_to_datetime(date_header)
                            if msg_datetime.tzinfo is None:
                                msg_datetime = msg_datetime.replace(tzinfo=timezone.utc)
                        except Exception:
                            pass

                    # Filter to exact 24 hour window
                    if msg_datetime and msg_datetime < since_time:
                        continue

                    body = self._extract_body(msg)
                    # Limit body length to prevent context explosion
                    snippet = body[:1500] if body else "(Empty body)"

                    emails_list.append({
                        "id": e_id.decode("utf-8"),
                        "subject": subject,
                        "sender": sender,
                        "date": msg_datetime.isoformat() if msg_datetime else date_header,
                        "body_snippet": snippet
                    })

        mail.logout()
        logging.info(f"Successfully fetched {len(emails_list)} emails within the last {hours} hours.")
        return emails_list
