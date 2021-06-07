import telepot, config, mysql.connector, time, ast, asyncio
from telepot.loop import MessageLoop

def get_data(c):
    c.execute("select data from tau_marin")
    data = c.fetchone()
    if not data:
        return None
    else:
        return ast.literal_eval(data[0])

bot = telepot.Bot(config.bot.welcome_token)

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    groups = {config.groups.musica, config.groups.grafica, config.groups.video}

    if msg["chat"]["id"] not in groups:
        if msg["chat"]["type"] == "private":
            bot.sendMessage(chat_id, "Questo bot funziona solo nei gruppi.", reply_to_message_id=msg["message_id"])
        return

    if msg.get("new_chat_members"):

        db = mysql.connector.connect(
          host=config.db.host,
          user=config.db.user,
          password=config.db.password,
          database=config.db.name
        )

        cursor = db.cursor()

        members = msg.get("new_chat_members")
        data = get_data(cursor)
        users = data["users"]

        db.close()

        print(users)

        for member in members:
            if str(member['username']).lower() not in users:
                if str(member['username']).lower() == config.bot.bot_nick:
                    return
                return bot.kickChatMember(chat_id, member['id'])
            else:
                if int(msg["chat"]["id"]) != int(users[str(member["username"]).lower()]["group"]):
                    return bot.kickChatMember(chat_id, member['id'])
                m = bot.sendVideo(chat_id, config.bot.welcome_image, caption = f"@{member['username']} è entrato/a", reply_to_message_id = msg['message_id'])
                asyncio.run(asyncio.sleep(5))
                return bot.deleteMessage((chat_id, m["message_id"]))

MessageLoop(bot, {'chat': on_chat_message}).run_as_thread()

print("ready")

while True:
    time.sleep(10)
