import pytest
import fastapi
from fastapi.testclient import TestClient
from tests import client_certificate
from api.main import app

client = TestClient(app)


def test_report_authorised():
    """
    If certificate has right role, return data and 200
    """
    test_role = (
        "https://registry.estf.ib1.org/scheme/electricty/role/supply-voltage-reader"
    )
    response = client.get(
        "/api/v1/supply-voltage?period=ABC",
        headers={"x-amzn-mtls-clientcert": client_certificate(roles=[test_role])},
    )
    assert response.status_code == 200


def test_report_unauthorised():
    """
    If the certificate does not contain the role, return a 401
    """
    response = client.get(
        "/api/v1/supply-voltage?period=ABC",
        headers={
            "x-amzn-mtls-clientcert": client_certificate(
                roles=["https://registry.estf.ib1.org/scheme/another/group/supplier"]
            )
        },
    )
    assert response.status_code == 401
