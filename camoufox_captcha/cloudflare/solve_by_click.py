import asyncio
import logging
from typing import Optional, Union, Literal

from playwright.async_api import Page, ElementHandle, Frame

from camoufox_captcha.cloudflare.utils.detection import detect_cloudflare_challenge
from camoufox_captcha.cloudflare.utils.dom_helpers import get_ready_checkbox
from camoufox_captcha.common.detection import detect_expected_content
from camoufox_captcha.common.shadow_root import search_shadow_root_iframes, search_shadow_root_elements

logger = logging.getLogger("camoufox_captcha.cloudflare")


async def solve_cloudflare_by_click(
        queryable: Union[Page, Frame, ElementHandle],
        challenge_type: Literal["interstitial", "turnstile"] = "interstitial",
        expected_content_selector: Optional[str] = None,
        solve_attempts: int = 3,
        solve_click_delay: int = 6,
        wait_checkbox_attempts: int = 10,
        wait_checkbox_delay: int = 6,
        checkbox_click_attempts: int = 3,
        attempt_delay: int = 5
) -> bool:
    """
    Solve Cloudflare challenge by searching for & clicking the checkbox input

    :param queryable: Page, Frame, ElementHandle
    :param challenge_type: Type of Cloudflare challenge: "interstitial" or "turnstile"
    :param expected_content_selector: Optional CSS selector to verify page content is accessible after solving
    :param solve_attempts: Maximum number of attempts to solve the Cloudflare challenge
    :param solve_click_delay: Delay after clicking the checkbox to allow Cloudflare to process the click
    :param wait_checkbox_attempts: Maximum number of attempts to find the checkbox and wait for it to be ready
    :param wait_checkbox_delay: Delay between wait_checkbox_attempts in seconds to find the checkbox and wait for it to be ready
    :param checkbox_click_attempts: Maximum number of attempts to click the checkbox
    :param attempt_delay: Delay between solve attempts in seconds
    :return: True if solved, False otherwise
    """

    logger.info(f'Starting Cloudflare {challenge_type} challenge solving by click...')

    for attempt in range(solve_attempts):
        if attempt > 0:
            await asyncio.sleep(attempt_delay)

            logger.warning(f'Retrying to solve ({attempt + 1}/{solve_attempts})...')

        # 1. check if Cloudflare challenge is present
        cloudflare_detected = await detect_cloudflare_challenge(queryable, challenge_type)
        expected_content_detected = await detect_expected_content(queryable, expected_content_selector)
        if not cloudflare_detected or expected_content_detected:
            logger.info('No Cloudflare challenge detected')
            return True

        # 2. find Cloudflare iframes
        cf_iframes = await search_shadow_root_iframes(
            queryable, 'https://challenges.cloudflare.com/cdn-cgi/challenge-platform/'
        )
        if not cf_iframes:
            logger.error(f'Cloudflare iframes not found')
            continue

        # 3. in all found iframes, search for the valid checkbox input and wait until it's ready to be clicked
        checkbox_data = await get_ready_checkbox(cf_iframes,
                                                 delay=wait_checkbox_delay,
                                                 attempts=wait_checkbox_attempts)
        if not checkbox_data:
            logger.error(f'Cloudflare checkbox not found or not ready')
            continue
        iframe, checkbox = checkbox_data

        logger.info('Found checkbox in Cloudflare iframe')

        # 4. click the checkbox
        for checkbox_click_attempt in range(checkbox_click_attempts):
            try:
                await checkbox.click()
                logger.info('Checkbox clicked successfully')

                break
            except Exception as e:
                logger.error(
                    f'Error clicking checkbox ({checkbox_click_attempt + 1}/{checkbox_click_attempts} attempt): {e}')
        else:
            logger.error(
                f'Failed to click checkbox after maximum attempts')
            continue

        # wait for Cloudflare to process the click
        await asyncio.sleep(solve_click_delay)

        # 5. verify success
        if challenge_type == "turnstile":
            # for turnstile, check for success element in the cf's iframe or expected content is present
            success_elements = await search_shadow_root_elements(iframe, 'div[id="success"]')
            challenge_solved = bool(success_elements)
        else:
            # for interstitial, check if challenge is gone or expected content is present
            cloudflare_detected = await detect_cloudflare_challenge(queryable)
            challenge_solved = not cloudflare_detected

        expected_content_detected = await detect_expected_content(queryable, expected_content_selector)
        if challenge_solved or expected_content_detected:
            logger.info('Solved successfully')
            return True

        logger.warning('Failed to solve Cloudflare challenge')

    logger.error('Max solving attempts reached, giving up')
    return False
