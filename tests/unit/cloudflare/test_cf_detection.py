from unittest.mock import AsyncMock

import pytest
from playwright.async_api import Page, Frame, ElementHandle

from camoufox_captcha.cloudflare.utils.detection import detect_cloudflare_challenge, \
    CF_TURNSTILE_INDICATORS_SELECTORS, CF_INTERSTITIAL_INDICATORS_SELECTORS


@pytest.fixture
def mock_page():
    page = AsyncMock(spec=Page)
    return page


@pytest.fixture
def mock_frame():
    frame = AsyncMock(spec=Frame)
    return frame


@pytest.fixture
def mock_element_handle():
    element = AsyncMock(spec=ElementHandle)
    return element


@pytest.mark.asyncio
async def test_detect_cloudflare_challenge_turnstile_found(mock_page):
    """ Test Cloudflare Turnstile challenge detection when present """
    # mock returns an element for the first selector
    mock_element = AsyncMock()
    mock_page.query_selector.side_effect = lambda selector: mock_element \
        if selector == CF_TURNSTILE_INDICATORS_SELECTORS[0] else None

    result = await detect_cloudflare_challenge(mock_page, challenge_type='turnstile')

    assert result is True
    assert mock_page.query_selector.call_count == 1, 'Should stop after finding the first match'


@pytest.mark.asyncio
async def test_detect_cloudflare_challenge_turnstile_not_found(mock_page):
    """ Test Cloudflare Turnstile challenge detection when absent """
    # mock no selectors match
    mock_page.query_selector.return_value = None

    result = await detect_cloudflare_challenge(mock_page, challenge_type='turnstile')

    assert result is False
    assert mock_page.query_selector.call_count == len(CF_TURNSTILE_INDICATORS_SELECTORS), 'Should check all selectors'


@pytest.mark.asyncio
async def test_detect_cloudflare_challenge_interstitial_found(mock_frame):
    """ Test Cloudflare interstitial challenge detection when present """
    mock_frame.query_selector.return_value = CF_INTERSTITIAL_INDICATORS_SELECTORS[0]

    result = await detect_cloudflare_challenge(mock_frame, challenge_type='interstitial')

    assert result is True


@pytest.mark.asyncio
async def test_detect_cloudflare_challenge_interstitial_not_found(mock_frame):
    """ Test Cloudflare interstitial challenge detection when absent """
    # mock no selectors match
    mock_frame.query_selector.return_value = None

    result = await detect_cloudflare_challenge(mock_frame, challenge_type='interstitial')

    assert result is False
    assert mock_frame.query_selector.call_count == len(CF_INTERSTITIAL_INDICATORS_SELECTORS)


@pytest.mark.asyncio
async def test_detect_cloudflare_challenge_with_element_handle(mock_element_handle):
    """ Test Cloudflare challenge detection with ElementHandle """
    mock_element_handle.query_selector.side_effect = lambda selector: AsyncMock() \
        if selector == CF_TURNSTILE_INDICATORS_SELECTORS[0] else None

    result = await detect_cloudflare_challenge(mock_element_handle)

    assert result is True
