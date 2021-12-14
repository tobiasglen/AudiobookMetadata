import requests
from rich import box, print_json
from rich.prompt import Prompt, Confirm
from rich.console import Console
from audiobookshelf import AudiobookshelfBook, audiobookshelf_login, audiobookshelf_book_lookup, audiobookshelf_book_update
from audnexus import audnexus_asin_lookup

console = Console()


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



if __name__ == '__main__':
    # Prompt user for book title & author (book title can not be blank)
    book_title_prompt = Prompt.ask("Book Title")
    while not bool(book_title_prompt):  # Verify user input is not empty
        book_title_prompt = Prompt.ask("Book Title (Can't be blank)")
    book_author_prompt = Prompt.ask("Author")

    query_aud = search_audible(book_title=book_title_prompt, book_author=book_author_prompt)

    if bool(query_aud):  # If the function returned at-least 1 asin we can call new function to gt book details
        aud_book_details = audnexus_asin_lookup(query_aud)
        console.line(count=2)  # Print 2 blank lines
        console.print(f'OK, We got the audiobook metadata for "[chartreuse2]{aud_book_details["title"]}[/chartreuse2]" by "[chartreuse2]{aud_book_details["authors"][0]["name"]}[/chartreuse2]"\n')

        # Ask if the user wants to see json output
        if Confirm.ask(prompt="Show JSON output?", default=False):
            print_json(data=aud_book_details)
            console.line(count=1)

        # Prompt user if they want to search audiobookshelf for the book & update the books details if found
        if Confirm.ask(prompt="Search audiobookshelf for the book?", default=True):
            bearer_token = audiobookshelf_login()  # Get the bearer token
            if bearer_token:
                # Now try & find the book on audiobookshelf
                audiobookshelf_lookup = audiobookshelf_book_lookup(book_title=book_title_prompt, book_author=book_author_prompt, token=bearer_token)
                if audiobookshelf_lookup:
                    console.print("\nBook found on audiobookshelf.\n", style="green")

                    # Use the AudiobookshelfBook class to create a default book object
                    p1 = AudiobookshelfBook(audiobookshelf_json=audiobookshelf_lookup, audnexus_json=aud_book_details)
                    # Update the book genres & tags which we get back from the audnexus api (AKA audible)
                    # TODO - Create a function to get the real genres & tags from the audible api
                    p1.update_genres(genres=["Science Fiction & Fantasy", "Science Fiction"])
                    p1.update_tags(tags=["Adventure", "Hard Science Fiction"])

                    # Update the book on audiobookshelf
                    f = audiobookshelf_book_update(book_id=audiobookshelf_lookup["id"], book_payload=p1.return_json(), token=bearer_token)
                    if f:
                        console.print("\nBook updated on audiobookshelf.\n", style="green")

                else:
                    console.print("\nBook not found on audiobookshelf.\n", style="red")
            else:
                console.print("\nError: Unable to get bearer token. Quitting...", style="red")


