import json
import os
import random
from urllib.parse import unquote
from typing import Annotated

from cryptography import x509
from cryptography.x509 import ObjectIdentifier
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend
from fastapi import FastAPI, HTTPException, Request, Header, Query
from . import conf
from . import certificate_extensions

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


app = FastAPI(
    title="Perseus Energy Demo Resource API",
    root_path=conf.OPEN_API_ROOT,
)


@app.get("/", response_model=dict)
def root():
    return {"urls": ["/api/v1/"]}


@app.get("/api/v1", response_model=dict)
def api_urls():
    return {"urls": ["/api/v1/consumption"]}


@app.get("/api/v1/info")
def request_info(
    request: Request,
    x_amzn_mtls_clientcert: Annotated[str | None, Header()] = None,
):
    """Return full details about the received request, including http and https headers
    Useful for testing and debugging
    """
    response = {
        "request": {
            "headers": dict(request.headers),
            "method": request.method,
            "url": request.url,
            # "body": request.body().decode("utf-8"),
        },
        # "environ": str(request.environ),
    }
    if x_amzn_mtls_clientcert is not None:
        cert = x509.load_pem_x509_certificate(
            bytes(unquote(x_amzn_mtls_clientcert), "utf-8")
        )
        response["client_subject"] = cert.subject.rfc4514_string()
    return response


@app.get("/api/v1/supply-voltage")
def request_supply_voltage(
    period: Annotated[str, Query()],
    x_amzn_mtls_clientcert: Annotated[str | None, Header()] = None,
):
    # Check the certificate includes the right role.
    require_role(
        "https://registry.estf.ib1.org/scheme/electricty/role/supply-voltage-reader",
        x_amzn_mtls_clientcert,
    )

    # Generate a random report.
    random.seed(period)
    response = {
        "period": period,
        "voltages": [int(230.0 + (random.random() * 20)) for x in range(16)],
    }
    return response


def require_role(role_name, quoted_certificate):
    """Check that the certificate presented by the client includes the given role,
    throwing an exception if the requirement isn't met. Assumes the proxy has verified
    the certificate.
    """
    # Belt and braces check to make sure the proxy is configured correctly.
    if quoted_certificate is None:
        raise HTTPException(status_code=401, detail="No client certificate provided")
    # Extract a list of roles from the certificate
    cert = x509.load_pem_x509_certificate(
        bytes(unquote(quoted_certificate), "utf-8"), default_backend()
    )
    try:
        role_der = cert.extensions.get_extension_for_oid(
            ObjectIdentifier("1.3.6.1.4.1.62329.1.1")
        ).value.value
    except x509.ExtensionNotFound:
        raise HTTPException(
            status_code=401,
            detail="Client certificate does not include role information",
        )
    roles = certificate_extensions.decode(
        der_bytes=role_der,
    )

    if role_name not in roles:
        raise HTTPException(
            status_code=401,
            detail="Client certificate does not include role " + role_name,
        )
