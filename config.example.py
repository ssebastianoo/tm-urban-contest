admin_password = "abc"
port = 1234
warn_id = 1234

class bot:
    bot_nick = "bot username on telegram"
    debug = False
    max_votes = 9
    token = "main bot token"
    welcome_token  = "welcome bot token"

class db:
    host = "0.0.0.0"
    user = "username"
    password = "1234"
    name = "db name"

class groups:
    links = {"grafiche": "https://t.me/joinchat/x", "video": "https://t.me/joinchat/y", "musica": "https://t.me/z"}
    ids = {"musica": -1, "grafica": -2, "video": -3}
    welcome = {-1: "https://video.mp4", -2: "https://video.mp4", -3: "https://video.mp4"}
    rules = {-1: "https://video.mp4", -2: "https://video.mp4", -3: "https://video.mp4"}
    format = {-1: "https://video.mp4", -2: "https://video.mp4", -3: "https://video.mp4"}
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
