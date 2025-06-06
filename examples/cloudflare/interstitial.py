import asyncio
import logging

from camoufox import AsyncCamoufox

from camoufox_captcha import solve_captcha

logging.basicConfig(
    level='INFO',
    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)


async def solve_interstitial() -> None:
    async with AsyncCamoufox(
            headless=True,
            geoip=True,
            humanize=False,
            i_know_what_im_doing=True,
            config={'forceScopeAccess': True},  # add this when creating Camoufox instance
            disable_coop=True,  # add this when creating Camoufox instance
    ) as browser:
        page = await browser.new_page()

        await page.goto('https://nopecha.com/demo/cloudflare')

        # wait for the page to load completely (could be replaced with a more robust check in a real scenario)
        await asyncio.sleep(5)

        await solve_captcha(page, captcha_type='cloudflare', challenge_type='interstitial')

    logging.info('Finished')


if __name__ == '__main__':
    asyncio.run(solve_interstitial())
