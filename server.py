import datetime, mysql.connector, config, os, requests, json, telepot, ast, utils, datetime, uuid, requests, io, base64
from PIL import Image
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.loop import MessageLoop
from flask import Flask, render_template, redirect, request, Response
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 64 * 1000 * 1000
bot = telepot.Bot(config.bot.token)
auth_key = config.api.key

connection = mysql.connector.connect(
  host=config.db.host,
  user=config.db.user,
  password=config.db.password,
  database=config.db.name
)
db = utils.DataBase(connection)

db.check_db()
cache_mode = db.get_data()["mode"]

@app.errorhandler(404)
def page_not_found(e):
    return "Non ho trovato la pagina che cercavi"

@app.errorhandler(413)
def file_too_large(e):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    return render_template("layout.html", error="Il file caricato supera i 64MB!", provincie=provincie, today=today)

@app.route("/votes")
def check_votes():
    data = db.get_data()["votes"]
    return render_template("check_votes.html", votes=sorted(data, key=lambda x: x["votes"], reverse=True))

@app.route("/test", methods=["POST"])
def test():
    picture = request.json.get("picture")
    base64_string = picture['content'].split(',')[1]
    image = base64.b64decode(base64_string)
    img = Image.open(io.BytesIO(image))

    ext = picture["name"].split(".")[-1]
    filename = f"{uuid.uuid1().int}.{ext}"
    current_path = os.getcwd()
    img.save(os.path.join(current_path, f"static/selfies/{filename}"))

    return request.json

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "GET":
        return render_template("layout.html")

    first_name = request.json.get("firstName")
    last_name = request.json.get("lastName")
    birth_date = request.json.get("birthDate")
    telephone = request.json.get("telephone")
    email = request.json.get("email")
    address = request.json.get("address")
    city = request.json.get("city")
    province = request.json.get("province")
    user_name = request.json.get("userName")
    category = request.json.get("category")
    picture = request.json.get("picture")

    base64_string = picture['content'].split(',')[1]
    image = base64.b64decode(base64_string)
    img = Image.open(io.BytesIO(image))
    ext = picture["name"].split(".")[-1]
    filename = f"{uuid.uuid1().int}.{ext}"
    current_path = os.getcwd()
    img.save(os.path.join(current_path, f"static/selfies/{filename}"))

    try:
        cursor = db.db.cursor()
    except (AttributeError, MySQLdb.OperationalError):
        db.connect()
        cursor = db.db.cursor()

    if request.form.get("parentFirstName"):
        parent_first_name = request.form.get("parentFirstName")
        parent_last_name = request.form.get("parentLastName")
        parent_id_card = request.form.get("parentIdCard")
        parent_telephone = request.form.get("parentTelephone")
        parent_email = request.form.get("parentEmail")

        cursor.execute("insert into users (fileName, firstName, lastName, birthDate, telephone, email, address, city, province, userName, category, parentFirstName, parentLastName, parentIdCard, parentTelephone, parentEmail) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (filename, first_name, last_name, birth_date, telephone, email, address, city, province, user_name, category, parent_first_name, parent_last_name, int(parent_id_card), parent_telephone, parent_email))
    else:
        cursor.execute("insert into users (fileName, firstName, lastName, birthDate, telephone, email, address, city, province, userName, category) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (filename, first_name, last_name, birth_date, telephone, email, address, city, province, user_name, category))
    db.db.commit()

    try:
        group = int(category)
    except:
        try:
            group = config.groups.ids[category]
        except KeyError:
            return 404, "Group not found"

    data = db.get_data()
    data["users"][str(user_name).lower()] = {"group": group}
    db.update_data(data)

    body = {"identifier": email, "requestInformation": config.OneTrust.requestInformation, "purposes": config.OneTrust.purposes, "dsDataElements": {"FirstName": first_name, "LastName": last_name}}
    requests.post(config.OneTrust.url, headers = {"Content-Type": "application/json"}, data=json.dumps(body))

    return Response(status=200, response="Ok")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/regolamento")
def regolamento():
    return render_template("regolamento.html")

@app.route("/isAdult/", methods=["POST"])
def is_adult():
    raw_date = request.json.get("birthDate")
    if not raw_date:
        return Response(response="missing date fiels", status=400)

    date = datetime.datetime.strptime(raw_date, "%Y-%m-%d")
    if (datetime.datetime.now() - date).days / 365 < 18:
        return {"adult": False}
    return {"adult": True}

@app.route("/admin", methods=["GET", "POST"])
def sql_admin():
    if request.method == "GET":
        return render_template("login.html", success=True)
    elif request.method == "POST":
        if request.form["type"] == "login":
            if request.form["password"] == config.admin_password and request.form["username"].lower() == "admin":
                cursor = db.db.cursor()
                data = db.get_data()
                cursor.execute("select * from users")
                sql = cursor.fetchall()
                return render_template("admin.html", data=data, json=json, sql=sql)

            else:
                return render_template("login.html", success=False)

        elif request.form["type"] == "admin":
            data = request.form["output"]
            lines = data.splitlines()
            count = 0
            data = ""
            for line in lines:
                if not line.isspace():
                    if count == 0:
                        if line.replace("{", "").isspace():
                            data += "{\n"
                    else:
                        data += line + "\n"
                count += 1
            try:
                data = ast.literal_eval(data)
            except:
                return "Syntax Error"

            db.update_data(data)

            return redirect("/admin")

@app.route("/telegram", methods=["GET", "POST"])
def users():
    if request.method == "GET":
        return "(╯°□°）╯︵ ┻━┻"

    key = request.headers.get('Authorization')
    if not key or str(key) != auth_key:
        key = request.args.get("api-key")
        if not key:
            key = request.json.get("api-key")
            if not key:
                abort(401, "Unauthorized")

    username = request.args.get('username')
    if not username:
        username = request.json.get('username')
        if not username:
            abort(400, "Missing username field")

    group = request.args.get('group')
    if not group:
        group = request.json.get('group')
        if not group:
            abort(400, "Missing group field")

    try:
        group = int(group)
    except:
        groups = {"musica": -1001461743777, "grafica": -1001313918608, "video": -1001433733101}
        try:
            group = config.groups.ids[group]
        except KeyError:
            abort(404, "Group not found")

    data = db.get_data()
    data["users"][str(username).lower()] = {"group": group}
    db.update_data(data)
    return "Done!"

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    groups = [config.groups.musica, config.groups.grafica, config.groups.video]

    if msg["chat"]["id"] not in groups:
        if msg["chat"]["type"] == "private":
            bot.sendMessage(chat_id, "Questo bot funziona solo nei gruppi.", reply_to_message_id=msg["message_id"])
        return

    for x in ["document", "media", "video", "photo", "animation", "audio"]:
        f = msg.get(x)
        if f:
            file = f
            break
        else:
            file = None

    if file:
        if cache_mode == "testo":
            member = bot.getChatMember(chat_id, msg["from"]["id"])
            if member["status"] in ["creator", "administrator"]:
                pass
            else:
                try: bot.deleteMessage((chat_id, msg["message_id"]))
                except: pass
                return

        data = db.get_data()
        votes = data["votes"]

        if msg["from"]["id"] in [vote["user_id"] for vote in votes]:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Conferma', callback_data='overwrite_confirm'), InlineKeyboardButton(text='Annulla', callback_data='overwrite_cancel')]])
            return bot.sendMessage(chat_id, "Sembra che tu abbia già inviato un file per il concorso, vuoi sovrascriverlo inviandone un altro?\nPerderai i voti raccolti fino ad oggi e la data di consegna (anche il tempo fa la differenza per vincere visto che se ci fossero lavori a pari merito vince chi ha fatto prima l’upload.)", reply_to_message_id=msg["message_id"], reply_markup=keyboard)

        if type(file) == list:
            file_id = file[0]["file_id"]
            file_unique_id = file[0]["file_unique_id"]
        elif type(file) == dict:
            file_id = file["file_id"]
            file_unique_id = file["file_unique_id"]

        ext = "." + str(bot.getFile(file_id)["file_path"].split(".")[-1])
        filename = file_unique_id + ext

        current_path = os.getcwd()
        bot.download_file(file_id, os.path.join(current_path, f"static/contest/{filename}"))

        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Vota', callback_data='vote')]])
        vote_message = bot.sendMessage(chat_id, f"Vota @{msg['from']['username']}", reply_markup=keyboard, reply_to_message_id=msg["message_id"])

        vote = {'chat_id': chat_id, 'message_id': msg['message_id'], "vote_id": vote_message["message_id"],'votes': 0, "users": [], "user_id": msg["from"]["id"], "username": msg["from"]["username"],"file": f"static/contest/{filename}"}
        votes.append(vote)

        db.update_data(data)

    else:
        if cache_mode == "media":
            member = bot.getChatMember(chat_id, msg["from"]["id"])
            if member["status"] in ["creator", "administrator"]:
                pass
            else:
                try: bot.deleteMessage((chat_id, msg["message_id"]))
                except: pass
                return

    text = msg.get("text")

    if not text:
        return

    elif text.startswith("/accept"):
        member = bot.getChatMember(chat_id, msg["from"]["id"])
        if member["status"] in ["creator", "administrator"]:
            pass
        else:
            return
        args = text.split(" ")
        if len(args) == 1:
            return bot.sendMessage(chat_id, "Specifica un username!", reply_to_message_id=msg["message_id"])
        else:
            username = str(args[1]).lower()
            if username.startswith("@"):
                username = username[1:]
            try: group = args[2]
            except: group = msg["chat"]["id"]

            try: group = int(group)
            except: return bot.sendMessage(chat_id, "ID di un gruppo non valido", reply_to_message_id=msg["message_id"])

            # db = sqlite3.connect(config.db_path)
            data = db.get_data()
            users = data["users"]
            users[username] = {"group": group}
            db.update_data(data)
            return bot.sendMessage(chat_id, f"@{username} ammesso al gruppo", reply_to_message_id=msg["message_id"])

    elif text.startswith("/leaderboard"):
        # db = sqlite3.connect(config.db_path)
        data = db.get_data()["votes"]
        # db.close()
        lb = sorted(data, key=lambda x : x["votes"], reverse=True)
        res = ""
        modes = dict()
        for x in data:
            try:
                modes[x["chat_id"]].append(x)
            except:
                modes[x["chat_id"]] = [x]

        for mode in modes:
            chat = bot.getChat(x["chat_id"])
            res += f"{chat['title']}\n"
            c = 0
            for x in modes[mode]:
                if c >= 5:
                    break
                member = bot.getChatMember(x["chat_id"], x["user_id"])
                if x["votes"] == 1:
                    v = "vote"
                else:
                    v = "votes"
                res += f"<b>@{member['user']['username']}</b> - <code>{x['votes']}</code> {v}\n"
                c += 1
            res += "\n"
        bot.sendMessage(chat_id, res, reply_to_message_id=msg["message_id"], parse_mode="HTML")

    elif text.startswith("/mode"):
        member = bot.getChatMember(chat_id, msg["from"]["id"])
        if member["status"] in ["creator", "administrator"]:
            pass
        else:
            return
        mode = cache_mode
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Default', callback_data='mode_default'), InlineKeyboardButton(text='Testo', callback_data='mode_testo'), InlineKeyboardButton(text='Media', callback_data='mode_media')]])

        bot.sendMessage(chat_id, f"Modalità attuale: *{mode}*\n\nScegli una delle seguenti modalità:\n*Default*: è possibile inviare sia testo che media.\n*Testo*: è possibile inviare solo testo.\n*Media*: è possibile inviare solo media.", parse_mode="Markdown", reply_markup=keyboard, reply_to_message_id=msg["message_id"])

    elif text.startswith("/id"):
        bot.sendMessage(chat_id, chat_id, reply_to_message_id=msg["message_id"])

def on_callback_query(msg):
    global cache_mode
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')

    chat = bot.getChat(from_id)

    if query_data == "vote":

        if from_id == msg["message"]["reply_to_message"]["from"]["id"]:
            return bot.answerCallbackQuery(query_id, text="Non puoi votarti da solo!", show_alert=True)

        data = db.get_data()
        user_votes = data["user_votes"]
        votes = data["votes"]
        vote = [v for v in votes if v["chat_id"] == msg["message"]["chat"]["id"] and v["message_id"] == msg["message"]["reply_to_message"]["message_id"]][0]

        if from_id in vote["users"]:
            user_votes[from_id] -= 1
            vote["votes"] -= 1
            vote["users"].remove(from_id)

        else:
            if not user_votes.get(from_id): user_votes[from_id] = 1
            else:
                if user_votes.get(from_id) >= config.bot.max_votes:
                    return bot.answerCallbackQuery(query_id, text="Hai raggiunto il massimo di voti! Rimuovi qualche voto precedente per votare ancora", show_alert=True)
                user_votes[from_id] += 1
            vote["votes"] += 1
            vote["users"].append(from_id)

        actual_votes = vote["votes"]

        db.update_data(data)

        text = f"Vota @{msg['message']['reply_to_message']['from']['username']}\n\nVoti: {actual_votes}"

        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Vota', callback_data='vote')]])
        bot.editMessageText((msg["message"]["chat"]["id"], msg["message"]["message_id"]), text, reply_markup=keyboard)

    elif query_data in ["mode_default", "mode_testo", "mode_media"]:

        if from_id != msg["message"]["reply_to_message"]["from"]["id"]:
            return bot.answerCallbackQuery(query_id, text="Non puoi eseguire quest'azione!", show_alert=True)

        mode = query_data[5:]
        cache_mode = mode
        data = db.get_data()
        data["mode"] = mode
        db.update_data(data)

        bot.editMessageText((msg["message"]["chat"]["id"], msg["message"]["message_id"]), f"Modalità aggiornata a *{cache_mode}*!", parse_mode="Markdown")

    elif query_data == "overwrite_confirm":

        if from_id != msg["message"]["reply_to_message"]["from"]["id"]:
            return bot.answerCallbackQuery(query_id, text="Questo bottone non è per te!", show_alert=True)

        for x in ["document", "media", "video", "photo", "animation", "audio"]:
            f = msg["message"]["reply_to_message"].get(x)
            if f:
                file = f
                break
            else:
                file = None

        data = db.get_data()
        votes = data["votes"]
        vote_to_delete = [vote for vote in votes if vote["user_id"] == msg["message"]["reply_to_message"]["from"]["id"]][0]
        votes.remove(vote_to_delete)

        if type(file) == list:
            file_id = file[0]["file_id"]
            file_unique_id = file[0]["file_unique_id"]
        elif type(file) == dict:
            file_id = file["file_id"]
            file_unique_id = file["file_unique_id"]

        ext = "." + str(bot.getFile(file_id)["file_path"].split(".")[-1])
        filename = file_unique_id + ext

        bot.download_file(file_id, f"static/contest/{filename}")

        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Vota', callback_data='vote')]])
        try: bot.deleteMessage((msg["message"]["chat"]["id"], msg["message"]["message_id"]))
        except: pass
        try: bot.deleteMessage((vote_to_delete["chat_id"], vote_to_delete["vote_id"]))
        except: pass
        vote_message = bot.sendMessage(msg["message"]["chat"]["id"], f"Vota @{msg['message']['reply_to_message']['from']['username']}", reply_markup=keyboard, reply_to_message_id=msg["message"]["reply_to_message"]["message_id"])

        vote = {'chat_id': msg["message"]["chat"]["id"], 'message_id': msg["message"]["reply_to_message"]['message_id'], "vote_id": vote_message["message_id"], 'votes': 0, "users": [], "user_id": msg["message"]["reply_to_message"]["from"]["id"], "username": msg["message"]["reply_to_message"]["from"]["username"],"file": f"static/{filename}"}
        votes.append(vote)

        db.update_data(data)

    elif query_data == "overwrite_cancel":
        if from_id != msg["message"]["reply_to_message"]["from"]["id"]:
            return bot.answerCallbackQuery(query_id, text="Questo bottone non è per te!", show_alert=True)

        bot.deleteMessage((msg["message"]["chat"]["id"], msg["message"]["message_id"]))

MessageLoop(bot, {'chat': on_chat_message, 'callback_query': on_callback_query}).run_as_thread()

print("ready")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.port, debug=config.bot.debug)
