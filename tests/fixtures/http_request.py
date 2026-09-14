import pytest
from fastapi import Request


@pytest.fixture
def http_request() -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/",
            "headers": [],
        }
    )