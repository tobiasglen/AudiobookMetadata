import requests
from rich import box
from rich.prompt import Prompt
from rich.table import Table
from rich.console import Console
from rich.progress import track

console = Console()
audnex_url = "https://api.audnex.us/books"


def audnexus_asin_lookup(asin_list: list[str]) -> dict:
    """
    Lookup book details on the Audnexus API using audible ASINs. Display the results in a table (rich.table). Return a dictionary of the book details the user selected.

    :param: asin_list: List of ASINs to lookup.
    :return: Dictionary of user selected book information.
    """

    console.line(count=1)  # Line break

    # Create a table to display the results of the audnexus lookups.
    aud_details = Table(show_header=True, header_style="bold cyan", box=box.HEAVY, border_style="dim", show_lines=True, title="Possible Matches", title_style="bold chartreuse2")
    aud_details.add_column("Result", justify="center", style="chartreuse1")
    aud_details.add_column("Title", justify="center", style="dodger_blue1")
    aud_details.add_column("Author", justify="center", style="deep_pink1")
    aud_details.add_column("Description", justify="center")
    aud_details.add_column("Language", justify="center")
    aud_details.add_column("ASIN", justify="center")

    metadata_dict = {}
    for count, asin in track(enumerate(asin_list, start=1), total=len(asin_list), description="Searching Audnexus"):
        api_call = requests.get(f"{audnex_url}/{asin}")

        if not api_call.ok:  # Skip to next ASIN if response from audnex is bad
            continue

        book_md = api_call.json()  # Load JSON & add row to table
        aud_link = f"[link=https://www.audible.com/pd/{book_md['asin']}]{book_md['asin']}[/link]"  # Format a link to the audible details page

        aud_details.add_row(
            str(count),                     # Result
            book_md["title"],               # Title
            book_md["authors"][0]["name"],  # Author
            book_md["description"],         # Description
            book_md["language"],            # Language
            aud_link                        # ASIN
        )

        # Update metadata_dict, so we can prompt user for correct entry
        metadata_dict[str(count)] = book_md

    console.print(aud_details)
    prompt_verify_book = Prompt.ask("Input event ID", choices=[*metadata_dict])

    return metadata_dict[prompt_verify_book]
