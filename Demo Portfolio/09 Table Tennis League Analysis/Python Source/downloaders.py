import time
import requests
from config import BASE_URL, TEAM_ID, LEAGUE_ID, ROUNDS, RAW_DIR, PAGE_TYPES

# Session cookie used for pages requiring authentication
COOKIES = {
'PHPSESSID': 'e0pj2tnk7ob8klul3qn1vtg927',
}

def download_pages(page_type: str, use_cookies: bool | None = None):
    """
    Download multiple pages based on the specified page type and optional cookie usage.

    This function downloads pages for each round specified in the global `ROUNDS` and saves them
    to the appropriate folder according to the configuration in `PAGE_TYPES`. The download can
    optionally use cookies if required by the page type configuration or as specified by the user.

    :param page_type: The type of the page to download, corresponding to keys in the `PAGE_TYPES`.
    :type page_type: str
    :param use_cookies: Whether to use cookies during the request. If None, the decision is based
        on the specific page configuration for "cookies_required".
    :type use_cookies: bool | None
    :return: None
    """
    # Load configuration for the requested page type
    page_config = PAGE_TYPES[page_type]

    # Create output directory if it does not exist
    output_dir = RAW_DIR / page_config["folder"]
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine whether cookies should be sent
    should_use_cookies = (
        page_config["cookies_required"]
        if use_cookies is None
        else use_cookies
    )

    # Download data for every configured round
    for round_number in ROUNDS:
        # Build request parameters
        params = {
            "ford": str(round_number),
            "mod": page_config["mod"],
            "id": TEAM_ID,
            "liga": LEAGUE_ID,
            "ok": "ok",
        }

        print(f"Downloading {page_type}, round {round_number}")

        # Request page content
        response = requests.get(
            BASE_URL,
            params=params,
            cookies=COOKIES if should_use_cookies else None,
        )
        response.raise_for_status()

        # Generate output filename
        filename = page_config["filename"].format(round_number=round_number)

        # Save downloaded HTML
        output_file = output_dir / filename
        output_file.write_bytes(response.content)

        # Avoid overwhelming the server
        time.sleep(0.5)

def download_all():
    """
    Downloads all pages for the predefined page types.

    This function iterates through all predefined page types
    and downloads their pages using an internal helper function.

    :return: None
    """
    # Download every configured page type
    for page_type in PAGE_TYPES:
        download_pages(page_type)