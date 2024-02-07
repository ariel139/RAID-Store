from flask import Flask, render_template, request
import sys
from User import User
from app.gui_Exceptions import *
app = Flask(__name__)

@app.route("/")
def signin():
    return render_template('pages/signin.html')

@app.route('/signin', methods = ['POST'])
def sign_in():
    user_id = request.form.get('user_id')
    password = request.form.get('password')
    try:
        user = User(user_id=user_id, password=password, sign_in= True)
        return render_template('pages/upload.html')
    except UserNotExist:
        return render_template('pages/popup.html',message_head='User Error', message='User Does Not Exist')
    except WrongPassword:
        return render_template('pages/popup.html', message_head='Password Error', message='Wrong Password')
    

if __name__ == "__main__":
    app.run(debug=True)