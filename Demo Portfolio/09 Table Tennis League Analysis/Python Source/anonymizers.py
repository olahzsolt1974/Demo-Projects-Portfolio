import csv
from pathlib import Path

from config import PROCESSED_DIR

# Columns containing player names
PLAYER_COLUMNS = {
    "player_name",
    "opponent_player",
    "home_player",
    "away_player",
}

# Columns containing team names
TEAM_COLUMNS = {
    "team_name",
    "opponent_team",
    "home_team_name",
    "away_team_name",
}

# Values that should remain unchanged
SPECIAL_VALUES_TO_KEEP = {
    "(játék nélkül)",
}

def get_anonymous_value(value: str, mapping: dict[str, str], prefix: str) -> str:
    """
    Get an anonymous value by mapping an input value to a unique anonymized string.

    This function checks if a given value exists and is part of a predefined mapping.
    If the value is not found in the mapping, it generates a new anonymous value
    using a provided prefix, numbers it sequentially, and stores it in the mapping.
    For special predefined values, the function will keep them unchanged.

    :param value: The input string to anonymize.
    :type value: str
    :param mapping: A dictionary containing a mapping of known values to their
        anonymized forms.
    :type mapping: dict[str, str]
    :param prefix: A string prefix used to generate the anonymized values.
    :type prefix: str
    :return: Anonymized value corresponding to the input or the unaltered
        value if it qualifies as special.
    :rtype: str
    """
    # Remove leading and trailing whitespace
    value = value.strip()

    # Keep empty values unchanged
    if not value:
        return value

    # Preserve predefined special values
    if value in SPECIAL_VALUES_TO_KEEP:
        return value

    # Create a new anonymous identifier if needed
    if value not in mapping:
        mapping[value] = f"{prefix} {len(mapping) + 1:03d}"

    return mapping[value]


def anonymize_csv(
    input_path: Path,
    player_map: dict[str, str],
    team_map: dict[str, str],
) -> None:
    """
    Anonymizes sensitive data in a CSV file by replacing specific columns' values using provided
    mappings for players and teams. The original file remains untouched, and a new anonymized file
    is created with a naming suffix.

    :param input_path: Path to the input CSV file that will be anonymized
    :type input_path: Path
    :param player_map: Dictionary mapping player names to anonymous values
    :type player_map: dict[str, str]
    :param team_map: Dictionary mapping team names to anonymous values
    :type team_map: dict[str, str]
    :return: This function does not return a value
    :rtype: None
    """
    # Read the entire CSV file
    with open(input_path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        fieldnames = reader.fieldnames

    # Skip empty files
    if not rows or not fieldnames:
        print(f"No rows to anonymize: {input_path}")
        return

    # Anonymize all matching columns
    for row in rows:
        # Replace player names
        for column in PLAYER_COLUMNS:
            if column in row:
                row[column] = get_anonymous_value(
                    row[column],
                    player_map,
                    "Player",
                )

        # Replace team names
        for column in TEAM_COLUMNS:
            if column in row:
                row[column] = get_anonymous_value(
                    row[column],
                    team_map,
                    "Team",
                )

    # Create output filename
    output_path = input_path.with_name(f"{input_path.stem}_anonymized.csv")

    # Write anonymized rows to a new CSV file
    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created anonymized file: {output_path}")


def anonymize_all() -> None:
    """
    Anonymizes all CSV files in the processed directory except those already
    marked as anonymized. The function uses maps to maintain consistency when
    replacing identifying information across multiple files.

    :raises FileNotFoundError: If the specified processed directory does not exist
        or cannot be accessed.
    """
    # Shared mappings ensure consistent anonymization
    player_map = {}
    team_map = {}

    # Collect all non-anonymized CSV files
    csv_files = [
        path
        for path in PROCESSED_DIR.glob("*.csv")
        if not path.name.endswith("_anonymized.csv")
    ]

    # Process each CSV file
    for path in csv_files:
        anonymize_csv(path, player_map, team_map)