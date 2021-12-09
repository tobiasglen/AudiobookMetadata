import requests
from rich import box, print_json
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.console import Console

console = Console()

# URL for the API
audnex_url = "https://api.audnex.us/books"


def search_audible(book_title, book_author):
    query = requests.get(
        url="https://api.audible.com/1.0/catalog/products",
        params={
            "title": book_title,
            "author": book_author,
            "category_id": "18685580011"  # Only show English results
        }
    )

    if not query.ok:  # If the request failed then we can't continue so just exit
        console.print("\nError: Unable to query audible API. Quitting...", style="red")
        quit()

    possible_asin = []
    # If any results are found we loop through them all & append each to a list
    if query.json()["total_results"] != 0:
        for result in query.json()["products"]:
            # noinspection PyTypeChecker
            possible_asin.append(result["asin"])

    # Return list of audible asin IDs for the book title & author we searched for
    return possible_asin


def book_details_verify(asin_list):
    console.line(count=1)  # Line break
    aud_details = Table(show_header=True, header_style="bold cyan", box=box.HEAVY, border_style="dim", show_lines=True, title="Possible Matches", title_style="bold chartreuse2")
    aud_details.add_column("Result", justify="center", style="chartreuse1")
    aud_details.add_column("Title", justify="center", style="dodger_blue1")
    aud_details.add_column("Author", justify="center", style="deep_pink1")
    aud_details.add_column("Description", justify="center")
    aud_details.add_column("Language", justify="center")
    aud_details.add_column("ASIN", justify="center")

    metadata_dict = {}
    for count, asin in enumerate(asin_list, start=1):
        api_call = requests.get(f"{audnex_url}/{asin}")

        if not api_call.ok:  # Skip to next iteration if response from audnex is bad
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

        # Update metadata_dict so we can prompt user for correct entry
        metadata_dict[str(count)] = book_md

    console.print(aud_details)
    prompt_verify_book = Prompt.ask("Input event ID", choices=[*metadata_dict])
    return metadata_dict[prompt_verify_book]


if __name__ == '__main__':
    # Prompt user for book title & author (book title can not be blank)
    book_title_prompt = Prompt.ask("Book Title")
    while not bool(book_title_prompt):  # Verify user input is not empty
        book_title_prompt = Prompt.ask("Book Title (Can't be blank)")
    book_author_prompt = Prompt.ask("Author")

    query_aud = search_audible(book_title=book_title_prompt, book_author=book_author_prompt)

    if bool(query_aud):  # If the function returned at-least 1 asin we can call new function to gt book details
        book_details = book_details_verify(query_aud)
        console.line(count=2)
        console.print(f'OK, We got the audiobook metadata for "[chartreuse2]{book_details["title"]}[/chartreuse2]" by "[chartreuse2]{book_details["authors"][0]["name"]}[/chartreuse2]"\n')

        # Ask if the user wants to see json output
        if Confirm.ask(prompt="Show JSON output?", default=True):
            print_json(data=book_details)

        # Now we start searching for a possible torrent
        console.line(count=1)


