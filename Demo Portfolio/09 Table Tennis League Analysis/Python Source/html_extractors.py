from typing import Optional
from bs4 import Tag
from datetime import datetime
import re

def extract_round_match(header, footer, round_number, round_match_number):
    """
    Extracts detailed information about a specific round match, including team names, points, date,
    time, and location. The data is retrieved from the specified HTML header and footer elements
    and returned in a structured dictionary.

    :param header: BeautifulSoup object representing the HTML header that contains match information
    :param footer: BeautifulSoup object representing the HTML footer that contains location details
    :param round_number: Number of the round to which the match belongs
    :param round_match_number: Number of the specific match within the round
    :return: A dictionary containing details of the match, including round numbers, team names,
             team points, match date, time, and location
    :rtype: dict
    """
    # Extract team names from the header
    team_names = header.select_one("span.erc").get_text()
    home_team_name = team_names.split(" - ")[0].strip()
    away_team_name = team_names.split(" - ")[1].strip()

    # Extract match score
    team_points = header.select_one("span.erv").get_text(strip=True)
    home_team_points = team_points.split("-")[0].strip()
    away_team_points = team_points.split("-")[1].strip()

    # Extract scheduled date and time
    date = header.select("span.erv")[1].get_text(strip=True)
    time = header.select_one("span.erd").get_text(strip=True)

    # Extract venue name and remove extra text
    location = footer.text.replace("Játékhely: ", "").split("(")[0].split("megközelítés")[0].strip()

    # Convert date/time strings to datetime
    datetime = normalize_date_time(date, time)

    # Build structured match record
    round_match_data = {
        "round_number": round_number,
        "round_match_number": round_match_number,
        "location": location,
        "datetime": datetime,
        "home_team_name": home_team_name,
        "away_team_name": away_team_name,
        "home_team_points": home_team_points,
        "away_team_points": away_team_points,
    }

    return round_match_data

def extract_individual_matches(table, round_match_data):
    """
    Extracts individual match details from a given HTML table structure and associated match metadata.

    The function processes an HTML table that contains match data, including player names and match results,
    and combines this information with provided metadata for the round and match. The resulting data structure
    contains comprehensive details for each individual match, such as player names, teams, and respective points.

    :param table: An HTML table element containing match details.
                  The table is expected to have a specific structure where the first row represents guest players,
                  and subsequent rows represent home players and match results.
    :type table: bs4.element.Tag
    :param round_match_data: A dictionary containing metadata for the round and match.
                             It includes details like round number, round match number, team names, etc.
    :type round_match_data: dict
    :return: A list of dictionaries, each representing an individual match.
             Each dictionary contains keys for round number, match number, player details, team names,
             and respective player points.
    :rtype: list | None
    """
    # Skip matches without a player table
    if table is None:
        return None

    rows = table.find_all("tr")

    # Header row contains away players
    first_row = rows[0]

    # Remaining rows contain home players and results
    other_rows = rows[1:]

    # Extract away player names from the first row
    away_players = [away_player_cell.get_text().strip() for away_player_cell in first_row.select("td.ertx")]

    # Extract home player names and match results from the other rows
    match_rows = []
    for other_row in other_rows:
        match_cells = [match_cell.get_text().strip() for match_cell in other_row.find_all("td")]
        match_rows.append(match_cells)

    individual_matches_data = []
    # Convert matrix cells into individual match records
    for match_row in match_rows:
        for index, match_cell in enumerate(match_row):
            if index > 0 and match_cell:
                individual_match = {
                    "round_number": round_match_data["round_number"],
                    "round_match_number": round_match_data["round_match_number"],
                    "home_player": match_row[0],
                    "home_team_name": round_match_data["home_team_name"],
                    "away_player" : away_players[index - 1],
                    "away_team_name": round_match_data["away_team_name"],
                    "home_player_points" : match_cell.split("\\")[0].strip(),
                    "away_player_points": match_cell.split("\\")[1].strip(),
                }
                individual_matches_data.append(individual_match)

    return individual_matches_data

def normalize_date_time(date: str, time: str) -> Optional[datetime]:
    """
    Normalizes a date and time string into a Python datetime object. The function handles Hungarian month
    abbreviations and corrects time formatting issues. If valid time information isn't provided,
    it defaults to `00:00`.

    :param date: A string representing the date in the format "YYYY-MMM-DD", where MMM is an abbreviated
                 Hungarian month name.
    :type date: str
    :param time: A string representing the time. It may include garbage or be formatted as "HH.MM", "HH:MM",
                 or embedded within the string. Optional; defaults to an empty string.
    :type time: str
    :return: A `datetime` object constructed with the normalized date and time if the input is valid;
             otherwise, returns `None`.
    :rtype: Optional[datetime]
    """
    # Mapping of Hungarian month abbreviations
    MONTHS_HU = {
        "JAN": 1, "FEB": 2, "FEBR": 2, "MÁR": 3, "MÁRC": 3, "ÁPR": 4, "MÁJ": 5, "JÚN": 6,
        "JÚL": 7, "AUG": 8, "SZEPT": 9, "OKT": 10, "NOV": 11, "DEC": 12
    }

    # Standardize time separator
    def fix_time(time):
        return time.replace(".", ":")

    # Extract year, month name, day
    m = re.search(r"(\d{4})-([A-ZÁÉŐÚÓÜÖ]+)-(\d+)", date)

    # Invalid date format
    if not m:
        return None

    year = int(m.group(1))
    month = MONTHS_HU[m.group(2)]
    day = int(m.group(3))

    # --- CASE 1: time_str exists but may contain garbage ---
    if time:
        # Look for HH.MM or HH:MM inside time
        t = re.search(r"(\d{1,2}[.:]\d{2})", time)
        if t:
            time_clean = fix_time(t.group(1))
            return datetime.strptime(f"{year}-{month}-{day} {time_clean}", "%Y-%m-%d %H:%M")
        # No valid time → default to 00:00
        return datetime(year, month, day, 0, 0)

    # --- CASE 2: time embedded inside date ---
    t = re.search(r"(\d{1,2}[.:]\d{2})", date)
    if t:
        time_clean = fix_time(t.group(1))
        return datetime.strptime(f"{year}-{month}-{day} {time_clean}", "%Y-%m-%d %H:%M")

    # If no time found, default to 00:00
    return datetime(year, month, day, 0, 0)

def extract_team_leaderboard(table: Tag, round_number: int) -> list[dict]:
    """
    Extracts the leaderboard details of teams from the given table and returns a list
    of dictionaries where each dictionary represents details of a team for a specific
    round in a competition or tournament.

    The method parses the provided table to extract data such as ranks, names, match
    statistics, and points related to each team. It assumes the table rows in the
    input start with header rows, which are skipped during parsing.

    :param table: A BeautifulSoup Tag object representing the leaderboard table.
    :param round_number: The round number associated with the leaderboard data.
    :type round_number: int
    :return: A list of dictionaries where each dictionary contains the team leaderboard
             details such as rank, team name, rounds played, matches won, points, etc.
    :rtype: list[dict]
    """
    leader_board_rows = []

    # Skip table header rows
    for table_row in table.find_all("tr")[2:]:
        table_cells = [td.get_text(" ", strip=True) for td in table_row.select("td")]

        # Convert table row into structured data
        leader_board_row = {
            "round_number": round_number,
            "rank": table_cells[0].replace(".", ""),
            "team_name": table_cells[1].replace(" *", "").strip(),
            "rounds_played": int(table_cells[2]),
            "rounds_won": int(table_cells[3]),
            "rounds_drawn": int(table_cells[4]),
            "rounds_lost": int(table_cells[5]),
            "matches_played": int(table_cells[6]),
            "matches_won": int(table_cells[7]),
            "matches_lost": int(table_cells[8]),
            "matches_won_percent": float(table_cells[9]),
            "points": int(table_cells[10]),
        }

        leader_board_rows.append(leader_board_row)

    return leader_board_rows

def extract_individual_leaderboard(table: Tag, round_number: int) -> list[dict]:
    """
    Extracts an individual leaderboard from a table element for a specific round and returns it
    as a list of dictionaries, where each dictionary represents an individual leaderboard record.

    This function parses a provided HTML table object, processes its rows to extract relevant
    leaderboard data such as player ranks, names, team names, and match performance statistics.

    :param table: The HTML table element (BeautifulSoup Tag) containing individual leaderboard data.
    :param round_number: The round number corresponding to the leaderboard data extracted.
    :return: A list of dictionaries where each dictionary holds the details of a single player's
             leaderboard record.
    :rtype: list[dict]
    """
    leader_board_rows = []

    # Skip table header rows
    for table_row in table.find_all("tr")[2:]:
        table_cells = [td.get_text(" ", strip=True) for td in table_row.select("td")]

        # Convert player statistics into structured data
        leader_board_row = {
            "round_number": round_number,
            "rank": table_cells[0].replace(".", ""),
            "player_name": table_cells[1].split("(")[0].replace(" *", "").strip(),
            "team_name": table_cells[1].split("(")[1].rstrip(")") if "(" in table_cells[1] else "",
            "matches_all": table_cells[3],
            "matches_played": table_cells[4],
            "percentage_played": float(table_cells[5]),
            "matches_won": table_cells[6],
            "matches_lost": table_cells[7],
            "matches_won_percent": float(table_cells[8]),
        }

        leader_board_rows.append(leader_board_row)

    return leader_board_rows