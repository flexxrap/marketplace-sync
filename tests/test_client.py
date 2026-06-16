from unittest.mock import MagicMock, patch

import httpx
import pytest

from client import get_products

_SAMPLE = [
    {
        "id": 175028571,
        "name": "Ноутбук Lenovo IdeaPad 3",
        "brand": "Lenovo",
        "subjectName": "Ноутбуки",
        "priceU": 5990000,
        "salePriceU": 4990000,
        "sale": 17,
        "rating": 4.8,
        "feedbacks": 1250,
    },
    {
        "id": 123456789,
        "name": "Ноутбук ASUS VivoBook",
        "brand": "ASUS",
        "subjectName": "Ноутбуки",
        "priceU": 4500000,
        "salePriceU": 4500000,
        "sale": 0,
        "rating": 4.5,
        "feedbacks": 890,
    },
]


def _ok(products: list) -> MagicMock:
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = 200
    resp.raise_for_status = MagicMock()
    resp.json.return_value = {"data": {"products": products, "total": len(products)}}
    return resp


def _429() -> MagicMock:
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = 429
    resp.raise_for_status.side_effect = httpx.HTTPStatusError(
        "429 Too Many Requests", request=MagicMock(), response=resp
    )
    return resp


def test_get_products_normalizes_fields():
    with patch("client.httpx.get", return_value=_ok(_SAMPLE)):
        products = get_products("ноутбук")

    assert len(products) == 2
    p = products[0]
    assert p["id"] == 175028571
    assert p["name"] == "Ноутбук Lenovo IdeaPad 3"
    assert p["brand"] == "Lenovo"
    assert p["category"] == "Ноутбуки"
    assert p["price_rub"] == 59900       # 5990000 / 100
    assert p["sale_price_rub"] == 49900  # 4990000 / 100
    assert p["discount_pct"] == 17


def test_get_products_retries_on_429():
    """Client retries on 429 and succeeds on the third attempt."""
    with patch("time.sleep"):  # skip tenacity backoff waits
        with patch(
            "client.httpx.get",
            side_effect=[_429(), _429(), _ok(_SAMPLE)],
        ):
            products = get_products("ноутбук")

    assert len(products) == 2


def test_get_products_raises_after_max_retries():
    """After 4 consecutive 429s tenacity re-raises the last HTTPStatusError."""
    with patch("time.sleep"):
        with patch("client.httpx.get", return_value=_429()):
            with pytest.raises(httpx.HTTPStatusError):
                get_products("ноутбук")


def test_get_products_empty_result():
    with patch("client.httpx.get", return_value=_ok([])):
        assert get_products("xyznotexist123") == []
