import datetime, mysql.connector, config, os
from flask import Flask, render_template, redirect, request
from werkzeug.utils import secure_filename

app = Flask(__name__)

db = mysql.connector.connect(
  host=config.db.host,
  user=config.db.user,
  password=config.db.password,
  database=config.db.name
)

cursor = db.cursor()
cursor.execute("create table if not exists users (firstName text, lastName text, birthDate text, telephone text, email text, address text, userName text, category text)")
db.commit()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("layout.html", show_error=False)

    # file = request.files.get("picture")
    first_name = request.form.get("firstName")
    last_name = request.form.get("lastName")
    birth_date = request.form.get("birthDate")
    telephone = request.form.get("telephone")
    email = request.form.get("email")
    address = request.form.get("address")
    user_name = request.form.get("userName")
    category = request.form.get("category")

    for value in [first_name, last_name, birth_date, telephone, email, address, user_name, category]:
        if len(value) == 0:
            return render_template("layout.html", show_error=True)
    cursor.execute("insert into users (firstName, lastName, birthDate, telephone, email, address, userName, category) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (first_name, last_name, birth_date, telephone, email, address, user_name, category))
    db.commit()

    telegram = {"grafiche": "https://t.me/joinchat/ty3nnfad2R5jMmJk", "video": "https://t.me/joinchat/Dutt5TvAZDA5M2Y0", "musica": "https://t.me/joinchat/df25lPGIEdswMWZk"}

    return redirect(telegram[category])

if __name__ == "__main__":
    app.run(port=config.port)
