from tennis_better import logger
from tennis_better.atp_scraper import get_player_urls
from tennis_better.odds import get_tennis_odds


def main():
    """Main function"""
    games = get_tennis_odds()
    logger.debug(len(games))

    player_urls = get_player_urls()
    logger.debug(len(player_urls))


if __name__ == "__main__":
    main()
