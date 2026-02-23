import os
from pathlib import Path

from dotenv import load_dotenv
import duckdb

load_dotenv()
db_players = os.getenv("DATABASE_PLAYER_URLS")

root = Path(__file__).parent.parent


def main():
    """Main function"""

    with duckdb.connect(root / db_players) as con:
        con.sql("CREATE OR REPLACE TABLE players (name VARCHAR, url VARCHAR)")


if __name__ == "__main__":
    main()
