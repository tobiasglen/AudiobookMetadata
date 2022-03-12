import json
import os
import re
import requests
from dotenv import load_dotenv
from rich.console import Console

console = Console()

# load .env
load_dotenv()

abs_headers = {
    "Authorization": "Bearer {}",
    "Content-Type": "application/json"
}


def audiobookshelf_login():
    login_payload = {
        "username": os.getenv("audiobookshelf_username"),
        "password": os.getenv("audiobookshelf_password"),
    }
    login_request = requests.post(url=f'{os.getenv("audiobookshelf_url")}/login', data=login_payload)
    return login_request.json()['user']['token'] if login_request.ok else None


def audiobookshelf_book_lookup(book_title, book_author, token):
    lookup_request = requests.get(url=f'{os.getenv("audiobookshelf_url")}/api/libraries/main/search?q={book_title}', headers={'Authorization': f'Bearer {token}'})
    if not lookup_request.ok or len(lookup_request.json()['audiobooks']) == 0:
        return None

    lookup_response = lookup_request.json()
    for audiobook in lookup_response['audiobooks']:
        resp_book_title = re.sub(r'\W+', '', str(audiobook['audiobook']['book']['title']).lower())
        resp_book_author = re.sub(r'\W+', '', str(audiobook['audiobook']['book']['author']).lower())
        # book_title = ''.join(e for e in str(audiobook['audiobook']['book']['title']) if e.isalnum()).lower()
        # book_author = ''.join(e for e in str(audiobook['audiobook']['book']['author']) if e.isalnum()).lower()

        if resp_book_title == re.sub(r'\W+', '', str(book_title).lower()) and resp_book_author == re.sub(r'\W+', '', str(book_author).lower()):
            # print(f'Found audiobookshelf! id: {audiobook["audiobook"]["id"]}')
            # print(print_json(json.dumps(audiobook)))
            # quit()
            return audiobook["audiobook"]

    return None


# Create a new class to parse the json & update certain fields then return the json
class AudiobookshelfBook:
    def __init__(self, audiobookshelf_json, audnexus_json):
        self.book_payload = {
            "book": {
                "title": f'{audiobookshelf_json["book"]["title"]}',
                "subtitle": audiobookshelf_json['book']['subtitle'],
                "description": audiobookshelf_json['book']['description'],
                "author": audiobookshelf_json['book']['author'],
                "narrator": audiobookshelf_json['book']['narrator'],
                "series": audiobookshelf_json['book']['series'],
                "volumeNumber": audiobookshelf_json['book']['volumeNumber'],
                "publishYear": audiobookshelf_json['book']['publishYear'],
                "publisher": audiobookshelf_json['book']['publisher'],
                "isbn": audiobookshelf_json['book']['isbn'],
                "genres": []
            },
            "tags": []
        }


    def update_book_title(self, new_title):
        self.book_payload['book']['title'] = new_title
        return self.book_payload

    def update_tags(self, tags):
        self.book_payload['tags'] = tags
        return self.book_payload

    def update_genres(self, genres):
        self.book_payload['book']['genres'] = genres
        return self.book_payload



    def return_json(self):
        # Prepare the json for the POST request to audiobookshelf (dumps to string) & return
        return json.dumps(self.book_payload)





def audiobookshelf_book_update(book_id, book_payload, token):
    # I got these headers from test requests made in Postman
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0',
        'Accept': 'application/json, text/plain, */*',
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json;charset=utf-8'
    }

    # Update the book details in the audiobookshelf
    update_book_request = requests.patch(url=f'{os.getenv("audiobookshelf_url")}/api/books/{book_id}', headers=headers, data=book_payload)

    return bool(update_book_request.ok)
