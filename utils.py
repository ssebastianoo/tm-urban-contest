import ast

def get_data(c):
    c.execute("select data from tau_marin")
    data = c.fetchone()
    if not data:
        return None
    else:
        return ast.literal_eval(data[0])

def update_data(c, db_, data):
    c.execute("update tau_marin set data=%s", (str(data),))
    db_.commit()

def check_db(c):
    c.execute("create table if not exists tau_marin (data text)")
    data = get_data(c)
    if not data:
        data = {"votes": [], "user_votes": {}, "users": {}, "mode": "default"}
        c.execute("insert into tau_marin (data) values (%s)", (str(data),))
