import logging
from unittest.mock import AsyncMock, patch

import pytest
from playwright.async_api import Frame, ElementHandle

from camoufox_captcha.cloudflare.utils.dom_helpers import get_ready_checkbox


@pytest.fixture
def mock_frames():
    frame1 = AsyncMock(spec=Frame)
    frame1.is_detached.return_value = False

    frame2 = AsyncMock(spec=Frame)
    frame2.is_detached.return_value = False

    return [frame1, frame2]


@pytest.fixture
def mock_checkbox():
    checkbox = AsyncMock(spec=ElementHandle)
    checkbox.is_visible.return_value = True
    return checkbox


@pytest.fixture
def mock_invisible_checkbox():
    checkbox = AsyncMock(spec=ElementHandle)
    checkbox.is_visible.return_value = False
    return checkbox


@pytest.fixture
def mock_detached_frame():
    frame = AsyncMock(spec=Frame)
    frame.is_detached.return_value = True
    return frame


@pytest.mark.asyncio
async def test_get_ready_checkbox_success(mock_frames, mock_checkbox):
    """ Test get_ready_checkbox when checkbox is found and visible """
    with patch('camoufox_captcha.cloudflare.utils.dom_helpers.search_shadow_root_elements',
               AsyncMock(return_value=[mock_checkbox])):
        result = await get_ready_checkbox(mock_frames, delay=0, attempts=1)

        assert result is not None
        assert result[0] == mock_frames[0]  # Frame
        assert result[1] == mock_checkbox  # ElementHandle


@pytest.mark.asyncio
async def test_get_ready_checkbox_invisible(mock_frames, mock_invisible_checkbox):
    """ Test get_ready_checkbox when checkbox is found but not visible """
    with patch('camoufox_captcha.cloudflare.utils.dom_helpers.search_shadow_root_elements',
               AsyncMock(return_value=[mock_invisible_checkbox])):
        result = await get_ready_checkbox(mock_frames, delay=0, attempts=1)

        assert result is None


@pytest.mark.asyncio
async def test_get_ready_checkbox_not_found(mock_frames):
    """ Test get_ready_checkbox when no checkbox is found """
    with patch('camoufox_captcha.cloudflare.utils.dom_helpers.search_shadow_root_elements',
               AsyncMock(return_value=[])):
        with patch('camoufox_captcha.cloudflare.utils.dom_helpers.asyncio.sleep', AsyncMock()):
            result = await get_ready_checkbox(mock_frames, delay=0, attempts=1)

            assert result is None


@pytest.mark.asyncio
async def test_get_ready_checkbox_multiple_attempts(mock_frames, mock_checkbox):
    """ Test get_ready_checkbox with multiple attempts to find checkbox """

    # track call count to simulate finding checkbox on second attempt
    call_count = 0

    async def search_side_effect(frame, *args, **kwargs):
        nonlocal call_count
        call_count += 1

        # 2 frames, 2 attempts

        # first attempt - no checkboxes in either frame
        if call_count <= 2:
            return []
        # second attempt, first frame - find checkbox
        elif call_count == 3:
            return [mock_checkbox]
        # second attempt, second frame - no checkbox
        else:
            return []

    with patch('camoufox_captcha.cloudflare.utils.dom_helpers.search_shadow_root_elements',
               AsyncMock(side_effect=search_side_effect)):
        with patch('camoufox_captcha.cloudflare.utils.dom_helpers.asyncio.sleep', AsyncMock()):
            result = await get_ready_checkbox(mock_frames, delay=0, attempts=2)

            assert result is not None
            assert result[0] == mock_frames[0]
            assert result[1] == mock_checkbox
            assert call_count == 4


@pytest.mark.asyncio
async def test_get_ready_checkbox_detached_frame(mock_detached_frame, mock_frames, mock_checkbox):
    """ Test get_ready_checkbox with detached frame """
    frames = [mock_detached_frame] + mock_frames

    # we want to only return checkbox for non-detached frame
    async def mock_search(frame, *args, **kwargs):
        return [mock_checkbox] if frame != mock_detached_frame else []

    with patch('camoufox_captcha.cloudflare.utils.dom_helpers.search_shadow_root_elements',
               AsyncMock(side_effect=mock_search)):
        result = await get_ready_checkbox(frames, delay=0, attempts=1)

        assert result is not None
        assert result[0] == mock_frames[0]  # should skip detached frame
        assert result[1] == mock_checkbox


@pytest.mark.asyncio
async def test_get_ready_checkbox_search_exception(mock_frames, caplog):
    """ Test get_ready_checkbox when search_shadow_root_elements raises exception """
    with patch('camoufox_captcha.cloudflare.utils.dom_helpers.search_shadow_root_elements',
               AsyncMock(side_effect=Exception("Test exception"))):
        with caplog.at_level(logging.ERROR):
            result = await get_ready_checkbox(mock_frames, delay=0, attempts=1)

            assert result is None
            assert "Error searching for checkboxes in iframe: Test exception" in caplog.text


@pytest.mark.asyncio
async def test_get_ready_checkbox_timeout(mock_frames, caplog):
    """ Test get_ready_checkbox when it times out """
    with patch('camoufox_captcha.cloudflare.utils.dom_helpers.search_shadow_root_elements',
               AsyncMock(return_value=[])):
        with patch('camoufox_captcha.cloudflare.utils.dom_helpers.asyncio.sleep', AsyncMock()):
            with caplog.at_level(logging.ERROR):
                result = await get_ready_checkbox(mock_frames, delay=0, attempts=2)

                assert result is None
                assert "Max attempts reached while waiting for Cloudflare checkbox input" in caplog.text


@pytest.mark.asyncio
async def test_get_ready_checkbox_negative_attempts(mock_frames, mock_checkbox):
    """ Test get_ready_checkbox with negative attempts value (should default to 1) """
    with patch('camoufox_captcha.cloudflare.utils.dom_helpers.search_shadow_root_elements',
               AsyncMock(return_value=[mock_checkbox])):
        result = await get_ready_checkbox(mock_frames, delay=0, attempts=-1)

        assert result is not None
        assert result[0] == mock_frames[0]
        assert result[1] == mock_checkbox


@pytest.mark.asyncio
async def test_get_ready_checkbox_outer_exception(mock_frames, caplog):
    """ Test get_ready_checkbox when checkbox.is_visible() raises an exception """
    # checkbox that raises an exception on is_visible
    error_checkbox = AsyncMock(spec=ElementHandle)
    error_checkbox.is_visible = AsyncMock(side_effect=Exception("Visibility error"))

    with patch('camoufox_captcha.cloudflare.utils.dom_helpers.search_shadow_root_elements',
               AsyncMock(return_value=[error_checkbox])):
        with patch('camoufox_captcha.cloudflare.utils.dom_helpers.asyncio.sleep', AsyncMock()):
            with caplog.at_level(logging.ERROR):
                result = await get_ready_checkbox(mock_frames, delay=0, attempts=2)

                assert result is None
                assert "Error while waiting for checkbox: Visibility error" in caplog.text
