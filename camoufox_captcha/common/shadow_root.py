import logging
from typing import Union, List, Optional

from playwright.async_api import ElementHandle, Page, Frame

logger = logging.getLogger("camoufox_captcha.common")


async def get_shadow_roots(
        queryable: Union[Page, Frame, ElementHandle],
) -> List[ElementHandle]:
    """
    Get all shadow roots on the page

    :param queryable: Page, Frame, ElementHandle
    :return: List of shadow roots ElementHandles
    """

    # script to collect all shadow roots
    js = """
    () => {
        const roots = [];

        function collectShadowRoots(node) {
            if (!node) return;

            if (node.shadowRootUnl) {
                roots.push(node.shadowRootUnl);
                node = node.shadowRootUnl;
            }

            for (const el of node.querySelectorAll("*")) {
                if (el.shadowRootUnl) {
                    collectShadowRoots(el);
                }
            }
        }

        collectShadowRoots(document);
        console.log(roots);
        return roots;
    }
    """

    handle = await queryable.evaluate_handle(js)

    # convert JSHandle array to python list of ElementHandle
    properties = await handle.get_properties()

    shadow_roots = []
    for prop_handle in properties.values():
        element = prop_handle.as_element()
        if element:
            shadow_roots.append(element)

    return shadow_roots


async def search_shadow_root_elements(
        queryable: Union[Page, Frame, ElementHandle],
        selector: str
) -> List[ElementHandle]:
    """
    Search for elements by selector within the shadow DOM of the queryable object

    :param queryable: Page, Frame, ElementHandle
    :param selector: CSS selector to search for elements
    :return: List of ElementHandles that match the selector
    """

    elements = []

    try:
        shadow_roots = await get_shadow_roots(queryable)  # get all shadow roots in the queryable object
        for shadow_root in shadow_roots:
            # find all elements by selector within the shadow root
            element_handle = await shadow_root.evaluate_handle(
                f"shadow => shadow.querySelector('{selector}')"
            )
            if not element_handle:
                continue

            element = element_handle.as_element()
            if element:
                elements.append(element)
    except Exception as e:
        logger.error(f'Error searching for elements: {e}')

    return elements


async def search_shadow_root_iframes(
        queryable: Union[Page, Frame, ElementHandle],
        src_filter: str
) -> Optional[List[Frame]]:
    """
    Search for an iframe within the shadow DOM, src of which includes the src_filter

    :param queryable: Page, Frame, ElementHandle
    :param src_filter: String to filter the iframe's src attribute
    :return: list of matched iframes or empty list if no iframes found
    """

    matched_iframes = []

    try:
        iframe_elements = await search_shadow_root_elements(queryable, 'iframe')
        for iframe_element in iframe_elements:
            src_prop = await iframe_element.get_property('src')
            src = await src_prop.json_value()

            if src_filter in src:
                cf_iframe = await iframe_element.content_frame()
                if cf_iframe and cf_iframe.is_detached():  # skip detached iframes
                    continue

                matched_iframes.append(cf_iframe)
    except Exception as e:
        logger.error(f'Error searching for iframes: {e}')

    return matched_iframes
