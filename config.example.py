admin_password = "abc"
port = 1234

class bot:
    bot_nick = "bot username on telegram"
    debug = False
    max_votes = 2
    token = "main bot token"
    welcome_token  = "welcome bot token"
    welcome_image = "https://a-cdn.com/image-url"

class api:
    url = "http://an.api"
    key = "abcdef1234"

class db:
    host = "0.0.0.0"
    user = "username"
    password = "1234"
    name = "db name"

class groups:
    links = {"grafiche": "https://t.me/joinchat/x", "video": "https://t.me/joinchat/y", "musica": "https://t.me/z/df25lPGIEdswMWZk"}
    ids = {"musica": -1, "grafica": -2, "video": -3}
    musica = -1
    grafica = -2
    video = -3

class OneTrust:
    url = "https://privacyportaluatde.onetrust.com/request/v1/consentreceipts"
    requestInformation = "token"
    purposes = [
        {
            "Id": "abcdef"
        },
        {
            "Id": "12345"
        }
    ]
