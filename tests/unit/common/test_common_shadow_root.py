import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from playwright.async_api import ElementHandle, Page, Frame

from camoufox_captcha.common.shadow_root import (
    get_shadow_roots,
    search_shadow_root_elements,
    search_shadow_root_iframes,
)


class MockElementHandle:
    def __init__(self, is_element=True, content_frame_detached=False):
        self.is_element = is_element
        self.content_frame_detached = content_frame_detached
        self.evaluate_handle = AsyncMock()
        self.get_property = AsyncMock()
        self.content_frame = AsyncMock()

    def as_element(self):
        return self if self.is_element else None


@pytest.fixture
def mock_page():
    page = AsyncMock(spec=Page)
    handle = AsyncMock()

    # mock properties
    prop1 = MagicMock()
    prop2 = MagicMock()
    props = {"0": prop1, "1": prop2}

    # return values
    handle.get_properties.return_value = props
    page.evaluate_handle.return_value = handle

    # mock element handles
    prop1.as_element.return_value = MockElementHandle()
    prop2.as_element.return_value = MockElementHandle()

    return page


@pytest.fixture
def mock_empty_page():
    page = AsyncMock(spec=Page)
    handle = AsyncMock()

    # return empty properties
    handle.get_properties.return_value = {}
    page.evaluate_handle.return_value = handle

    return page


@pytest.fixture
def mock_frame():
    frame = AsyncMock(spec=Frame)
    handle = AsyncMock()

    # mock properties
    prop1 = MagicMock()
    props = {"0": prop1}

    # return values
    handle.get_properties.return_value = props
    frame.evaluate_handle.return_value = handle

    # mock element handle
    prop1.as_element.return_value = MockElementHandle()

    return frame


@pytest.mark.asyncio
async def test_get_shadow_roots_with_page(mock_page):
    """ Test get_shadow_roots with a Page object containing multiple shadow roots """
    shadow_roots = await get_shadow_roots(mock_page)

    # Verify the JavaScript was evaluated
    mock_page.evaluate_handle.assert_called_once()
    assert len(shadow_roots) == 2
    assert all(isinstance(root, MockElementHandle) for root in shadow_roots)


@pytest.mark.asyncio
async def test_get_shadow_roots_empty(mock_empty_page):
    """ Test get_shadow_roots when no shadow roots are found """
    shadow_roots = await get_shadow_roots(mock_empty_page)

    mock_empty_page.evaluate_handle.assert_called_once()
    assert len(shadow_roots) == 0


@pytest.mark.asyncio
async def test_get_shadow_roots_with_frame(mock_frame):
    """ Test get_shadow_roots with a Frame object """
    shadow_roots = await get_shadow_roots(mock_frame)

    mock_frame.evaluate_handle.assert_called_once()
    assert len(shadow_roots) == 1


@pytest.mark.asyncio
async def test_get_shadow_roots_with_non_element():
    """ Test get_shadow_roots when properties aren't elements """
    element = AsyncMock(spec=ElementHandle)
    handle = AsyncMock()

    # mock property that isn't an element
    prop = MagicMock()
    prop.as_element.return_value = None
    props = {"0": prop}

    # return values
    handle.get_properties.return_value = props
    element.evaluate_handle.return_value = handle

    shadow_roots = await get_shadow_roots(element)

    assert len(shadow_roots) == 0


@pytest.mark.asyncio
async def test_search_shadow_root_elements_success():
    """ Test search_shadow_root_elements when elements are found """
    page = AsyncMock(spec=Page)
    shadow_root = MockElementHandle()

    # mock element that will be found
    found_element = MockElementHandle()

    # configure the mocks
    with patch('camoufox_captcha.common.shadow_root.get_shadow_roots',
               AsyncMock(return_value=[shadow_root])):
        shadow_root.evaluate_handle.return_value = found_element

        elements = await search_shadow_root_elements(page, '.button')

        assert len(elements) == 1
        assert elements[0] is found_element


@pytest.mark.asyncio
async def test_search_shadow_root_elements_no_elements():
    """ Test search_shadow_root_elements when no elements are found """
    page = AsyncMock(spec=Page)
    shadow_root = MockElementHandle()

    # setup mock to return non-element
    found_handle = MockElementHandle(is_element=False)

    # configure the mocks
    with patch('camoufox_captcha.common.shadow_root.get_shadow_roots',
               AsyncMock(return_value=[shadow_root])):
        shadow_root.evaluate_handle.return_value = found_handle

        elements = await search_shadow_root_elements(page, '.non-existent')

        assert len(elements) == 0


@pytest.mark.asyncio
async def test_search_shadow_root_elements_with_exception(caplog):
    """ Test search_shadow_root_elements when an exception occurs """
    page = AsyncMock(spec=Page)

    # configure the mock to raise an exception
    with patch('camoufox_captcha.common.shadow_root.get_shadow_roots',
               AsyncMock(side_effect=Exception("Test error"))):
        with caplog.at_level(logging.ERROR):
            elements = await search_shadow_root_elements(page, '.button')

            assert len(elements) == 0
            assert "Error searching for elements: Test error" in caplog.text


@pytest.mark.asyncio
async def test_search_shadow_root_iframes():
    """ Test search_shadow_root_iframes when iframes are found """
    page = AsyncMock(spec=Page)
    iframe_element = MockElementHandle()

    # mock the src property
    src_prop = AsyncMock()
    src_prop.json_value.return_value = "https://example.com/iframe"
    iframe_element.get_property.return_value = src_prop

    # mock the content frame
    mock_frame = AsyncMock(spec=Frame)
    mock_frame.is_detached.return_value = False
    iframe_element.content_frame.return_value = mock_frame

    # configure the search_shadow_root_elements mock
    with patch('camoufox_captcha.common.shadow_root.search_shadow_root_elements',
               AsyncMock(return_value=[iframe_element])):
        frames = await search_shadow_root_iframes(page, "example.com")

        assert frames is not None
        assert len(frames) == 1
        assert frames[0] is mock_frame


@pytest.mark.asyncio
async def test_search_shadow_root_iframes_no_match():
    """ Test search_shadow_root_iframes when no iframes match the filter """
    page = AsyncMock(spec=Page)
    iframe_element = MockElementHandle()

    # mock the src property with non-matching value
    src_prop = AsyncMock()
    src_prop.json_value.return_value = "https://other-domain.com/iframe"
    iframe_element.get_property.return_value = src_prop

    # configure the search_shadow_root_elements mock
    with patch('camoufox_captcha.common.shadow_root.search_shadow_root_elements',
               AsyncMock(return_value=[iframe_element])):
        frames = await search_shadow_root_iframes(page, "example.com")

        assert frames is not None
        assert len(frames) == 0


@pytest.mark.asyncio
async def test_search_shadow_root_iframes_detached():
    """ Test search_shadow_root_iframes with detached iframes """
    page = AsyncMock(spec=Page)
    iframe_element = MockElementHandle()

    # mock the src property
    src_prop = AsyncMock()
    src_prop.json_value.return_value = "https://example.com/iframe"
    iframe_element.get_property.return_value = src_prop

    # mock detached content frame
    mock_frame = AsyncMock(spec=Frame)
    mock_frame.is_detached.return_value = True
    iframe_element.content_frame.return_value = mock_frame

    # configure the search_shadow_root_elements mock
    with patch('camoufox_captcha.common.shadow_root.search_shadow_root_elements',
               AsyncMock(return_value=[iframe_element])):
        frames = await search_shadow_root_iframes(page, "example.com")

        assert frames is not None

    assert len(frames) == 0


@pytest.mark.asyncio
async def test_search_shadow_root_elements_null_element():
    """ Test search_shadow_root_elements when element_handle is None/false """
    page = AsyncMock(spec=Page)
    shadow_root = AsyncMock()

    shadow_root.evaluate_handle.return_value = None

    with patch('camoufox_captcha.common.shadow_root.get_shadow_roots',
               AsyncMock(return_value=[shadow_root])):
        elements = await search_shadow_root_elements(page, '.button')

        assert len(elements) == 0
        # verify evaluate_handle was called even though result was None
        shadow_root.evaluate_handle.assert_called_once()


@pytest.mark.asyncio
async def test_search_shadow_root_iframes_exception(caplog):
    """ Test search_shadow_root_iframes when search_shadow_root_elements raises an exception """
    page = AsyncMock(spec=Page)

    with patch('camoufox_captcha.common.shadow_root.search_shadow_root_elements',
               AsyncMock(side_effect=Exception("Iframe search error"))):
        with caplog.at_level(logging.ERROR):
            frames = await search_shadow_root_iframes(page, "example.com")

            assert len(frames) == 0
            assert "Error searching for iframes: Iframe search error" in caplog.text
