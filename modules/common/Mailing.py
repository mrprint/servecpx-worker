# -*- coding: utf8

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from system.basemodule import BaseModule
import options as config


class Mailing(BaseModule):

    def cmd_send(self, recipient, subject, message, from_email=None, sender_name=None):

        msg = MIMEMultipart('alternative')
        msg["Subject"] = subject or "GameCPx mailing system"
        msg["From"] = "GameCPx mailing system <%s>" %config.smtp_login
        msg["To"] = recipient

        content = MIMEText(message.encode("utf-8"), 'html')
        content["Content-Type"] = "text/html; charset=utf-8"

        msg.attach(content)

        self.logger.info("Sending mail using smtp host:%s and login:%s" % (config.smtp_host, config.smtp_login))
        conn = smtplib.SMTP(config.smtp_host)
        conn.ehlo()
        conn.starttls()
        conn.ehlo()
        conn.login(config.smtp_login, config.smtp_password)

        if from_email is None:
            from_email = "GameCPx mailing system <%s>" % config.smtp_login

        result = conn.sendmail(from_email, recipient, msg.as_string())
        conn.quit()
        self.logger.info("Mail sent!")
        return result
