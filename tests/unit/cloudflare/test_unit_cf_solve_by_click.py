from unittest.mock import AsyncMock, patch

import pytest
from playwright.async_api import Page, Frame, ElementHandle

from camoufox_captcha import solve_captcha


@pytest.fixture
def mock_page():
    page = AsyncMock(spec=Page)
    return page


@pytest.fixture
def mock_frame():
    frame = AsyncMock(spec=Frame)
    return frame


@pytest.fixture
def mock_element():
    element = AsyncMock(spec=ElementHandle)
    return element


@pytest.fixture
def mock_checkbox():
    checkbox = AsyncMock(spec=ElementHandle)
    return checkbox


@pytest.mark.asyncio
async def test_solve_by_click_no_challenge_detected(mock_page):
    """ Test solving by click when no Cloudflare challenge is detected """
    with patch('camoufox_captcha.cloudflare.solve_by_click.detect_cloudflare_challenge',
               AsyncMock(return_value=False)), \
            patch('camoufox_captcha.cloudflare.solve_by_click.detect_expected_content',
                  AsyncMock(return_value=False)):
        result = await solve_captcha(mock_page, captcha_type='cloudflare', challenge_type='interstitial')

        assert result is True


@pytest.mark.asyncio
async def test_solve_by_click_expected_content_already_present(mock_page):
    """ Test solving by click when expected content is already detected """
    with patch('camoufox_captcha.cloudflare.solve_by_click.detect_cloudflare_challenge',
               AsyncMock(return_value=True)), \
            patch('camoufox_captcha.cloudflare.solve_by_click.detect_expected_content',
                  AsyncMock(return_value=True)):
        result = await solve_captcha(mock_page, captcha_type='cloudflare', challenge_type='interstitial',
                                     expected_content_selector='.content')

        assert result is True


@pytest.mark.asyncio
async def test_solve_by_click_no_iframes_found(mock_page):
    """ Test solving by click when no Cloudflare iframes are found """
    with patch('camoufox_captcha.cloudflare.solve_by_click.detect_cloudflare_challenge',
               AsyncMock(return_value=True)), \
            patch('camoufox_captcha.cloudflare.solve_by_click.detect_expected_content',
                  AsyncMock(return_value=False)), \
            patch('camoufox_captcha.cloudflare.solve_by_click.search_shadow_root_iframes',
                  AsyncMock(return_value=[])):
        result = await solve_captcha(mock_page, captcha_type='cloudflare', challenge_type='interstitial')

        assert result is False


@pytest.mark.asyncio
async def test_solve_by_click_no_checkbox_found(mock_page, mock_frame):
    """ Test solving by click when no checkbox is found in iframes """
    with patch('camoufox_captcha.cloudflare.solve_by_click.detect_cloudflare_challenge',
               AsyncMock(return_value=True)), \
            patch('camoufox_captcha.cloudflare.solve_by_click.detect_expected_content',
                  AsyncMock(return_value=False)), \
            patch('camoufox_captcha.cloudflare.solve_by_click.search_shadow_root_iframes',
                  AsyncMock(return_value=[mock_frame])), \
            patch('camoufox_captcha.cloudflare.solve_by_click.get_ready_checkbox',
                  AsyncMock(return_value=None)):
        result = await solve_captcha(mock_page, captcha_type='cloudflare', challenge_type='interstitial')

        assert result is False


@pytest.mark.asyncio
async def test_solve_by_click_interstitial_success(mock_page, mock_frame, mock_checkbox):
    """ Test successful solving of interstitial challenge """
    detect_challenge_mock = AsyncMock()
    detect_challenge_mock.side_effect = [True, False]  # challenge present, then absent after solving

    with patch('camoufox_captcha.cloudflare.solve_by_click.detect_cloudflare_challenge',
               detect_challenge_mock), \
            patch('camoufox_captcha.cloudflare.solve_by_click.detect_expected_content',
                  AsyncMock(return_value=False)), \
            patch('camoufox_captcha.cloudflare.solve_by_click.search_shadow_root_iframes',
                  AsyncMock(return_value=[mock_frame])), \
            patch('camoufox_captcha.cloudflare.solve_by_click.get_ready_checkbox',
                  AsyncMock(return_value=(mock_frame, mock_checkbox))), \
            patch('asyncio.sleep', AsyncMock()):
        result = await solve_captcha(mock_page, captcha_type='cloudflare', challenge_type='interstitial')

        assert result is True
        mock_checkbox.click.assert_called_once()


@pytest.mark.asyncio
async def test_solve_by_click_turnstile_success(mock_page, mock_frame, mock_checkbox):
    """ Test successful solving of turnstile challenge """
    success_element = AsyncMock()

    with patch('camoufox_captcha.cloudflare.solve_by_click.detect_cloudflare_challenge',
               AsyncMock(return_value=True)), \
            patch('camoufox_captcha.cloudflare.solve_by_click.detect_expected_content',
                  AsyncMock(return_value=False)), \
            patch('camoufox_captcha.cloudflare.solve_by_click.search_shadow_root_iframes',
                  AsyncMock(return_value=[mock_frame])), \
            patch('camoufox_captcha.cloudflare.solve_by_click.get_ready_checkbox',
                  AsyncMock(return_value=(mock_frame, mock_checkbox))), \
            patch('camoufox_captcha.cloudflare.solve_by_click.search_shadow_root_elements',
                  AsyncMock(return_value=[success_element])), \
            patch('asyncio.sleep', AsyncMock()):
        result = await solve_captcha(mock_page, captcha_type='cloudflare', challenge_type='turnstile')

        assert result is True
        mock_checkbox.click.assert_called_once()


@pytest.mark.asyncio
async def test_solve_by_click_click_exception(mock_page, mock_frame, mock_checkbox):
    """ Test solve by click when checkbox click raises an exception """
    mock_checkbox.click.side_effect = Exception("Click error")
    detect_challenge_mock = AsyncMock()
    detect_challenge_mock.side_effect = [True, False]  # challenge present, then absent after solving

    with patch('camoufox_captcha.cloudflare.solve_by_click.detect_cloudflare_challenge',
               detect_challenge_mock), \
            patch('camoufox_captcha.cloudflare.solve_by_click.detect_expected_content',
                  AsyncMock(return_value=False)), \
            patch('camoufox_captcha.cloudflare.solve_by_click.search_shadow_root_iframes',
                  AsyncMock(return_value=[mock_frame])), \
            patch('camoufox_captcha.cloudflare.solve_by_click.get_ready_checkbox',
                  AsyncMock(return_value=(mock_frame, mock_checkbox))), \
            patch('asyncio.sleep', AsyncMock()):
        result = await solve_captcha(mock_page, captcha_type='cloudflare', challenge_type='interstitial')

        assert result is True  # still succeed because challenge is gone


@pytest.mark.asyncio
async def test_solve_by_click_max_attempts_reached(mock_page, mock_frame, mock_checkbox):
    """ Test solving by click when max attempts are reached without success """
    detect_challenge_mock = AsyncMock(return_value=True)  # challenge always present
    detect_content_mock = AsyncMock(return_value=False)  # content never appears

    solve_attempts = 3

    with patch('camoufox_captcha.cloudflare.solve_by_click.detect_cloudflare_challenge',
               detect_challenge_mock), \
            patch('camoufox_captcha.cloudflare.solve_by_click.detect_expected_content',
                  detect_content_mock), \
            patch('camoufox_captcha.cloudflare.solve_by_click.search_shadow_root_iframes',
                  AsyncMock(return_value=[mock_frame])), \
            patch('camoufox_captcha.cloudflare.solve_by_click.get_ready_checkbox',
                  AsyncMock(return_value=(mock_frame, mock_checkbox))), \
            patch('camoufox_captcha.cloudflare.solve_by_click.search_shadow_root_elements',
                  AsyncMock(return_value=[])), \
            patch('asyncio.sleep', AsyncMock()):
        result = await solve_captcha(mock_page, captcha_type='cloudflare', challenge_type='interstitial',
                                     solve_attempts=solve_attempts)

        assert result is False
        assert detect_challenge_mock.call_count > 1
        assert mock_checkbox.click.call_count == solve_attempts
