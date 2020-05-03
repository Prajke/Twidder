from flask import Flask, render_template, request, url_for,jsonify
import json
import os
import database_helper
from base64 import b64encode
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer

app = Flask(__name__)
db = database_helper.Database()
websockets = {}

# Generates a unique token that is used as a key for authentication.
# The token gives access to the data in the databases by enabling functions in the server that retrieves and sends data to the database.
def generateToken():
    bytes = os.urandom(24)
    token =  str(b64encode(bytes).decode('utf-8'))
    if not db.validateToken(token):
        return token
    else:
        generateToken()

# Loads the "client.html" file when the standard route is called.
@app.route('/', methods = ['GET'])
def index():
    return render_template("client.html")

@app.route('/test', methods = ['GET'])
def test():
    return jsonify({"success": True, "message": "Test"})

# Inits a websocket which represents a session. 
# A session is created when a userprofile credentials are used to log in. 
# These sessions are used to prevent for userprofiles to be active simultaneously.
@app.route('/init_socket')
def init_socket():
    try:
        if request.environ.get('wsgi.websocket'):
            ws = request.environ['wsgi.websocket']
            data = json.loads(ws.receive())
            token = data['token']
            websockets[token] = ws
            ws.send(json.dumps({'success':True,'message':"It works"}))
            while True:
                data = ws.receive()
                if data is None:
                    del websockets[token]
                    ws.close()
                    return ""
            return ""
        else:
            return ""
    except:
        print("Exception in init_socket")

# Calls the update graph function
@app.route('/update_graph/', methods = ['GET'])
def init_update_graph():
    token = request.headers.get('Token')
    if db.validateToken(token):
        update_graph()
        return jsonify({"success": True, "message": "Updated graph"})
    else:
        return jsonify({"success": False, "message": "Token is not valid"})

# Updates the live graph with specific stastics by sending information through a websocket, thus creating a live graph.
def update_graph():
    data = json.dumps({
        "users" : db.nrUsers(),
        "activeusers": db.nrActiveUsers(),
        "males": db.nrGender("male"),
        "females": db.nrGender("female")})

    for key in websockets:
        websockets[key].send(json.dumps({"success": True, "message": "Update graph", "data": data}))


# Affirms if the provided credentials for the userprofile exists and is correct.
@app.route('/sign_in', methods = ['POST'])
def sign_in():
    data = request.get_json()
    name = data['email']
    password = data['password']
    if db.checkPassword(name, password):
        # Validates if the userprofile is already active, if so the other active session are terminated and signed out.
        if db.validateActiveUser(name):
            oldToken = db.emailToToken(name)
            ws = websockets[oldToken]
            del websockets[oldToken]
            db.removeActiveUser(name)
            ws.send(json.dumps({'success':False, 'message':"You have been logged out! "}))
            ws.close()
        token = generateToken()
        db.insertActiveUser(name,token)
        return jsonify({'success':True, 'message':"Signing in!",'data':token})
    else:
        return jsonify({'success':False, 'message':"Wrong username or password. Try again!"})

# Creates a new userprofile based on the information provided.
@app.route('/sign_up', methods=['POST'])
def sign_up():
    data = request.get_json()
    email = data['email']
    # Validate that the information provided is in a correct format.
    if "@" in email and len(email) > 4 and len(data['firstname']) > 1 and len(data['familyname']) > 1 and len(data['city']) > 1 and len(data['country']) > 1 and len(data['password']) > 7 and (data['gender'] == "male" or data['gender'] == "female" or data['gender'] == "none") :
        if  not db.validateUser(email):
            user = {
                "email": email,
                "password": data['password'],
                "firstname": data['firstname'],
                "familyname": data['familyname'],
                "gender": data['gender'],
                "city": data['city'],
                "country": data['country']
            }
            db.addUser(user)
            #update_graph()
            return jsonify({"success": True, "message": "Successfully created a new account. Logging in!"})
        else:
            return jsonify({"success": False, "message": "This email is already exists. Try another email!"})
    else:
        return jsonify({"success": False, "message": "The information provided is not correct. Try again!"})

# Signs out the active userprofile by removing the token.
@app.route('/sign_out', methods = ['POST'])
def sign_out():
    data = request.get_json()
    token = request.headers.get('Token')
    if db.validateToken(token):
        email = db.tokenToEmail(token)
        db.removeActiveUser(email)
        #update_graph();
        return jsonify({"success": True, "message": "Successfully signed out."})
    else:
        return jsonify({"success": False, "message": "Token is not valid"})

# Changes the password for a userprofile.
@app.route('/Change_password', methods=['POST'])
def Change_password():
    data = request.get_json()
    token = request.headers.get('Token')
    old_paswd = data['oldPassword']
    new_paswd = data['newPassword']
    email = db.tokenToEmail(token)
    if db.validateToken(token):
        if db.checkPassword(email, old_paswd):
            if db.changePassword(email,old_paswd,new_paswd):
                return jsonify({"success": True, "message": "Password changed."})
            else:
                return jsonify({"success": False, "message": "Wrong password."})
        else:
            return jsonify({"success": False, "message": "Wrong old password."})
    else:
        return jsonify({"success": False, "message": "Token is not valid"})

# Retrieve information about a userprofile by using the token to provide with a email.
@app.route('/Get_user_data_by_token/', methods=['GET'])
def Get_user_data_by_token(email = None):
    data = request.get_json()
    token = request.headers.get('Token')
    if db.validateToken(token):
        email = db.tokenToEmail(token)
        if db.validateUser(email):
            return jsonify({"success": True, "message":"User data retrieved.", "data":db.getUser(email) })
        else:
            return jsonify({"success": False, "message": "User don't exists"})
    else:
        return jsonify({"success": False, "message": "Token is not valid"})

# Retrieve information about a userprofile by using the provided email.
@app.route('/Get_user_data_by_email/<email>', methods=['GET'])
def Get_user_data_by_email(email = None):
    data = request.get_json()
    token = request.headers.get('Token')
    if db.validateToken(token):
        if db.validateUser(email):
            return jsonify({"success": True, "message": "User data retrieved.", "data": db.getUser(email)})
        else:
            return jsonify({"success": False, "message": "No such user."})
    else:
        return jsonify({"success": False, "message": "Token is not valid"})

# Retrieve messages from a userprofile by using the token to provide with a email.
@app.route('/Get_user_messages_by_token/', methods=['GET'])
def Get_user_messages_by_token():
    token = request.headers.get('Token')
    if db.validateToken(token):
        email = db.tokenToEmail(token)
        return jsonify({"success": True, "message": "User messages retrieved.", "data": db.getMessages(email)})
    else:
        return jsonify({"success": False, "message": "Token is not valid."})

# Retrieve messages from a userprofile by using the provided email.
@app.route('/Get_user_messages_by_email/<email>', methods=['GET'])
def Get_user_messages_by_email(email = None):
    data = request.get_json()
    token = request.headers.get('Token')
    if db.validateToken(token):
        if db.validateUser(email):
            return jsonify({"success": True, "message": "User messages retrieved.", "data": db.getMessages(email)})
        else:
            return jsonify({"success": False, "message": "No such user."})
    else:
        return jsonify({"success": False, "message": "Token is not valid."})

# Stores a message for the specific userprofile.
@app.route('/Post_message', methods=['POST'])
def Post_messages():
    data = request.get_json()
    token = request.headers.get('Token')
    toEmail = data['toEmail']
    content = data['content']
    fromEmail = db.tokenToEmail(token)
    if db.validateToken(token):
        if fromEmail != None:
            if toEmail == None:
                toEmail = fromEmail
        if db.validateUser(toEmail):
            if db.postMessage(fromEmail,toEmail,content):
                return jsonify({"success": True, "message": "Message posted!"})
            else:
                return jsonify({"success": False, "message": "No such user."})
    else:
        return jsonify({"success": False, "message": "Token is not valid."})

if __name__ == '__main__':

    app.run(debug=True)
