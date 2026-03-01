import datetime as dt
import dateutil
import functools
import os
from pathlib import Path
import re
import typing as T

from dotenv import load_dotenv
import duckdb
import pandas as pd
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

from tennis_better import logger, root_folder, dict_db_paths

load_dotenv()
db_players = os.getenv("DATABASE_PLAYER_URLS")
motherduck_token = os.getenv("MOTHERDUCK_TOKEN")

root = Path(root_folder)


def db_cache(
    table_name: str,
    force_update: bool = False,
    timedelta: dt.timedelta = None,
    on_new_week: bool = False,
):
    """Read and store ouput of function to database

    Arguments:
        table_name (str): The name of the table in the database
        force_update (bool)
        timedelta (datetime.timedelta): The max allowed gap before the table is considered as expired
        on_new_week (bool): whether the gap is expressed as being in another week.

    Returns:
        A decorator
    """

    def db_cache_decorator(func):
        @functools.wraps(func)
        def db_cache_wrapper(*args, **kwargs):

            with duckdb.connect(dict_db_paths["player_urls"]) as conn:
                # If table exists and is not expired, return existing table
                table_exists = (
                    conn.execute(
                        f"SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table_name}'"
                    )
                    .df()
                    .size
                    == 1
                )
                if not force_update and table_exists:
                    created_at = next(
                        iter(
                            conn.execute(
                                f"SELECT MAX(created_at) FROM {table_name}"
                            ).fetchone()
                        )
                    )
                    created_at = dateutil.parser.parse(created_at)
                    if (
                        on_new_week
                        and dt.datetime.now().isocalendar().week
                        == created_at.isocalendar().week
                    ):
                        logger.debug(f"Recycling {table_name} ")
                        return conn.execute(f"SELECT * FROM {table_name}").df()
                    if not on_new_week and dt.datetime.now() - created_at < timedelta:
                        logger.debug(f"Recycling {table_name} ")
                        return conn.execute(f"SELECT * FROM {table_name}").df()

                # Main function
                output = func(*args, **kwargs)

                # Store output to database
                conn.sql(
                    f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM output"
                )

            return output

        return db_cache_wrapper

    return db_cache_decorator


def _is_valid_name(text: str) -> bool:
    """Check whether a string is a valid name, i.e. containing only letters, white spaces, dashes or apostrophes"""
    pattern = r"^[a-zA-Z\s\-\']+$"
    return bool(re.match(pattern, text))


@db_cache("player_urls", on_new_week=True)
def get_player_urls() -> T.List[dict]:
    """
    Scrape the 'atptour.com' website to extract the urls of all players of the top 300

    Returns:
        A list of dict, containing the name and url of all tennis players
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
            data = container.locator(
                "a[href*='/en/players/'][href*='overview']"
            ).evaluate_all("""
                           elements => elements.map(e => ({
                               name: e.innerText.trim(),
                               url: e.href
                           }))
                           """)

        except Exception as error:
            # Take a screenshot to look at the error page
            page.screenshot(path="error_state.png")
            logger.error("Failed to extract player links. Check 'error_state.png'.")
            raise error

        browser.close()

    # Drop duplicates
    seen_names = set()
    player_links = []

    for d in data:
        if d["name"] not in seen_names and _is_valid_name(d["name"]):
            player_links.append(d)
            seen_names.add(d["name"])

    logger.info(f"Found {len(player_links)} player links")

    df_players = pd.DataFrame(player_links)

    df_players["created_at"] = dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    return df_players
