import asyncio
import logging

from camoufox import AsyncCamoufox

from camoufox_captcha import solve_captcha

logging.basicConfig(
    level='INFO',
    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)


async def solve_turnstile() -> None:
    async with AsyncCamoufox(
            headless=True,
            geoip=True,
            humanize=False,
            i_know_what_im_doing=True,
            config={'forceScopeAccess': True},  # add this when creating Camoufox instance
            disable_coop=True  # add this when creating Camoufox instance
    ) as browser:
        page = await browser.new_page()

        await page.goto('https://nopecha.com/demo/turnstile')

        # wait for the page to load completely (could be replaced with a more robust check in a real scenario)
        await asyncio.sleep(5)

        # search for the element that contains the turnstile challenge (shadow DOM)
        turnstile_container = await page.wait_for_selector('.turnstile_container')
        if not turnstile_container:
            logging.error('Turnstile container not found on the page')
            return

        await solve_captcha(turnstile_container, captcha_type='cloudflare', challenge_type='turnstile')

    logging.info('Finished')


if __name__ == '__main__':
    asyncio.run(solve_turnstile())
