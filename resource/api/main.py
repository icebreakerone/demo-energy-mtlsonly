import json
import os
from cryptography import x509
from urllib.parse import unquote
from typing import Annotated

from fastapi import FastAPI, HTTPException, Response, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request

from . import conf

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


app = FastAPI(
    docs_url="/api-docs",
    title="Perseus Energy Demo Resource API",
    root_path=conf.OPEN_API_ROOT,
)


@app.get("/", response_model=dict)
def root():
    return {"urls": ["/api/v1/"]}


@app.get("/api/v1", response_model=dict)
def api_urls():
    return {"urls": ["/api/v1/consumption"]}


# @app.get("/api/v1/info")
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

