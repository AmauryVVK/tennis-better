from tennis_better import logger
from tennis_better.odds import get_tennis_games

import json


def main():
    """Main function"""
    games = get_tennis_games()
    logger.info(json.dumps(games, indent=4))


if __name__ == "__main__":
    main()
