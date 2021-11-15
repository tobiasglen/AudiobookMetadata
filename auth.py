import audible
from os.path import exists
from rich.prompt import Prompt


def get_auth():

    if exists("audible_auth.txt"):
        auth = audible.Authenticator.from_file(filename="audible_auth.txt")
    else:
        # Get the username and password from the user & authenticate with audible then dump the cookie/auth to a text file
        audible_username = Prompt.ask("Enter your Audible/Amazon username")
        audible_password = Prompt.ask("Enter your Audible/Amazon password")

        auth = audible.Authenticator.from_login(username=f"{audible_username}", password=f"{audible_password}", locale="us", register=True)
        auth.to_file(filename="t.txt", encryption=False)

    # Return the authenticator class instance
    return auth

