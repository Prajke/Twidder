import sqlite3, json


class Database:
    def __init__(self):
        self.db = sqlite3.connect("database.db", check_same_thread = False)
        self.cursor = self.db.cursor()
        #self.cursor.executescript("schema.sql")

    def __exit__(self):
        self.commit()
        self.connection.close()

    #def init_db():
    #    return sqlite3.connect("database.db")

    #works#
    def addUser(self,user):
        sql = "INSERT INTO USERS (email, firstname, familyname, gender, city, country, password) VALUES (?, ?,?,?,?,?,?)"
        val = (user["email"], user["firstname"], user["familyname"], user["gender"], user["city"], user["country"], user["password"])
        self.cursor.execute(sql, val)
        self.db.commit()
        return self.validateUser(user["email"])

    #works#
    def getUser(self, email):
        sql = "SELECT * FROM USERS WHERE email = ? "
        val = (email,)
        self.cursor.execute(sql, val)
        row = self.cursor.fetchone()
        if row == None:
            user = []
            return user
        user = {
            "email":row[0],
            "firstname":row[1],
            "familyname":row[2],
            "gender": row[3],
            "city": row[4],
            "country": row[5],
            "password": row[6]
        }
        return user

    #works#
    def validateUser(self, email):
        user = self.getUser(email)
        if user == []:
            return False
        else:
            return True

    #works#
    def checkPassword(self, email, password):
        sql = "SELECT * FROM USERS WHERE email = ? AND password = ? "
        val = (email, password,)
        self.cursor.execute(sql, val)
        row = self.cursor.fetchone()
        if row != None:
            return True
        else:
            return False

    #works#
    def changePassword(self, email , oldpassword, newpassword):
        if self.checkPassword(email,oldpassword):
            sql = "UPDATE users SET password = ? WHERE email = ? "
            val = (newpassword,email)
            self.cursor.execute(sql, val)
            self.db.commit()
            return self.checkPassword(email, newpassword)
        else:
            return False

    #works#
    def postMessage(self, sender, reciever, message):
        sql = "CREATE TABLE IF NOT EXISTS '"+reciever+"' (sender TEXT NOT NULL, message	TEXT NOT NULL)"
        self.cursor.execute(sql)
        sql = "INSERT INTO '"+reciever+"' (sender, message) VALUES (?, ?)"
        val = (sender, message)
        self.cursor.execute(sql, val)
        self.db.commit()
        if self.cursor.rowcount == 0 :
            return False
        else:
            return True

    #works#
    def getMessages(self, email):
        try:
            #print (email)
            sql = "SELECT * FROM '"+email+"'"
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()

            messages = []
            for row in rows:
                message = {'sender':row[0], 'message':row[1]}
                jsonmessage = json.dumps(message)
                messages.append(jsonmessage)
            #jsonmessages = json.dumps(messages)

            return messages
        except sqlite3.Error as e:
            return []

    #works#
    def insertActiveUser(self,email,token):
        try:
            sql = "INSERT INTO activeusers (email, token) VALUES (?, ?)"
            val = (email, token)
            self.cursor.execute(sql, val)
            self.db.commit()
            return self.validateToken(token)
        except sqlite3.Error as e:
            return False
    #works#
    def removeActiveUser(self, email):
        sql = "SELECT token FROM activeusers WHERE email = ?"
        val = (email,)
        self.cursor.execute(sql,val)
        token = self.cursor.fetchone()

        sql = "DELETE FROM activeusers WHERE email = ?"
        val = (email,)
        self.cursor.execute(sql, val)
        self.db.commit()
        if token == None:
            return None;
        else:
            return ' '.join(token);

    def emailToToken(self,email):
        sql = "SELECT token FROM activeusers WHERE email = ?"
        val = (email,)
        self.cursor.execute(sql, val)
        self.db.commit()
        row = self.cursor.fetchone()
        if row == None:
            return None;
        else:
            return ' '.join(row)
    #works
    def tokenToEmail(self,token):
        sql = "SELECT email FROM activeusers WHERE token = ?"
        val = (token,)
        self.cursor.execute(sql, val)
        self.db.commit()
        row = self.cursor.fetchone()
        if row == None:
            return None;
        else:
            return ' '.join(row) #Converts from tuple to string

    #works#
    def validateToken(self, token):
        row = self.tokenToEmail(token)
        if row == None:
            return False
        else:
            return True

    def validateActiveUser(self, email):
        sql = "SELECT * FROM activeusers WHERE email = ?"
        val = (email,)
        self.cursor.execute(sql, val)
        self.db.commit()
        row = self.cursor.fetchone()
        if row == None:
            return False
        else:
            return True
    def nrUsers(self):
        sql = "SELECT COUNT(*) FROM users"
        self.cursor.execute(sql)
        self.db.commit()
        data = self.cursor.fetchone()
        return data[0]

    def nrActiveUsers(self):
        sql = "SELECT COUNT(*) FROM activeusers"
        self.cursor.execute(sql)
        self.db.commit()
        data = self.cursor.fetchone()
        return data[0]

    def nrGender(self, gender):
        ""
        sql = "SELECT COUNT(*) FROM  users WHERE gender= ?"
        val =(gender, )
        self.cursor.execute(sql, val)
        self.db.commit()
        data = self.cursor.fetchone()
        return data[0]
