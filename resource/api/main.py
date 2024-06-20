import json
import os
import random
from urllib.parse import unquote
from typing import Annotated

from cryptography import x509
from cryptography.x509.oid import NameOID
from fastapi import FastAPI, HTTPException, Request, Header, Query

from . import conf

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
        cert = x509.load_pem_x509_certificate(bytes(unquote(x_amzn_mtls_clientcert), 'utf-8'))
        response["client_subject"] = cert.subject.rfc4514_string()
    return response


@app.get("/api/v1/supply-voltage")
def request_supply_voltage(
    period: Annotated[str, Query()],
    x_amzn_mtls_clientcert: Annotated[str | None, Header()] = None,
):
    # Check the certificate includes the right role.
    require_role("supply-voltage-reader@electricity", x_amzn_mtls_clientcert)

    # Generate a random report.
    random.seed(period)
    response = {
        "period": period,
        "voltages": [int(230.0+(random.random()*20)) for x in range(16)]
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
    # Extrace a list of roles from the certificate
    cert = x509.load_pem_x509_certificate(bytes(unquote(quoted_certificate), 'utf-8'))
    roles = [ou.value for ou in cert.subject.get_attributes_for_oid(NameOID.ORGANIZATIONAL_UNIT_NAME)]
    # Check the given role is included in the list of client's roles
    if role_name not in roles:
        raise HTTPException(status_code=401, detail="Client certificate does not include role "+role_name)
