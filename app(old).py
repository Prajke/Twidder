from flask import Flask, render_template, jsonify, request
import database_helper
app = Flask(__name__)

#class database:
#        db= "none"

db = database_helper.Database()

@app.route("/")
def index():
    return render_template('client.html')

@app.route("/test", methods=['POST'])
def switch():
    #db.postMessage("lars@mail.com", "user@mail.com", " hej user")

    if db.validateUser("user@mail.com"):
        return jsonify(success = True, message = "EXISTS!")
    else:
        return  jsonify(success = False, message = " error")

@app.route("/adduser")
def addUser():
    user = {
     "email":"user@mail.com",
     "firstname":"user",
     "familyname":"name",
     "gender":"male",
     "city":"c",
     "country":"c",
     "password": "123"
    }

    #database_helper.init_db()
    db.addUser(user)
    user2 = db.getUser(user["email"])
    return  user2["email"]

@app.route('/login', methods=['POST', 'GET'])
def login():
    return request.form

if __name__ == "__main__":
  app.run()
