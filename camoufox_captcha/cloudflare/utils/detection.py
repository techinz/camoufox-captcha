from typing import Literal, Union

from playwright.async_api import ElementHandle, Frame, Page

# selectors for detecting Cloudflare interstitial challenge (page)
CF_INTERSTITIAL_INDICATORS_SELECTORS = [
    'script[src*="/cdn-cgi/challenge-platform/"]',
]

# selectors for detecting Cloudflare turnstile challenge (small embedded captcha)
CF_TURNSTILE_INDICATORS_SELECTORS = [
    'input[name="cf-turnstile-response"]',
    'script[src*="challenges.cloudflare.com/turnstile/v0"]',
]


async def detect_cloudflare_challenge(
        queryable: Union[Page, Frame, ElementHandle],
        challenge_type: Literal['turnstile', 'interstitial'] = 'turnstile'
) -> bool:
    """
    Detect if a Cloudflare challenge is present in the provided queryable object by checking for specific predefined selectors

    :param queryable: Page, Frame, ElementHandle
    :param challenge_type: Type of challenge to detect ('turnstile' or 'interstitial')
    :return: True if Cloudflare challenge is detected, False otherwise
    """

    selectors = CF_TURNSTILE_INDICATORS_SELECTORS if challenge_type == 'turnstile' else CF_INTERSTITIAL_INDICATORS_SELECTORS
    for selector in selectors:
        element = await queryable.query_selector(selector)
        if not element:
            continue
        return True

    return False
