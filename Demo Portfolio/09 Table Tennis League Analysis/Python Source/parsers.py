import csv
from pathlib import Path
from bs4 import BeautifulSoup

from config import RAW_DIR, PROCESSED_DIR, ROUNDS
from html_extractors import (
    extract_team_leaderboard,
    extract_individual_leaderboard,
    extract_round_match,
    extract_individual_matches,
)

def write_csv(path: Path, rows: list[dict]) -> None:
    """
    Writes a list of dictionaries to a CSV file. If the specified file path's parent
    directories do not exist, they will be created automatically. If the list of
    rows is empty, the function will log a message and exit without writing.

    :param path: File path where the CSV should be written. This should include
        the filename and extension.
    :type path: Path
    :param rows: List of dictionaries representing the data to be written to the
        CSV. Each dictionary's keys correspond to column headers.
    :type rows: list[dict]
    :return: This function does not return anything.
    :rtype: None
    """
    # Skip writing empty datasets
    if not rows:
        print(f"No rows to write:{path}")
        return

    # Create output directory if needed
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write rows to CSV file
    with open(path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

def read_soup(path: Path) -> BeautifulSoup:
    """
    Reads an HTML or XML file and parses it into a BeautifulSoup object.

    :param path: Path to the file to be read and parsed.
    :type path: Path
    :return: BeautifulSoup object representing the parsed file content.
    :rtype: BeautifulSoup
    """
    # Parse HTML using BeautifulSoup
    with open(path, "rb") as file:
        return BeautifulSoup(file.read(), "html.parser")

def normalize_player_match_results(individual_matches: list[dict]) -> list[dict]:
    """
    Normalizes individual match results by converting them into a more structured format
    where each player's performance in a match is represented as a separate dictionary.
    This allows for easy querying and manipulation of match data at the player level.

    :param individual_matches: A list of dictionaries, each representing data for a particular
        match. The dictionary must contain keys, including "round_number", "round_match_number",
        "home_player", "home_team_name", "away_player", "away_team_name", "home_player_points",
        and "away_player_points".
    :return: A list of dictionaries, each representing the normalized match results for individual
        players. Each dictionary contains keys such as "round_number", "round_match_number",
        "player_name", "team_name", "opponent_player", "opponent_team", "player_points",
        "opponent_points", and "side".
    :rtype: list[dict]
    """
    player_match_results = []

    for match in individual_matches:

        # Add home player's perspective
        player_match_results.append(
            {
                "round_number": match["round_number"],
                "round_match_number": match["round_match_number"],
                "player_name": match["home_player"],
                "team_name": match["home_team_name"],
                "opponent_player": match["away_player"],
                "opponent_team": match["away_team_name"],
                "player_points": match["home_player_points"],
                "opponent_points": match["away_player_points"],
                "side": "Home",
            }
        )

        # Add away player's perspective
        player_match_results.append(
            {
                "round_number": match["round_number"],
                "round_match_number": match["round_match_number"],
                "player_name": match["away_player"],
                "team_name": match["away_team_name"],
                "opponent_player": match["home_player"],
                "opponent_team": match["home_team_name"],
                "player_points": match["away_player_points"],
                "opponent_points": match["home_player_points"],
                "side": "Away",
            }
        )

    return player_match_results

def parse_round_matches() -> None:
    """
    Parses round match data and processes it to generate CSV files for round matches,
    individual matches, and player match results. This function reads raw HTML files
    for rounds, extracts relevant match data and information, and writes the cleaned
    and normalized data into structured CSV outputs.

    :raises FileNotFoundError: If the required HTML files are not found at the specified paths.

    :return: This function does not return anything. It performs actions such as
             reading input files, processing data, and writing output files.
    """
    round_matches = []
    individual_matches = []

    # Process every configured round
    for round_number in ROUNDS:
        path = RAW_DIR / "round_matches" / f"round_{round_number}.html"
        print(f"Parsing {path}...")
        soup = read_soup(path)

        # Locate all match blocks on the page
        match_blocks = soup.select("div.erbx")

        for index, match_block in enumerate(match_blocks):
            header = match_block.select_one("p.ovgr.erhe")
            footer = match_block.select_one("p.ovbu.erft")
            table = match_block.select_one("table.ertb")

            # Extract match-level information
            round_match = extract_round_match(
                header,
                footer,
                round_number,
                index+1
            )
            round_matches.append(round_match)

            # Extract player-level match information
            matches = extract_individual_matches(table, round_match)
            if matches:
                individual_matches.extend(matches)

    # Save round summary dataset
    write_csv(PROCESSED_DIR / "round_matches.csv", round_matches)
    # Save individual match dataset
    write_csv(PROCESSED_DIR / "individual_matches.csv", individual_matches)
    # Save player-centric match dataset
    write_csv(
        PROCESSED_DIR / "player_match_results.csv",
        normalize_player_match_results(individual_matches),
    )

def parse_team_leaderboard() -> None:
    """
    Parses and processes team leaderboard data for multiple rounds, combining information
    from HTML files in a specific directory into a structured format, and saves it as
    a CSV file.

    This function reads HTML files for each round, extracts relevant leaderboard data using
    a helper function, consolidates the data in a list, and writes the final results into
    a CSV file in a specified directory.

    :raises FileNotFoundError: If any of the required HTML files are not found.
    :raises ValueError: If there's an issue with parsing or extracting data from the HTML.
    :return: None
    """
    rows = []

    # Process every round leaderboard
    for round_number in ROUNDS:
        path = RAW_DIR / "team_leaderboard" / f"round_{round_number}.html"
        print(f"Parsing {path}...")

        soup = read_soup(path)

        # Locate leaderboard table
        table = soup.select_one("table#tere")

        # Extract leaderboard rows
        if table:
            rows.extend(extract_team_leaderboard(table, round_number))

    # Save consolidated leaderboard
    write_csv(PROCESSED_DIR / "team_leaderboard.csv", rows)

def parse_individual_leaderboard() -> None:
    """
    Parses individual leaderboard data from HTML files and writes the processed data to a CSV file.
    The function iterates through multiple rounds, extracts relevant table data from HTML files,
    and compiles it into a structured dataset.

    :raises FileNotFoundError: If the specified HTML file does not exist.
    :raises ValueError: If `extract_individual_leaderboard` encounters unexpected table structure.
    """
    rows = []

    # Process every round leaderboard
    for round_number in ROUNDS:
        path = RAW_DIR / "individual_leaderboard" / f"round_{round_number}.html"
        print(f"Parsing {path}...")

        soup = read_soup(path)

        # Locate leaderboard table
        table = soup.select_one("table#tere")

        # Extract leaderboard rows
        if table:
            rows.extend(extract_individual_leaderboard(table, round_number))

    # Save consolidated leaderboard
    write_csv(PROCESSED_DIR / "individual_leaderboard.csv", rows)

def parse_all() -> None:
    """
    Parses all the required data such as team leaderboard, individual leaderboard,
    and round matches by calling their respective parsing functions.

    This function serves as an orchestrator, delegating the task of parsing
    specific data types to their corresponding functions.

    :return: None
    """
    # Parse team standings
    parse_team_leaderboard()
    # Parse player standings
    parse_individual_leaderboard()
    # Parse match results
    parse_round_matches()