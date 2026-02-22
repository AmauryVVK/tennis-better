import typing as T

from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

from tennis_better import logger


def get_player_urls() -> T.List[str]:
    """
    Scrape the 'atptour.com' website to extract the urls of all players of the top 300

    Returns:
        A list of str, containing the url of all tennis players
    """

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

            # Urls are inside <div id="content" class="u tennis v header-scores">
            container = page.locator("[class='atp_rankings-all']")
            container.wait_for(state="visible", timeout=20000)

            # Find urls inside the container
            # Search for anchor <a> with attributes href: "/en/players/" and "overview"
            # Model url: https://www.atptour.com/en/players/carlos-alcaraz/a0e2/overview
            player_urls = container.locator(
                "a[href*='/en/players/'][href*='overview']"
            ).evaluate_all("elements => elements.map(e => e.href)")
            logger.info(f"Found {len(player_urls)} player links")

        except Exception as error:
            # Take a screenshot to look at the error page
            page.screenshot(path="error_state.png")
            logger.error("Failed to extract player links. Check 'error_state.png'.")
            raise error

        browser.close()

    return player_urls
