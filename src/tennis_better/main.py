from tennis_better import logger
from tennis_better.atp_scraper import get_player_urls
from tennis_better.livescore_scraper import get_tennis_match_urls
from tennis_better.odds import get_tennis_odds

import datetime as dt


def main():
    """Main function"""
    games = get_tennis_odds()
    logger.debug(games)

    player_urls = get_player_urls()
    logger.debug(len(player_urls))

    match_urls = get_tennis_match_urls(
        dt.datetime.today().date() - dt.timedelta(days=1)
    )
    for url in match_urls:
        logger.debug(url)


if __name__ == "__main__":
    main()
