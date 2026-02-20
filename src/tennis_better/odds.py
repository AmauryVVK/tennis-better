"""
Functions for extracting odds from the-odds-api, a sports bettings API
API documentation at https://the-odds-api.com/liveapi/guides/v4/
Python code samples: https://github.com/the-odds-api/samples-python/tree/master
"""

import os
import typing as T

import requests
from dotenv import load_dotenv

from tennis_better import logger

load_dotenv()
api_key = os.getenv("ODDS_API_TOKEN")


def get_sports() -> T.List[dict]:
    """Get list of available sports

    Returns:
        A list of sport dicts
    """
    base_url = "https://api.the-odds-api.com/v4/sports/"
    params = {"apiKey": api_key}

    response = requests.get(base_url, params=params)

    if not response.ok:
        logger.error(response.text)
        response.raise_for_status()

    return response.json()


def get_events(sport: str) -> T.List[dict]:
    """Get events for a specific sport key

    Args:
        sport (str): The sport key to get events from.

    Returns:
        A list of dicts, describing sport events
    """
    base_url = f"https://api.the-odds-api.com/v4/sports/{sport}/events/"
    params = {"apiKey": api_key}

    response = requests.get(base_url, params=params)

    if not response.ok:
        logger.error(response.text)
        response.raise_for_status()

    return response.json()


def get_odds(sport: str, event_id: str, regions: str) -> dict:
    """Get odds for a specific event

    Args:
        sport (str): The sport key
        event_id (str): The id of the event or game
        regions (str): The regions of bookmakers. Multiple regions can be specified if comma delimited (see https://the-odds-api.com/sports-odds-data/bookmaker-apis.html#us-bookmakers)

    Returns:
        A dict describing the event and the h2h odds from all bookmakers of regions
    """
    base_url = f"https://api.the-odds-api.com/v4/sports/{sport}/events/{event_id}/odds"
    params = {
        "apiKey": api_key,
        "regions": regions,
        "markets": "h2h",
        "oddsFormat": "decimal",
        "dateFormat": "iso",
    }

    response = requests.get(base_url, params=params)

    if not response.ok:
        logger.error(response.text)
        response.raise_for_status()

    return response.json()


def get_tennis_odds() -> T.List[dict]:
    """
    Get all tennis matches and their odds from all available French bookmakers

    Returns:
        A list of dict
    """
    list_odds: T.List[dict] = []

    sports = get_sports()
    tennis_keys = [
        sport["key"] for sport in sports if sport["key"].startswith("tennis_atp")
    ]

    for key in tennis_keys:
        matches = get_events(key)
        for match in matches:
            odds = get_odds(key, match["id"], regions="fr")
            for bookmk in odds["bookmakers"]:
                bookmk_odds = {
                    "tournament": odds["sport_title"],
                    "commence_time": odds["commence_time"],
                    "player_1": bookmk["markets"][0]["outcomes"][0]["name"],
                    "odds_1": bookmk["markets"][0]["outcomes"][0]["price"],
                    "player_2": bookmk["markets"][0]["outcomes"][1]["name"],
                    "odds_2": bookmk["markets"][0]["outcomes"][1]["price"],
                    "bookmaker": bookmk["title"],
                }
                list_odds.append(bookmk_odds)

    logger.info(f"Found {len(matches)} tennis matches and {len(list_odds)} odds")

    return list_odds
