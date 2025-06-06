from unittest.mock import AsyncMock, patch

import pytest
from playwright.async_api import Page

from camoufox_captcha import solve_captcha


@pytest.fixture
def mock_page():
    page = AsyncMock(spec=Page)
    return page


@pytest.mark.asyncio
@patch('camoufox_captcha.solve_cloudflare_by_click', AsyncMock(return_value=True))
async def test_solve_captcha_default_challenge_type(mock_page):
    """ Test solve_captcha when challenge_type is None or empty """
    result = await solve_captcha(mock_page, challenge_type=None)
    assert result is True

    result = await solve_captcha(mock_page, challenge_type="")
    assert result is True


@pytest.mark.asyncio
async def test_solve_captcha_unsupported_challenge_type(mock_page):
    """ Test solve_captcha with unsupported challenge type """
    with pytest.raises(ValueError) as excinfo:
        await solve_captcha(mock_page, challenge_type="invalid")

    assert "Unsupported Cloudflare challenge type" in str(excinfo.value)
    assert "'invalid'" in str(excinfo.value)
    assert "interstitial" in str(excinfo.value)
    assert "turnstile" in str(excinfo.value)


@pytest.mark.asyncio
async def test_solve_captcha_unsupported_method(mock_page):
    """ Test solve_captcha with unsupported method """
    with pytest.raises(ValueError) as excinfo:
        await solve_captcha(mock_page, method="invalid_method")

    assert "Unsupported method 'invalid_method' for Cloudflare captcha" in str(excinfo.value)
    assert "Currently only 'click' method is supported" in str(excinfo.value)


@pytest.mark.asyncio
async def test_solve_captcha_unsupported_captcha_type(mock_page):
    """ Test solve_captcha with unsupported captcha type """
    with pytest.raises(ValueError) as excinfo:
        await solve_captcha(mock_page, captcha_type="recaptcha")

    assert "Unsupported captcha type: 'recaptcha'" in str(excinfo.value)
    assert "Currently only 'cloudflare' is supported" in str(excinfo.value)
