import pytest

from fastapi.exceptions import HTTPException

from tests import cert_response
from api.main import require_role


def test_role_in_certificate():
    cert_urlencoded = cert_response(cert_file="cert1.pem", urlencoded=True)
    require_role("supply-voltage-reader@electricity", cert_urlencoded)
    require_role("reporter@electricity", cert_urlencoded)


def test_role_not_in_certificate():
    cert_urlencoded = cert_response(cert_file="cert2.pem", urlencoded=True)
    with pytest.raises(HTTPException):
        require_role("supply-voltage-reader@electricity", cert_urlencoded)


def test_certificate_with_no_roles():
    cert_urlencoded = cert_response(cert_file="cert3.pem", urlencoded=True)
    with pytest.raises(HTTPException):
        require_role("supply-voltage-reader@electricity", cert_urlencoded)


def test_empty_role():
    cert_urlencoded = cert_response(cert_file="cert1.pem", urlencoded=True)
    with pytest.raises(HTTPException):
        require_role("", cert_urlencoded)


def test_no_certificate_supplied():
    with pytest.raises(HTTPException):
        require_role("supply-voltage-reader@electricity", None)


def test_bad_certificate():
    with pytest.raises(ValueError):
        require_role("supply-voltage-reader@electricity", "Not a PEM encoded certificate")
