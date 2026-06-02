import argparse

from downloaders import download_pages, download_all
from parsers import (
    parse_round_matches,
    parse_team_leaderboard,
    parse_individual_leaderboard,
    parse_all,
)
from anonymizers import anonymize_all
from pipeline import run_all


def main():
    """
    Executes various commands related to downloading, parsing, anonymizing,
    and managing data. The available commands determine specific workflows
    to execute depending on the provided user input.

    Commands allow downloading different forms of data (e.g., round matches,
    team leaderboard, individual leaderboard) or parsing and processing such
    data to suit required formats or functionalities. The program also
    supports anonymizing or executing all tasks sequentially.

    :raises SystemExit: Raised by argparse when invalid command-line
        arguments are provided.
    """
    # Create command-line argument parser
    parser = argparse.ArgumentParser()

    # Define supported commands
    parser.add_argument(
        "command",
        choices=[
            "download-round-matches",
            "download-team-leaderboard",
            "download-individual-leaderboard",
            "download-all",
            "parse-round-matches",
            "parse-team-leaderboard",
            "parse-individual-leaderboard",
            "parse-all",
            "anonymize-all",
            "run-all"
        ],
    )

    # Read command-line arguments
    args = parser.parse_args()

    # Run the selected command
    if args.command == "download-round-matches":
        download_pages("round-matches")
    elif args.command == "download-team-leaderboard":
        download_pages("team-leaderboard")
    elif args.command == "download-individual-leaderboard":
        download_pages("individual-leaderboard")
    elif args.command == "download-all":
        download_all()
    elif args.command == "parse-round-matches":
        parse_round_matches()
    elif args.command == "parse-team-leaderboard":
        parse_team_leaderboard()
    elif args.command == "parse-individual-leaderboard":
        parse_individual_leaderboard()
    elif args.command == "parse-all":
        parse_all()
    elif args.command == "anonymize-all":
        anonymize_all()
    elif args.command == "run-all":
        run_all()

# Run main function when file is executed directly
if __name__ == "__main__":
    main()