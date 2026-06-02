from pathlib import Path

# Base URL used for all downloads
BASE_URL = "https://dbpatsz.hu/leagues.php"

# Target league identifier
LEAGUE_ID = "57"
# Target team identifier
TEAM_ID = "1"
# Season rounds to process
ROUNDS = range(1, 31)

# Directory for downloaded HTML files
RAW_DIR = Path("data/raw")
# Directory for processed CSV outputs
PROCESSED_DIR = Path("data/processed")

# Configuration for each supported page type
PAGE_TYPES = {
    "round-matches": {
        # Page mode parameter
        "mod": "1",
        # Storage folder
        "folder": "round_matches",
        # Output filename pattern
        "filename": "round_{round_number}.html",
        # This page requires authentication cookies
        "cookies_required": True,
    },
    "team-leaderboard": {
        # Page mode parameter
        "mod": "4",
        # Storage folder
        "folder": "team_leaderboard",
        # Output filename pattern
        "filename": "round_{round_number}.html",
        # Public page
        "cookies_required": False,
    },
    "individual-leaderboard": {
        # Page mode parameter
        "mod": "6",
        # Storage folder
        "folder": "individual_leaderboard",
        # Output filename pattern
        "filename": "round_{round_number}.html",
        # Public page
        "cookies_required": False,
    },
}