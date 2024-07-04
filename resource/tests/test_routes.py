
import pytest
import fastapi
from fastapi.testclient import TestClient
from tests  import cert_response
from api.main import app

client = TestClient(app)


def test_report_authorised():
    """
    If certificate has right role, return data and 200
    """
    response = client.get("/api/v1/supply-voltage?period=ABC", headers={'x-amzn-mtls-clientcert': cert_response(cert_file="cert1.pem", urlencoded=True)})
    assert response.status_code == 200


def test_report_unauthorised():
    """
    If the certificate does not contain the role, return a 401
    """
    response = client.get("/api/v1/supply-voltage?period=ABC", headers={'x-amzn-mtls-clientcert': cert_response(cert_file="cert2.pem", urlencoded=True)})
    assert response.status_code == 401
