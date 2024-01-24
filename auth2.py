from flask import Flask, request, render_template, session, redirect, url_for,flash,jsonify
from flask_session import Session
from flask_socketio import join_room,leave_room,send,emit,SocketIO
from db import *
from mail import *
from genOTP import *
import configparser
from flask_socketio import SocketIO,join_room, leave_room,send
import random
from datetime import datetime
from string import ascii_uppercase
import time

mydb = MongoDB("ChatUserData","data")
db=MongoDB("Rooms","info")

chat={}
message_queue = {}
def generate_unique_code():
    timestamp = int(time.time() * 1000)  # Get current timestamp in milliseconds
    random_part = random.randint(1000, 9999)  # Add a random 4-digit number
    
    unique_code = f"{timestamp}{random_part}"
    return str(unique_code)

app = Flask(__name__)
        # Initialize SocketIO within the App constructor

socket=SocketIO(app)   
# Define a route and associated function

messages=[]

@app.route("/")
def index():
    if "username" in session:
        username = session["username"]
        users=mydb.fetch()
        usernames=[user["username"]for user in users]
        
        return render_template("home.html",username=username,contacts=usernames)
        
    return "You are not logged in. <a href='/register'>Register</a> <a href='/login'>Login existing users</a>"


@app.route("/chat/<name>")
def chatWith(name):
    session['contact'] = name 
    username = session["username"]
    contact=name
    users =sorted([username, contact])
    chatID=f'{users[0]}_{users[1]}'
    return render_template("room.html",contact=contact,messages=messages,room=chatID)


@socket.on('connect')
def handle_connect():
    if "username" in session: 
        username = session["username"]
        contact = session.get("contact")
        users =sorted([username, contact])
        chatID=f'{users[0]}_{users[1]}'
        emit('sendChatID', {'chat_room_id': chatID})

        join_room(chatID)  # Join a room named after the conversation identifier
        print(f"{username} connected to conversation {chatID}")


    

@socket.on('message')
def handle_message(data):
    sender = session["username"]
    contact = session.get("contact")
    users =sorted([sender, contact])
    chatID=f'{users[0]}_{users[1]}'
    
    now = datetime.now()
    current_time = now.strftime("%I:%M %p")

    content = {
        "name": sender,
        "message": data['message'],
        "time": current_time,
        "chatID":chatID
    }
    
    # Emit the message directly to the conversation room
    socket.emit('message', content, room=chatID,include_self=False)

    messages.append(content)
    print(f"{sender} to {contact}: {content['message']}")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]      
        pwd=mydb.hashit(password)
        otp=generate_otp()
        # Generate and send an OTP to the user's email
        r=sendMail(email,otp)
        flash(r)
# Store the OTP in the session for verification
        session['otp'] = otp
    # Store other user data in the session for later use
        session['user_data'] = {"username": username, "email": email, "password": pwd}
        
    return render_template("register.html")

        
@app.route("/verify", methods=["GET", "POST"])
def verify():
         if request.method == "POST":
            eotp = request.form["otp"]
            if(verifyMail(session['otp'],eotp)):
             info=session['user_data']
             mydb.insert(info)
             flash("Registration successful. You can now log in.")
             return redirect(url_for("login"))
         flash("Incorrect otp/email id entered!")
         return render_template("register.html")
         

        
@app.route("/login", methods=["GET", "POST"])
def login():
         if request.method == "POST":
          username = request.form["username"]
          password=request.form["pwd"]
          session["username"] = username
          hashpass = mydb.fetch({"username":username})[0]["password"]
          if mydb.verifyHash(password,hashpass):
           
           return redirect(url_for("index"))
          else:
           flash("Incorrect username/password!")
         return render_template("login.html")

           
@app.route("/logout")
def logout():
           session.pop("username", None)
           return redirect(url_for("index"))
             
    
config = configparser.ConfigParser()
config.read('key_config.ini')
# Configure session
app.config["SESSION_TYPE"] = "filesystem"  
Session(app)
#Secret key for session
app.secret_key = config['SECTION']["key"]


if __name__ == '__main__':
    socket.run(app,debug=True,host="0.0.0.0", ssl_context="adhoc")