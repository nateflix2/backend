"""
Email functions
"""
import os
import requests


def send_password_reset_email(dest_email, username, reset_link):
    subject = "Reset your password"
    body = (
        "Hi {username},\n\n"
        "You have requested to change your password, please click the following link, or "
        "copy-paste it into your address bar to change it. The link will work "
        "for 24 hours.\n\n{link}"
    ).format(username=username, link=reset_link)

    return _send_mail(dest_email, subject, body)


def _send_mail(dest_email, subject, body):
    """
    Internal function to send mail with subject and body
    Returns True on success, False otherwise
    """
    url = "https://api.sendgrid.com/v3/mail/send"
    sender = os.environ["NF_EMAIL_SENDER"]
    name = os.environ["NF_EMAIL_SENDER_NAME"]
    headers = {"Authorization": "Bearer {}".format(os.environ["NF_SENDGRID_KEY"])}
    data = {
        "personalizations": [{"to": [{"email": dest_email}]}],
        "from": {"email": sender, "name": name},
        "subject": subject,
        "content": [{"type": "text/plain", "value": body}],
    }
    try:
        r = requests.post(url, json=data, headers=headers)
        r.raise_for_status()
    except requests.exceptions.RequestException:
        return False

    return True
