from flask import Flask, render_template, request, redirect, url_for, abort
import sys, os
from importlib.machinery import SourceFileLoader
from User import *
from gui_Exceptions import *
from enums import Requests
import pickle
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
SERVER_SHARED_MEMORY_NAME ='server_shared_memory'
SERVER_SEMAPHORE_NAME = 'server_sem_signal'
GUI_SHARED_MEMORY_NAME ='gui_shared_memory'
GUI_SEMAPHORE_NAME = 'gui_sem_signal'

gui_shr = SharedMemory(GUI_SHARED_MEMORY_NAME,query.DEFAULT_SIZE)
gui_sem = Semaphore(GUI_SEMAPHORE_NAME,0,1)
server_shr = SharedMemory(SERVER_SHARED_MEMORY_NAME,query.DEFAULT_SIZE)
server_sem = Semaphore(SERVER_SEMAPHORE_NAME,0,1)

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
app.route('/upload_file_page',methods=['GET','POST'])
def upload_file():
    return render_template('pages/upload.html')
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
                req = query.Query_Request(Requests.Add_File,file_name,data=data_stream, memory_view=gui_shr)
                req_msg = req.build_req()
                gui_sem.release()
                server_sem.acquire()
                response = query.Query_Request.analyze_request(server_shr)
                res = pickle.loads(response.data)
                return render_template('pages/popup.html', message_head=res[0], message=res[1])
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
@app.route('/file_explorer', methods = ['GET', 'POST'])
def explorar():
    try:
        if user is None: raise UserMustBeConnected()
        req = query.Query_Request(Requests.Files_List, memory_view=gui_shr)
        req_msg = req.build_req()
        gui_sem.release()
        server_sem.acquire()
        response = query.Query_Request.analyze_request(server_shr)
        res = pickle.loads(response.data)
        return render_template('pages/explorar.html', records=res[1])
    except UserMustBeConnected:
       return render_template('pages/popup.html', message_head='Not Connected', message='Must sign in first')

@app.route('/download_fle',methods=['GET'])
def download_file():
    try:
        if user is None: raise UserMustBeConnected()    
        file_id = request.args.get('file_id')
        print(file_id)
        req = query.Query_Request(Requests.Retrive_File,file_id, memory_view=gui_shr)
        req_msg = req.build_req()
        gui_sem.release()
        server_sem.acquire()
        response = query.Query_Request.analyze_request(server_shr)
        res = pickle.loads(response.data)
        if res[0] == 'Success':
            return res[1]
        else:
            raise ErrorInRecivingFile()
    except UserMustBeConnected:
        abort(401, description="must be conncted with the right use to make the request")
    except ErrorInRecivingFile:
        abort(505, description="must be conncted with the right use to make the request")



@app.route('/settings', methods = ['GET', 'POST'])
def settings():
    return render_template('pages/popup.html', message_head='Not implamented', message='settings no implament')

@app.route('/dash_board', methods = ['GET', 'POST'])
def dashboard():
    return render_template('pages/popup.html', message_head='Not implamented', message='dashboard no implament')

if __name__ == "__main__":
   
    app.run(debug=True)