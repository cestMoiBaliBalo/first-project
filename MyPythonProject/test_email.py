# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import locale
import os
import smtplib
from email.message import EmailMessage
from email.parser import BytesParser
from email.policy import default

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "french")

with open(r"C:\Users\Xavier\Downloads\python_mail.txt", "rb") as fp:
    headers = BytesParser(policy=default).parse(fp)

# print('To: {0}'.format(headers['to']))
# print('From: {0}'.format(headers['from']))
# print('Subject: {0}'.format(headers['subject']))
#
# print('Recipient username: {0}'.format(headers['to'].addresses[0].username))
# print('Sender name: {0}'.format(headers['from'].addresses[0].display_name))

# print(headers.keys())
# print(headers.get_body(preferencelist="plain"))
# print(headers.get_content())

msg = EmailMessage()
msg['Subject'] = headers['subject']
msg['From'] = headers['from']
msg['To'] = headers['to']
msg.add_header("Cc", headers['cc'])
msg.add_header("Reply-To", headers['reply-to'])
msg.add_header("Keywords", headers['keywords'])
msg.set_content(headers.get_content())
s = smtplib.SMTP(host=os.path.expandvars("%_SMTP_HOST%"), port=int(os.path.expandvars("%_SMTP_PORT%")))
s.login(os.path.expandvars("%_SMTP_USER%"), os.path.expandvars("%_SMTP_PASSWORD%"))
s.send_message(msg)
s.quit()
