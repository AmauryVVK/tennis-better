import datetime as dt
import time
import typing as T

from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

from tennis_better import logger

today = dt.datetime.today().date()


def get_tennis_match_urls(date: dt.datetime) -> T.List[str]:
    """
    Scrape the 'livescore.com' website to extract the urls of all ATP matches played on 'date'

    Args:
        date (date): The date matches were played

    Returns:
        A list of str, containing the url of all played matches
    """

    if date < today:
        url = f"https://www.livescore.com/en/tennis/{date.strftime('%Y-%m-%d')}/"
    else:
        url = "https://www.livescore.com/en/tennis/"
    logger.debug(f"Fetching matches from {url}")

    with Stealth().use_sync(sync_playwright()) as p:
        # Launch a browser in the background
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load the page
        page.goto(url, wait_until="domcontentloaded")

        try:
            logger.info(f"Waiting for match links to render from {url} ...")

            # Urls are inside <div id="content" class="u tennis v header-scores">
            container = page.locator("#content[class*='header-scores']")
            container.wait_for(state="visible", timeout=20000)

            # Scroll progressively down the page
            match_urls = set()
            last_height = 0
            while True:
                # Find urls inside the container
                # Search for anchor <a> with attributes href: "/en/tennis/atp-" and "-vs-"
                # Model url: https://www.livescore.com/en/tennis/atp-500/qatar-open-doha/carlos-alcaraz-vs-andrey-rublev/1741553/
                hrefs = container.locator(
                    "a[href*='/en/tennis/atp-'][href*='-vs-']"
                ).evaluate_all("elements => elements.map(e => e.href)")
                match_urls.update(hrefs)

                # Scroll by 1000 pixels and check bottom of the page is reached
                page.mouse.wheel(0, 1000)
                time.sleep(1)
                new_height = page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

        except Exception as error:
            # Take a screenshot to look at the error page
            page.screenshot(path="error_state.png")
            logger.error("Failed to extract match urls. Check 'error_state.png'.")
            raise error

        browser.close()

    return match_urls
