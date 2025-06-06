from unittest.mock import AsyncMock

import pytest
from playwright.async_api import Page, Frame, ElementHandle

from camoufox_captcha.common.detection import detect_expected_content


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
async def test_detect_expected_content_found(mock_page):
    """ Test expected content detection when present """
    mock_element = AsyncMock()
    mock_page.query_selector.return_value = mock_element
    selector = "#content"

    result = await detect_expected_content(mock_page, expected_content_selector=selector)

    assert result is True
    mock_page.query_selector.assert_called_once_with(selector)


@pytest.mark.asyncio
async def test_detect_expected_content_not_found(mock_page):
    """ Test expected content detection when absent """
    mock_page.query_selector.return_value = None
    selector = "#content"

    result = await detect_expected_content(mock_page, expected_content_selector=selector)

    assert result is False
    mock_page.query_selector.assert_called_once_with(selector)


@pytest.mark.asyncio
async def test_detect_expected_content_no_selector(mock_page):
    """ Test expected content detection with no selector provided """
    result = await detect_expected_content(mock_page, expected_content_selector=None)

    assert result is False
    mock_page.query_selector.assert_not_called()


@pytest.mark.asyncio
async def test_detect_expected_content_with_frame(mock_frame):
    """ Test expected content detection with Frame object """
    mock_frame.query_selector.return_value = AsyncMock()
    selector = ".main-content"

    result = await detect_expected_content(mock_frame, expected_content_selector=selector)

    assert result is True
    mock_frame.query_selector.assert_called_once_with(selector)
