import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class ReportMailer:
    """Sends the daily email digest report via Gmail SMTP."""

    def __init__(self, email_address: str, app_password: str):
        self.email_address = email_address
        self.app_password = app_password.replace(" ", "").strip()
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 465

    def send_report(self, subject: str, markdown_body: str, to_email: str) -> bool:
        """
        Sends the markdown report as an email.
        Returns True on success, False on failure.
        """
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"Agents Hub <{self.email_address}>"
            msg["To"] = to_email

            # Plain text version (raw markdown)
            text_part = MIMEText(markdown_body, "plain", "utf-8")
            msg.attach(text_part)

            # HTML version (basic formatting for email clients)
            html_body = self._markdown_to_basic_html(markdown_body)
            html_part = MIMEText(html_body, "html", "utf-8")
            msg.attach(html_part)

            logging.info(f"Connecting to Gmail SMTP to send report to {to_email}...")
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.email_address, self.app_password)
                server.send_message(msg)

            logging.info(f"Report emailed successfully to {to_email}")
            return True

        except Exception as e:
            logging.error(f"Failed to send report email: {e}", exc_info=True)
            return False

    def _markdown_to_basic_html(self, md: str) -> str:
        """
        Converts markdown to basic HTML for email rendering.
        Handles headers, bold, tables, and line breaks.
        """
        import re

        lines = md.split("\n")
        html_lines = []
        in_table = False

        for line in lines:
            stripped = line.strip()

            # Skip table separator rows (|---|---|)
            if re.match(r"^\|[\s\-:|]+\|$", stripped):
                continue

            # Table rows
            if stripped.startswith("|") and stripped.endswith("|"):
                cells = [c.strip() for c in stripped.strip("|").split("|")]
                if not in_table:
                    in_table = True
                    html_lines.append('<table style="border-collapse:collapse;width:100%;font-size:14px;">')
                    # First row is header
                    html_lines.append("<tr>" + "".join(
                        f'<th style="border:1px solid #ddd;padding:8px;background:#f4f4f4;text-align:left;">{c}</th>'
                        for c in cells
                    ) + "</tr>")
                else:
                    html_lines.append("<tr>" + "".join(
                        f'<td style="border:1px solid #ddd;padding:8px;">{c}</td>'
                        for c in cells
                    ) + "</tr>")
                continue
            elif in_table:
                in_table = False
                html_lines.append("</table><br>")

            # Headers
            if stripped.startswith("# "):
                html_lines.append(f'<h1 style="color:#1a1a2e;">{stripped[2:]}</h1>')
            elif stripped.startswith("## "):
                html_lines.append(f'<h2 style="color:#16213e;">{stripped[3:]}</h2>')
            elif stripped.startswith("### "):
                html_lines.append(f'<h3 style="color:#0f3460;">{stripped[4:]}</h3>')
            elif stripped.startswith("---"):
                html_lines.append('<hr style="border:1px solid #eee;">')
            elif stripped.startswith("> [!"):
                # GitHub-style callouts → styled div
                match = re.match(r">\s*\[!(NOTE|IMPORTANT|WARNING|CAUTION)\]", stripped)
                if match:
                    callout_type = match.group(1)
                    colors = {
                        "NOTE": "#0969da", "IMPORTANT": "#8250df",
                        "WARNING": "#9a6700", "CAUTION": "#cf222e"
                    }
                    color = colors.get(callout_type, "#333")
                    html_lines.append(
                        f'<div style="border-left:4px solid {color};padding:8px 16px;margin:8px 0;'
                        f'background:#f6f8fa;"><strong style="color:{color};">{callout_type}</strong><br>'
                    )
            elif stripped.startswith(">"):
                content = stripped.lstrip("> ").strip()
                if content:
                    html_lines.append(f'<span style="color:#555;">{content}</span><br>')
                else:
                    html_lines.append("</div>")
            elif stripped.startswith("- ") or stripped.startswith("* "):
                html_lines.append(f"<li>{stripped[2:]}</li>")
            elif stripped == "":
                html_lines.append("<br>")
            else:
                # Bold
                processed = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", stripped)
                # Inline code
                processed = re.sub(r"`(.+?)`", r'<code style="background:#f0f0f0;padding:2px 4px;border-radius:3px;">\1</code>', processed)
                html_lines.append(f"<p style='margin:4px 0;'>{processed}</p>")

        if in_table:
            html_lines.append("</table>")

        body_html = "\n".join(html_lines)
        return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
             max-width:700px;margin:0 auto;padding:20px;color:#1a1a2e;">
{body_html}
<br>
<hr style="border:1px solid #eee;">
<p style="color:#888;font-size:12px;">
    🤖 Sent automatically by <strong>Agents Hub</strong> — your personal AI agent framework.
</p>
</body>
</html>"""
