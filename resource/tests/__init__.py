import json
import os
from typing import Optional
import time
from urllib.parse import quote

from cryptography import x509
from cryptography.hazmat.backends import default_backend

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def cert_response(cert_file=None, urlencoded=False):
    if cert_file is None:
        raise Exception("No certificate file specified")
    with open(f"{ROOT_DIR}/fixtures/{cert_file}", "rb") as cert_content:
        cert_data = cert_content.read()
    if urlencoded:
        cert = quote(cert_data.decode())
    else:
        cert = x509.load_pem_x509_certificate(cert_data, default_backend())
    return cert

