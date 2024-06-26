import json
from flask import Flask, render_template, request, redirect, url_for, abort, Response
import sys, os
from importlib.machinery import SourceFileLoader
from User import *
from gui_Exceptions import *
from enums import Requests
import pickle
import traceback
from side import is_english, printable
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
    #TODO: check sign-in 
    if  User.check_if_users_exsists():
        return render_template('pages/signin.html')
    else:
        return redirect(url_for('sign_up'))

@app.route('/sign_up', methods=['POST', 'GET'])
def sign_up():
    global user
    print(request.method)
    if request.method == 'get'.upper():
        return render_template('pages/sign-up.html')
    elif request.method == 'post'.upper():
        name = request.form.get('name')
        user_id = request.form.get('user_id')
        password_1 = request.form.get('password-1')    
        password_2 = request.form.get('password-2')    
        if password_1 != password_2:
            return render_template('pages/popup.html',message_head='Error', message='Passwords Dont Match')
        else:
            try:
                user = User(user_id,password_1,name)
                return redirect('/dash_board')
            except Exception as err:
                traceback.print_exc()
                return render_template('pages/popup.html',message_head='Error', message=err)
    
@app.route('/error', methods=['GET'])
def error():
    global user
    if request.method == 'post'.upper():
        ttl = request.form['error title']
        content = request.form['error content']
        return render_template('pages/popup.html',message_head=ttl, message=content)

@app.route('/signin', methods = ['POST'])
def sign_in():
    global user
    user_id = request.form.get('user_id')
    password = request.form.get('password')
    try:
        user = User(user_id=user_id, password=password, sign_in= True)
        return redirect('/dash_board')
    except UserNotExist:
        return render_template('pages/popup.html',message_head='User Error', message='User Does Not Exist')
    except WrongPassword:
        return render_template('pages/popup.html', message_head='Password Error', message='Wrong Password')

@app.route('/upload_file_page',methods=['GET'])
def upload_file():
    if request.method == 'GET':
        if user is not None:
            return render_template('pages/upload.html', user=user)
        else:
            return render_template('pages/popup.html', message_head='Not Connected', message='Must sign in first')
    else:
        abort(405)


@app.route('/upload_file', methods=['POST','GET'])
def process_file():
    global user
    try:
        if user is None: raise UserMustBeConnected()
        if 'file' in request.files:
            file = request.files['file']
            file_name = file.filename
            if not is_english(file_name):
                return render_template('pages/popup.html', message_head='General Error', message=f'file name must have only printable chars:\n{printable}')
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
    return redirect('/upload_file_page')

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
        raw_records = res[1]
        filter_recs_method = lambda record: record[4] ==user.user_name
        filtered_data = list(filter(filter_recs_method,raw_records))
        return render_template('pages/explorar.html', records=filtered_data, user=user)
    except UserMustBeConnected:
       traceback.print_exc()
       return render_template('pages/popup.html', message_head='Not Connected', message='Must sign in first')
    except Exception as err:
       traceback.print_exc()
       return render_template('pages/popup.html', message_head='Error', message=traceback.format_exc())


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
        error_message = json.dumps({'Message': f'error in reciving file: {str(res[1])}'})
        abort(Response(error_message,505))



@app.route('/settings', methods = ['GET', 'POST'])
def settings():
    global user
    if user is not None:
        print(user.full_name)
        return render_template('pages/settings.html', user=user)
    else:
        return render_template('pages/popup.html', message_head='Error', message='Must sign in ')

@app.route('/dash_board', methods = ['GET', 'POST'])
def dashboard():
    if user is not None:
        g_req = query.Query_Request(Requests.Info, memory_view=gui_shr, data=user.user_name.encode())
        req_msg = g_req.build_req()
        gui_sem.release()
        server_sem.acquire()
        response = query.Query_Request.analyze_request(server_shr)
        #TODO: error handeling
        # actual_data = pickle.loads(response.data[0])
        real = pickle.loads(response.data)[1]
    
        return render_template('pages/dashboard.html', data=json.dumps(real),user=user)
    else:
        return render_template('pages/popup.html', message_head='Error', message='Must sign in ')

@app.route('/change-password',methods = ['GET', 'POST'])
def change_password():
    if user is not None:
        if request.method == 'GET':
            return render_template('pages/change_password.html', user=user)
        elif request.method == 'POST':
            current_pass = request.form.get('password-0')
            new_pass_1 = request.form.get('password-1')
            new_pass_2= request.form.get('password-2')
            if new_pass_1!= new_pass_2:
                return render_template('pages/popup.html', message_head='Error', message='new passwords dont match')
            if user.password != current_pass:
                return render_template('pages/popup.html', message_head='Error', message='Current password dont match')
            user.change_password(new_pass_1)
            return render_template('pages/popup.html', message_head='Success', message='Password changed')
        

@app.route('/signout')
def sign_out():
    global user
    if user is not None:
        user=None
        return redirect('/')
    else:
        return render_template('pages/popup.html', message_head='Error', message='User Not even signed')

@app.route('/delete_file', methods = ['GET'])
def delete_file():
    global user
    if user is  None:
        return redirect('/')
    else:
        print('got here')
        file_id = request.args.get('file_id')
        # return 'file id = ' + str(file_id)
        req = query.Query_Request(Requests.Delete_File,str(file_id), memory_view=gui_shr)
        req_msg = req.build_req()
        gui_sem.release()
        server_sem.acquire()
        response = query.Query_Request.analyze_request(server_shr)
        response_data = pickle.loads(response.data)
        if {response_data[0]}=='good':
            return 'delted file succefuly'
        else:
            return f'status: {response_data[0]}\ndescription: {response_data[1]}'

if __name__ == "__main__":
   
    app.run(debug=True)