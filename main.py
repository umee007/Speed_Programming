from flask import Flask,render_template,request,redirect,jsonify,Response
from User import *
from Functions import *
import os

USER_DATABASE=Load_User_Database()
QUESTION_DATABASE=Load_Question_Database()

tmp_user_name=''



app=Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True 

@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


@app.route('/privacy_policy/Leafy')
def Leafy():
    return render_template('leafy_policy.html')

@app.route('/volley', methods=['GET', 'POST'])
def f():
    content = request.get_json()
    print (content['data'])
    num=int(content['data'])+1

    return jsonify({'return':num})


@app.route('/privacy_policy/T_Drive')
def T_Drive():
    return render_template('T_Drive.html')

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/main_page',methods=['POST','GET'])
def main_page():
    global tmp_user_name

    if request.method=='POST':
        global USER_DATABASE,QUESTION_DATABASE

        USER_DATABASE=Load_User_Database()

        Username=request.form['Username']
        Password=request.form['Password']



        if (Username in USER_DATABASE) and USER_DATABASE[Username].Password==Password:
            status='Ok'
            user=USER_DATABASE[Username]
        elif (Username in USER_DATABASE) and USER_DATABASE[Username].Password!=Password:
            status='Wrong'
            user=USER_DATABASE[Username]
        elif Username not in USER_DATABASE:
            status='New'
            user=User(Username,Password)
            Write_User_Database(USER_DATABASE,user)

        #print(user)

        tmp_user_name=Username

        return render_template('main_page.html',User=user,Status=status,Question=QUESTION_DATABASE)
    if request.method=='GET':
        if tmp_user_name!='':
            USER_DATABASE=Load_User_Database()
            return render_template('main_page.html',User=USER_DATABASE[tmp_user_name],Status='Ok',Question=QUESTION_DATABASE)
    return redirect('/')


@app.route('/check',methods=['POST','GET'])
def check():
    global USER_DATABASE,QUESTION_DATABASE

    USER_DATABASE=Load_User_Database()


    if request.method=='POST':
        file=request.files['file']
        index=str(request.form['index'])
        key=str(request.form['userKey'])

        user=USER_DATABASE[key]

        if index in user.Progress:
            return 'Already Attempted'



        file.save('/home/ysvg2tafy/mysite/'+key+file.filename)
        Py='/home/ysvg2tafy/mysite/'+key+file.filename
        Input="/home/ysvg2tafy/mysite/Questions/{}/input.txt".format(index)
        Output='/home/ysvg2tafy/mysite/'+key+"out.txt"

        os.system('chmod a=rwx {}'.format(Py))

        os.system('python3 {} < {} > {}'.format(Py,Input,Output))

        actual="/home/ysvg2tafy/mysite/Questions/{}/output.txt".format(index)

        f=open(actual,'r')
        content1=f.read().strip()
        f.close()

        f=open(Output,'r')
        content2=f.read().strip()
        f.close()


        if content1==content2:
            success=True
            user.Score+=10
            user.Progress.add(index)

        else:
            success=False
            user.Score-=5

        os.remove(Output)
        os.remove(Py)



        #print(user.Username)
        #print(user.Score)
        #print(user.Progress)

        Write_User_Database(USER_DATABASE,user)


        return render_template('check.html',Success=success,Index=index,Score=user.Score)
    else:
        return  redirect('/')


@app.route('/rank_list.html',methods=['GET'])
def rank_list():
    if request.method=='GET':
        global USER_DATABASE
        USER_DATABASE=Load_User_Database()
        data=Prepare_rank_list(USER_DATABASE)
        return render_template('rank_list.html',Data=data)
    else:
        return redirect('/')

@app.route('/instruction.html')
def instruction():
    return render_template('instruction.html')



if __name__=='__main__':
    app.run(app.run(debug=True,host='0.0.0.0', port=8081))
