import telepot, config, mysql.connector, time, ast, asyncio, datetime
from telepot.loop import MessageLoop
from discord.ext import tasks

db = mysql.connector.connect(
  host=config.db.host,
  user=config.db.user,
  password=config.db.password,
  database=config.db.name
)

cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS welcome (time text, chat_id varchar(50), message_id varchar(50))")
db.commit()

@tasks.loop(seconds=5)
async def delete_welcome(bot):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM welcome")
        data = cursor.fetchall()
        now = datetime.datetime.utcnow()

        for x in data:
            time = datetime.datetime.strptime(x[0], '%d/%m/%Y %H:%M:%S')
            if now >= time:
                bot.deleteMessage((int(x[1]), int(x[2])))
                cursor.execute("DELETE FROM welcome WHERE message_id=%s", (x[2],))

        db.commit()
    except Exception as e:
        print(e)

bot = telepot.Bot(config.bot.welcome_token)
delete_welcome.start(bot)

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    groups = [config.groups.musica, config.groups.grafica, config.groups.video]

    if msg["chat"]["id"] not in groups:
        if msg["chat"]["type"] == "private":
            bot.sendMessage(chat_id, "Questo bot funziona solo nei gruppi.", reply_to_message_id=msg["message_id"])
        return

    if msg.get("new_chat_members"):
        members = msg.get("new_chat_members")
        cursor = db.cursor()
        for member in members:
            if member["id"] != bot.getMe()["id"]:
                m = bot.sendVideo(chat_id, config.groups.welcome[msg["chat"]["id"]], caption = f"@{member['username']} è entrato/a", reply_to_message_id = msg['message_id'])
                now = datetime.datetime.utcnow()
                then = (now + datetime.timedelta(seconds=80))
                raw  = f"{then.day if len(str(then.day)) != 1 else f'0{then.day}'}/{then.month if len(str(then.month)) != 1 else f'0{then.month}'}/{then.year if len(str(then.year)) != 1 else f'0{then.year}'} {then.hour if len(str(then.hour)) != 1 else f'0{then.hour}'}:{then.minute if len(str(then.minute)) != 1 else f'0{then.minute}'}:{then.second if len(str(then.second)) != 1 else f'0{then.second}'}"
                cursor.execute("INSERT INTO welcome (time, chat_id, message_id) VALUES (%s, %s, %s)", (raw, chat_id, m["message_id"]))
        db.commit()

MessageLoop(bot, {'chat': on_chat_message}).run_as_thread()
print("ready")

loop = asyncio.get_event_loop()
loop.run_forever()
