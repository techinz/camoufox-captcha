"""
Camoufox Captcha - Automatically solve captcha using Camoufox
"""
import logging
from typing import Union, Literal, Optional

from playwright.async_api import Page, Frame, ElementHandle

from .cloudflare import solve_cloudflare_by_click

logging.getLogger("camoufox_captcha").addHandler(logging.NullHandler())


async def solve_captcha(
        queryable: Union[Page, Frame, ElementHandle],
        captcha_type: Literal["cloudflare"] = "cloudflare",
        challenge_type: Literal["interstitial", "turnstile"] = "interstitial",
        method: Optional[str] = None,
        **kwargs
) -> bool:
    """
    Universal captcha solving function

    This function provides a unified interface for solving different types of captcha
    Currently supports Cloudflare challenges, with more providers planned for future releases

    Args:
        queryable: Page, Frame or ElementHandle containing the captcha
        captcha_type: Type of captcha provider ("cloudflare", future: "hcaptcha", "recaptcha", etc.)
        challenge_type: Type of challenge specific to the captcha provider:
                       - For "cloudflare": "interstitial" or "turnstile" (defaults to "interstitial")
        method: Solving method (defaults to the best available method for the captcha type)
        **kwargs: Additional parameters passed to the specific solver function
        
    Returns:
        bool: True if captcha was successfully solved, False otherwise
        
    Example:
        ```python
        # simple usage with defaults
        success = await solve_captcha(page, captcha_type="cloudflare", challenge_type="interstitial")

        # with additional parameters
        success = await solve_captcha(
            page,
            captcha_type="cloudflare",
            challenge_type="interstitial",
            expected_content_selector="#main-content", 
            solve_attempts=3,
            solve_click_delay=6,
            wait_checkbox_attempts=10,
            wait_checkbox_delay=6,
            checkbox_click_attempts=3
            attempt_delay=5
        )
        ```
    """

    if captcha_type == "cloudflare":
        challenge_type: Literal["interstitial", "turnstile"]

        if not challenge_type:
            challenge_type = "interstitial"

        if challenge_type not in ("turnstile", "interstitial"):
            raise ValueError(
                f"Unsupported Cloudflare challenge type: '{challenge_type}'. "
                f"Supported types are: 'interstitial' or 'turnstile'"
            )

        if method in (None, 'click'):
            return await solve_cloudflare_by_click(
                queryable,
                challenge_type=challenge_type,
                **kwargs
            )

        raise ValueError(
            f"Unsupported method '{method}' for Cloudflare captcha. "
            f"Currently only 'click' method is supported."
        )

    raise ValueError(
        f"Unsupported captcha type: '{captcha_type}'. "
        f"Currently only 'cloudflare' is supported."
    )


__all__ = ['solve_captcha', 'solve_cloudflare_by_click']
