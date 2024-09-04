import pytest

from fastapi.exceptions import HTTPException

from tests import client_certificate
from api.main import require_role


def test_role_in_certificate():
    test_role = (
        "https://registry.estf.ib1.org/scheme/electricty/role/supply-voltage-reader"
    )
    cert_urlencoded = client_certificate(
        roles=[
            test_role,
            "https://registry.estf.ib1.org/scheme/electricty/group/reporter",
        ]
    )
    require_role(  # No assertion, just checking for exceptions
        test_role,
        cert_urlencoded,
    )


def test_role_not_in_certificate():
    test_role = (
        "https://registry.estf.ib1.org/scheme/electricty/role/supply-voltage-reader"
    )
    cert_urlencoded = client_certificate(
        roles=[
            "https://registry.estf.ib1.org/scheme/electricty/group/reporter",
        ]
    )
    with pytest.raises(HTTPException):
        require_role(test_role, cert_urlencoded)


def test_certificate_with_no_roles():
    cert_urlencoded = client_certificate()
    with pytest.raises(HTTPException):
        require_role(
            "https://registry.estf.ib1.org/scheme/electricty/role/supply-voltage-reader",
            cert_urlencoded,
        )


def test_empty_role():
    cert_urlencoded = client_certificate(roles=[""])
    with pytest.raises(HTTPException):
        require_role(
            "https://registry.estf.ib1.org/scheme/electricty/role/supply-voltage-reader",
            cert_urlencoded,
        )


def test_no_certificate_supplied():
    with pytest.raises(HTTPException):
        require_role(
            "https://registry.estf.ib1.org/scheme/electricty/role/supply-voltage-reader",
            None,
        )


def test_bad_certificate():
    with pytest.raises(ValueError):
        require_role(
            "https://registry.estf.ib1.org/scheme/electricty/role/supply-voltage-reader",
            "Not a PEM encoded certificate",
        )
