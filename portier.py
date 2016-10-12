#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Richard Lamboj'
__copyright__ = 'Copyright 2016, Unicom'
__credits__ = ['Richard Lamboj']
__license__ = 'Proprietary'
__version__ = '0.1'
__maintainer__ = 'Richard Lamboj'
__email__ = 'rlamboj@unicom.ws'
__status__ = 'Development'


# standard library imports
import os
import sys
import time
import socket
import smtplib
import ConfigParser

from email.mime.text import MIMEText

# related third party imports

# local application/library specific imports


STD_OUT = 1
STD_ERR = 2


def log(msg, channel=STD_OUT):
    date = time.strftime("[%d-%m-%Y %H:%M:%S]", time.gmtime())
    if channel != STD_ERR:
        sys.stdout.write("%s %s\n" % (date, msg))
    else:
        sys.stderr.write("%s %s\n" % (date, msg))


def send(mailfrom, rcpttos, subject, message, smtp_ip="localhost", smtp_port=25, username="", password="", resend_timeout=60):
    send_complete = False

    # Create a text/plain message
    mail = MIMEText(message)

    mail['Subject'] = subject
    mail['From'] = mailfrom
    mail['To'] = ", ".join(rcpttos)

    while send_complete == False:
        try:
            server = smtplib.SMTP(smtp_ip, smtp_port)
            if username != "":
                server.login(username, password)
            server.sendmail(mailfrom, rcpttos, mail.as_string())
            server.quit()
            send_complete = True
        except:
            log("Error: Trying to send mail again in %s Seconds...\n" % (resend_timeout), STD_ERR)
            time.sleep(resend_timeout)


def main():
    """
    [smtp]
    ip = localhost
    port = 25
    username =
    password =
    resend_timeout = 60
    [message]
    from =  portier@localhost
    to = root@localhost
    subject = Login: %(user)s from %(rhost)s on %(host)s
    message =
    """
    hostname = socket.gethostname()
    mailfrom = "postler@" + hostname
    mapping = {
        'user': os.environ.get('PAM_USER', ''),
        'rhost': os.environ.get('PAM_RHOST', ''),
        'host': hostname
    }
    smtp_defaults = {
        "ip": "localhost",
        "port": "25",
        "username": "",
        "password": "",
        "resend_timeout": "60"
    }
    message_defaults = {
        "from": mailfrom,
        "to": "root@localhost",
        "subject": "Login: %(user)s from %(rhost)s on %(host)s",
        "message": ""
    }

    config = ConfigParser.ConfigParser()
    config.read(os.path.join(os.path.dirname(os.path.abspath(__file__.decode(sys.getfilesystemencoding()))), 'configuration.ini'))

    smtp_ip = config.get('smtp', 'ip', 0, smtp_defaults)
    smtp_port = int(config.get('smtp', 'port', 0, smtp_defaults))
    username = config.get('smtp', 'username', 0, smtp_defaults)
    password = config.get('smtp', 'password', 0, smtp_defaults)
    resend_timeout = int(config.get('smtp', 'resend_timeout', 0, smtp_defaults))

    subject = config.get('message', 'subject', 1, message_defaults) % mapping
    message = config.get('message', 'message', 1, message_defaults) % mapping
    mailfrom = config.get('message', 'from', 0, message_defaults)
    rcpttos = [rcpt.strip() for rcpt in config.get('message', 'to', 0, message_defaults).split(",")]

    if 'PAM_TYPE' in os.environ:
        if os.environ['PAM_TYPE'] != "close_session":
            send(mailfrom, rcpttos, subject, message, smtp_ip, smtp_port, username, password, resend_timeout)


if __name__ == '__main__':
    main()