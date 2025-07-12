# ⚠️ This project has moved

This repo is no longer maintained. Please use the actively developed version here:

👉 [https://github.com/techinz/playwright-captcha](https://github.com/techinz/playwright-captcha)

# Camoufox Captcha

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen.svg)](https://pytest-cov.readthedocs.io/en/latest/readme.html#acknowledgements)
[![PyPI version](https://img.shields.io/pypi/v/camoufox-captcha.svg)](https://pypi.org/project/camoufox-captcha/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A Python library that extends [Camoufox](https://github.com/daijro/camoufox) to automatically solve captcha challenges. Currently supports only Cloudflare challenges (interstitial and turnstile), with more captcha types planned.

## 📸 Demonstration (recorded in headless mode)

<div align="center">
  <h3>Cloudflare Click Interstitial</h3>

  https://github.com/user-attachments/assets/10ced3fe-044b-4657-b371-155f1e943955

  <details> 
  <summary><h3>Cloudflare Click Turnstile</h3></summary>

  https://github.com/user-attachments/assets/90206e23-ac2f-4e45-a4c4-e1fd7e8f17e3

  </details>
</div>

## ⚠️ LEGAL DISCLAIMER

**THIS TOOL IS PROVIDED FOR EDUCATIONAL AND RESEARCH PURPOSES ONLY**

This software is designed to demonstrate security concepts and should not be used to bypass protections on websites without explicit permission from the website owner. Using this tool against websites without authorization may violate:

- The Computer Fraud and Abuse Act (CFAA)
- Terms of Service agreements
- Various cybersecurity laws in your jurisdiction

The author takes no responsibility for any misuse of this software. Users are solely responsible for ensuring their use complies with all applicable laws and regulations.

## ✨ Features

- **Closed Shadow DOM Traversal**: Navigates complex closed Shadow DOM structures to find and interact with challenge elements
- **Advanced Retry Logic**: Implements retry mechanisms with configurable attempts and delays
- **Verification Steps**: Confirms successful solving through multiple validation methods
- **Fully Tested**: 100% code coverage with unit and integration tests

## 📖 Requirements

This package requires:
- Python 3.8+
- camoufox[geoip] 0.4.11 or higher (must be installed separately)

## 📦 Installation

### From PyPI

```bash
# firstly make sure to have camoufox or install it 
pip install "camoufox[geoip]>=0.4.11"

# install camoufox-captcha
pip install camoufox-captcha
```

### Development Installation

```bash
git clone https://github.com/techinz/camoufox-captcha.git
cd camoufox-captcha
pip install -e ".[dev]"
```

## 👨‍💻 Usage

### ❗️ Important

When creating your Camoufox instance, make sure to include these parameters for the library to work:

```python
AsyncCamoufox(
    # other parameters...
    config={'forceScopeAccess': True},  # required
    disable_coop=True                   # required
)
```

These settings are essential for proper closed Shadow DOM traversal and browser security bypassing required by the captcha solving.


---  


See usage examples in the [/examples](https://github.com/techinz/camoufox-captcha/tree/main/examples) directory for ready-to-use scripts.

### Basic Example (Cloudflare Interstitial)

```python
import asyncio
from camoufox import AsyncCamoufox
from camoufox_captcha import solve_captcha  # import it


async def main():
    async with AsyncCamoufox(
            headless=True,
            geoip=True,
            humanize=False,
            i_know_what_im_doing=True,
            config={'forceScopeAccess': True},  # add this when creating Camoufox instance
            disable_coop=True  # add this when creating Camoufox instance
    ) as browser:
        page = await browser.new_page()

        # navigate to a site with Cloudflare protection
        await page.goto("https://example-with-cloudflare.com")

        # solve using solve_captcha
        success = await solve_captcha(page, captcha_type='cloudflare', challenge_type='interstitial')
        if not success:
            return print("Failed to solve captcha challenge")

        print("Successfully solved captcha challenge!")
        # continue with your automation...


if __name__ == "__main__":
    asyncio.run(main())
```

<details>
<summary>Cloudflare Turnstile Example</summary>

### Cloudflare Turnstile Example

```python
import asyncio
from camoufox import AsyncCamoufox
from camoufox_captcha import solve_captcha  # import it


async def main():
    async with AsyncCamoufox(
            headless=True,
            geoip=True,
            humanize=False,
            i_know_what_im_doing=True,
            config={'forceScopeAccess': True},  # add this when creating Camoufox instance
            disable_coop=True  # add this when creating Camoufox instance
    ) as browser:
        page = await browser.new_page()

        await page.goto("https://site-with-turnstile.com")

        # locate the container with the Turnstile challenge
        turnstile_container = await page.wait_for_selector('.turnstile_container')

        # specify challenge type for Turnstile
        success = await solve_captcha(
            turnstile_container,
            captcha_type="cloudflare",
            challenge_type="turnstile"
        )

        if not success:
            return print("Failed to solve captcha challenge")

        print("Successfully solved captcha challenge!")
        # continue with your automation...


if __name__ == "__main__":
    asyncio.run(main())
```
</details>

### With Content Verification

```python
# specify a CSS selector that should appear after successful bypass
success = await solve_captcha(
    page,
    challenge_type="interstitial",
    expected_content_selector="#super-protected-content"
)
```

## 📚 Configuration Options

The solve_captcha function provides a unified interface with multiple parameters:

```python
await solve_captcha(
    queryable,                       # Page, Frame or ElementHandle containing the captcha
    captcha_type="cloudflare",       # Type of captcha provider (currently only "cloudflare")
    challenge_type="interstitial",   # For Cloudflare: "interstitial" or "turnstile"
    method=None,                     # Solving method (defaults to best available for the captcha type):
                                        # Cloudflare: "click"
    **kwargs                         # Additional parameters passed to the specific solver:
        # Cloudflare click:
            # expected_content_selector=None,  # CSS selector to verify solving success
            # solve_attempts=3,                # Maximum attempts for solving
            # solve_click_delay=2.0,           # Delay after clicking checkbox in seconds
            # checkbox_click_attempts=3,       # Maximum attempts to click the checkbox
            # wait_checkbox_attempts=5,        # Maximum attempts to wait for checkbox readiness
            # wait_checkbox_delay=1.0          # Delay between checkbox readiness checks
)
```

## 🧠 Solving Methods

<details>
<summary>Cloudflare Interstitial Click Method</summary>

### Cloudflare Interstitial Click Method

This method handles Cloudflare's full-page interstitial challenge that appears before accessing protected content.

**How it works:**
1. Detects the Cloudflare challenge page through specific DOM elements
2. Finds all iframes in the page's Shadow DOM tree
3. Searches for the checkbox inside security frames
4. Simulates a user click on the verification checkbox
5. Waits for the page to reload or challenge to disappear
6. Verifies success by checking for expected content or absence of challenge
</details>

<details>
<summary>Cloudflare Turnstile Click Method</summary>

### Cloudflare Turnstile Click Method

This method handles Cloudflare's Turnstile widget that appears embedded within forms or other page elements.

**How it works:**
1. Targets the Turnstile widget container element
2. Finds all iframes in the page's Shadow DOM tree
3. Searches for the checkbox inside security frames
4. Simulates a user click on the verification checkbox
5. Monitors for completion by watching for success state elements
5. Verifies success by checking for expected content or success element in the widget
</details>

## 🧪 Testing

The project has unit and integration tests:

```bash
# run all tests with coverage report
pytest --cov=camoufox_captcha --cov-report=html tests/
    
# run only unit tests
pytest tests/unit/
    
# run only integration tests
pytest tests/integration/
```

## 🔮 Future Development

- Support for additional captcha types (hCaptcha, reCAPTCHA)
- Integration with external solving services (2Captcha, Anti-Captcha, CapMonster) 
- Advanced detection methods for various captcha types
- Image-based captcha solving

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

Please ensure your code passes all tests and maintains or improves test coverage.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/techinz/camoufox-captcha/tree/main/LICENSE) file for details.

---

**Remember**: Use this tool responsibly and only on systems you have permission to test.