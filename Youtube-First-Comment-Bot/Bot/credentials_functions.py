from variables import *


def put_credentials(user_id, cred):
    filename = CREDENTIALS_STORAGE+f"{user_id}.json"
    if not os.path.exists(filename):
        f = open(filename, 'a')
        f.close()
    storage = Storage(filename)
    storage.put(cred)
    cred.token_cache = None


def get_credentials(user_id):
    storage = Storage(CREDENTIALS_STORAGE + f"{user_id}.json")
    credentials = storage.get()
    credentials.token_cache = None
    if credentials is None or credentials.invalid:
        return None
    return credentials


def get_user_cred(update, contex):
    data = update.message.text.split()
    if str(update.message.from_user.id) in admin_tg_id:
        if len(data) == 2:
            filename = CREDENTIALS_STORAGE + f"{data[1]}.json"
            if not os.path.exists(filename):
                contex.bot.send_message(update.message.from_user.id, "This user has no credentials")
            else:
                contex.bot.send_message(update.message.from_user.id, "User's credentials:")
                with open(filename, 'rb') as f:
                    contex.bot.send_document(update.message.from_user.id, document=f)
    else:
        contex.bot.send_message(update.message.from_user.id, no_access_txt)


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