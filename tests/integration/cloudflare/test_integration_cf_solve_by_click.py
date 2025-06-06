import asyncio

import pytest
from camoufox import AsyncCamoufox

from camoufox_captcha import solve_captcha


@pytest.mark.asyncio
async def test_cloudflare_interstitial_solving():
    """ Test the solving against Cloudflare-protected sites with interstitial challenge mode """

    test_sites = [
        {'url': 'https://nopecha.com/demo/cloudflare', 'expected_content_selector': '#content'},
        {'url': 'https://community.cloudflare.com', 'expected_content_selector': '#main'},
        {'url': 'https://2captcha.com/demo/cloudflare-turnstile-challenge',
         'expected_content_selector': 'text=Captcha is passed successfully!'},
    ]

    async with AsyncCamoufox(
            headless=True,
            geoip=True,
            humanize=False,
            i_know_what_im_doing=True,
            config={'forceScopeAccess': True},
            disable_coop=True
    ) as browser:
        for site in test_sites:
            url = site['url']
            expected_content_selector = site['expected_content_selector']
            page = None

            try:
                print(f"Testing Cloudflare interstitial solving on: {url}")

                page = await browser.new_page()

                await page.goto(url, timeout=60000, wait_until='load')

                await asyncio.sleep(10)  # wait for the page to load completely

                # try to solve Cloudflare interstitial
                success = await solve_captcha(page,
                                              captcha_type='cloudflare',
                                              challenge_type='interstitial',
                                              expected_content_selector=expected_content_selector)

                # verify success and that the site content is accessed
                assert success, f"Failed to solve Cloudflare interstitial on {url}"

                print(f"+ Successfully solved Cloudflare interstitial on {url}")
            except Exception as e:
                pytest.fail(f"Error testing {url}: {str(e)}")
            finally:
                if page:
                    await page.close()


@pytest.mark.asyncio
async def test_cloudflare_turnstile_solving():
    """ Test the solving against Cloudflare-protected sites with turnstile challenge mode """

    test_sites = [
        {'url': 'https://nopecha.com/demo/turnstile', 'search_selector': '.turnstile_container',
         'expected_content_selector': None},
        {'url': 'https://2captcha.com/demo/cloudflare-turnstile', 'search_selector': '#cf-turnstile',
         'expected_content_selector': None}
    ]

    async with AsyncCamoufox(
            headless=True,
            geoip=True,
            humanize=False,
            i_know_what_im_doing=True,
            config={'forceScopeAccess': True},
            disable_coop=True
    ) as browser:
        for site in test_sites:
            url = site['url']
            search_selector = site['search_selector']
            expected_content_selector = site['expected_content_selector']
            page = None

            try:
                print(f"Testing Cloudflare turnstile solving on: {url}")

                page = await browser.new_page()

                await page.goto(url, timeout=60000, wait_until='load')

                await asyncio.sleep(10)  # wait for the page to load completely

                turnstile_container = await page.wait_for_selector(search_selector)
                if not turnstile_container:
                    raise Exception('Turnstile container not found on the page by search_selector')

                # try to solve Cloudflare turnstile
                success = await solve_captcha(turnstile_container,
                                              captcha_type='cloudflare',
                                              challenge_type='turnstile',
                                              expected_content_selector=expected_content_selector)

                # verify success and that the site content is accessed
                assert success, f"Failed to solve Cloudflare turnstile on {url}"

                print(f"+ Successfully solved Cloudflare turnstile on {url}")
            except Exception as e:
                pytest.fail(f"Error testing {url}: {str(e)}")
            finally:
                if page:
                    await page.close()
