from .variables import *


def put_credentials(user_id, cred):
    storage = Storage(CREDENTIALS_STORAGE+f"{user_id}.json")
    storage.put(cred)


def get_credentials(user_id):
    storage = Storage(CREDENTIALS_STORAGE + f"{user_id}.json")
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        return None
    return credentials


def refresh_token(client_id, client_secret, ref_token):
    params = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": ref_token
    }

    authorization_url = "https://oauth2.googleapis.com/token"

    r = requests.post(authorization_url, data=params)

    if r.ok:
        return r.json()['access_token']
    else:
        return None