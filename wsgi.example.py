"""
WSGI Configuration File
"""
import os
from nf2.app import make_app

# Environment variables to set
environs = {
    # The secret key to use for tokens.
    'NF_SECRET_KEY': 'mysecretkey',

    # Email sender address
    'NF_EMAIL_SENDER': 'noreply@nateflix.cc',

    # Email sender name
    'NF_EMAIL_SENDER_NAME': 'nateflix',

    # Sendgrid API Key
    'NF_SENDGRID_KEY': 'mysendgridkey',

    # (optional) defaults to "localhost". The address of the mongodb database to use.
    #'NF_DB_ADDR': 'localhost',

    # (optional) defaults to "27017"
    #'NF_DB_PORT': 27017
}

for k, v in environs.items():
    os.environ[k] = v

app = application = make_app()
