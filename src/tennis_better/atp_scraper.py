from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

from tennis_better import logger


def get_player_urls():

    # Url for top 300 players
    url = "https://www.atptour.com/en/rankings/singles?rankRange=0-300"

    with Stealth().use_sync(sync_playwright()) as p:
        # Launch a browser in the background
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load the page
        page.goto(url, wait_until="domcontentloaded")

        try:
            logger.info(f"Waiting for player links to render from {url} ...")

            # Search for anchor <a> with attribute href "/en/players/"
            # Model url: https://www.atptour.com/en/players/carlos-alcaraz/a0e2/overview
            page.wait_for_selector('a[href*="/en/players/"]', timeout=15000)
            hrefs = page.eval_on_selector_all(
                'a[href*="/en/players/"]', "elements => elements.map(e => e.href)"
            )

            # Clean and deduplicate (only keep 'overview' pages)
            player_urls = {link for link in hrefs if "/overview" in link}
            logger.info(f"Found {len(player_urls)} player links")

        except Exception as error:
            # If it fails, take a screenshot to look at the error page
            page.screenshot(path="error_state.png")
            logger.error("Failed to find player links. Check 'error_state.png'.")
            raise error

        browser.close()

    return player_urls
