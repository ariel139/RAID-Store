from flask import Flask, render_template, request
import sys, os
from importlib.machinery import SourceFileLoader
from User import *
from gui_Exceptions import *
from enums import Requests
import signal
import traceback
directory_path = 'E:\YUDB\project\RAID-Store'
file_path = os.path.join(directory_path, 'Query_Request.py')
query = SourceFileLoader('Query_Request', file_path).load_module()
SharedMemory = SourceFileLoader('SharedMemory', file_path).load_module()
Semaphore = SourceFileLoader('Semaphore', file_path).load_module()

from SharedMemory import SharedMemory
from Semaphore import Semaphore
app = Flask(__name__)

SERVER_PID = None
SHARED_MEMORY_NAME ='shared_memory'
SIGNAL_SEMAPHORE_NAME = 'sem_signal'
shr = SharedMemory(SHARED_MEMORY_NAME,query.DEFAULT_SIZE)
signal_sem = Semaphore(SIGNAL_SEMAPHORE_NAME,0,1)
user = None
@app.route("/")
def signin():
    return render_template('pages/signin.html')

@app.route('/signin', methods = ['POST'])
def sign_in():
    global user
    user_id = request.form.get('user_id')
    password = request.form.get('password')
    try:
        user = User(user_id=user_id, password=password, sign_in= True)
        return render_template('pages/upload.html')
    except UserNotExist:
        return render_template('pages/popup.html',message_head='User Error', message='User Does Not Exist')
    except WrongPassword:
        return render_template('pages/popup.html', message_head='Password Error', message='Wrong Password')

@app.route('/upload_file', methods=['POST'])
def process_file():
    global user
    try:
        if user is None: raise UserMustBeConnected()
        if 'file' in request.files:
            file = request.files['file']
            file_name = file.filename
            print(file_name)
            file_data = file.read()
            if len(file_data)>0 :
                data_stream = user.user_name.encode()+b'*'+file_data
                req = query.Query_Request(Requests.Add,file_name,data=data_stream, memory_view=shr)
                req_msg = req.build_req()
                signal_sem.release()
            
        else:
            return render_template('pages/popup.html', message_head='Server Upload Error', message='Could not upload file')
    except OverflowError:
        print('file to big. file size: ', str(len(file_data)))
        return render_template('pages/popup.html', message_head='Server Upload Error', message='Could not upload file. File To Large')
    except UserMustBeConnected:
        return render_template('pages/popup.html', message_head='Not Connected', message='Must sign in first')
    except Exception as err:
        traceback.print_exc()
        return render_template('pages/popup.html', message_head='Server Upload Error', message='Genreral server error')
   
    print('succesed')
    return render_template('pages/upload.html')

if __name__ == "__main__":
   
    app.run(debug=True)