from typing import Optional, Union

from playwright.async_api import ElementHandle, Frame, Page


async def detect_expected_content(
        queryable: Union[Page, Frame, ElementHandle],
        expected_content_selector: Optional[str] = None
) -> bool:
    """
    Check if the expected content is present in the page

    :param queryable: Page, Frame, ElementHandle
    :param expected_content_selector: CSS selector for the expected content
    :return: True if expected content is found, False otherwise
    """

    if not expected_content_selector:
        return False

    element = await queryable.query_selector(expected_content_selector)
    return bool(element)
