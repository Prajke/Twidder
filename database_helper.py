import sqlite3, json


class Database:
    def __init__(self):
        self.db = sqlite3.connect("database.db", check_same_thread = False)
        self.cursor = self.db.cursor()
        #self.cursor.executescript("schema.sql")

    def __exit__(self):
        self.commit()
        self.connection.close()

    # Creates a userprofile in the database.
    def addUser(self,user):
        sql = "INSERT INTO USERS (email, firstname, familyname, gender, city, country, password) VALUES (?, ?,?,?,?,?,?)"
        val = (user["email"], user["firstname"], user["familyname"], user["gender"], user["city"], user["country"], user["password"])
        self.cursor.execute(sql, val)
        self.db.commit()
        return self.validateUser(user["email"])

    # Retrieves information about a userprofile.
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

    # Validates that it exists a userprofile with the provided email.
    def validateUser(self, email):
        user = self.getUser(email)
        if user == []:
            return False
        else:
            return True

    # Affirms that there exists a userprofile with the provided email and password.
    def checkPassword(self, email, password):
        sql = "SELECT * FROM USERS WHERE email = ? AND password = ? "
        val = (email, password,)
        self.cursor.execute(sql, val)
        row = self.cursor.fetchone()
        if row != None:
            return True
        else:
            return False

    # Updates the password for a userprofile.
    def changePassword(self, email , oldpassword, newpassword):
        if self.checkPassword(email,oldpassword):
            sql = "UPDATE users SET password = ? WHERE email = ? "
            val = (newpassword,email)
            self.cursor.execute(sql, val)
            self.db.commit()
            return self.checkPassword(email, newpassword)
        else:
            return False

    # Stores a message for a userprofile.
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

    # Retrieves all messages connected to the userprofile with the email provided.
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

    # Inserts the email and token of the userprofile that is active.
    # The active user list keeps track of all active users.
    def insertActiveUser(self,email,token):
        try:
            sql = "INSERT INTO activeusers (email, token) VALUES (?, ?)"
            val = (email, token)
            self.cursor.execute(sql, val)
            self.db.commit()
            return self.validateToken(token)
        except sqlite3.Error as e:
            return False
    # Removes a user from the active user list.
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
            return None
        else:
            return ' '.join(token)

    # Provides the token connected to the provided email.
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
    
    #  Provides the email connected to the provided token.
    def tokenToEmail(self,token):
        sql = "SELECT email FROM activeusers WHERE token = ?"
        val = (token,)
        self.cursor.execute(sql, val)
        self.db.commit()
        row = self.cursor.fetchone()
        if row == None:
            return None
        else:
            return ' '.join(row) #Converts from tuple to string

    # Validates the provided token.
    def validateToken(self, token):
        row = self.tokenToEmail(token)
        if row == None:
            return False
        else:
            return True

    # Validates if a certain userprofile is active.
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

    #Sum of the number of userprofiles.
    def nrUsers(self):
        sql = "SELECT COUNT(*) FROM users"
        self.cursor.execute(sql)
        self.db.commit()
        data = self.cursor.fetchone()
        return data[0]

    #Sum of userprofiles that are active.
    def nrActiveUsers(self):
        sql = "SELECT COUNT(*) FROM activeusers"
        self.cursor.execute(sql)
        self.db.commit()
        data = self.cursor.fetchone()
        return data[0]

    #Sum of userprofiles which has the provided gender.
    def nrGender(self, gender):
        ""
        sql = "SELECT COUNT(*) FROM  users WHERE gender= ?"
        val =(gender, )
        self.cursor.execute(sql, val)
        self.db.commit()
        data = self.cursor.fetchone()
        return data[0]
