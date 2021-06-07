import ast, config, mysql.connector

class DataBase:
    def __init__(self, database):
        self.db = database

    def connect(self):
        try:
            self.db = mysql.connector.connect(host=config.db.host, user=config.db.user, password=config.db.password, database=config.db.name)
        except (MySQLdb.Error, MySQLdb.Warning) as e:
            print(e)
            self.db = None
        return self.db

    def get_data(self):
        try:
            cursor = self.db.cursor()
        except (AttributeError, MySQLdb.OperationalError):
            self.connect()
            cursor = self.db.cursor()
        cursor.execute("select data from tau_marin")
        data = cursor.fetchone()
        if not data:
            return None
        else:
            return ast.literal_eval(data[0])

    def update_data(self, data):
        try:
            cursor = self.db.cursor()
        except (AttributeError, MySQLdb.OperationalError):
            self.connect()
            cursor = self.db.cursor()
        cursor.execute("update tau_marin set data=%s", (str(data),))
        self.db.commit()

    def check_db(self):
        try:
            cursor = self.db.cursor()
        except (AttributeError, MySQLdb.OperationalError):
            self.connect()
            cursor = self.db.cursor()
        cursor.execute("create table if not exists tau_marin (data text)")
        cursor.execute("create table if not exists users (fileName text, firstName text, lastName text, birthDate text, telephone text, email text, address text, city text, province text, userName text, category text, parentFirstName text, parentLastName text, parentIdCard int, parentTelephone text, parentEmail text)")
        data = self.get_data()
        if not data:
            data = {"votes": [], "user_votes": {}, "users": {}, "mode": "default"}
            cursor.execute("insert into tau_marin (data) values (%s)", (str(data),))
        self.db.commit()

    def query(self, sql):
        try:
            cursor = self.db.cursor()
        except (AttributeError, MySQLdb.OperationalError):
            self.connect()
            cursor = self.db.cursor()
        cursor.execute(sql)
        self.db.commit()
