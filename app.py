from flask import *
import json
from werkzeug.utils import secure_filename
import mysql.connector
app = Flask(__name__)
from datetime import datetime

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="Cloud"
)

mycursor = mydb.cursor()


@app.route("/login",methods=['GET','POST']) 
def login() : 
  if request.method == 'POST' : 
    user = request.form["floatingInput"]
    password = request.form["floatingPassword"]
    res = make_response(render_template("test.html"))
    sql = f"select username,password from users where username='{user}' and password='{password}'"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    if len(result) == 1: 
      res.set_cookie('userID',user)
      return res
    else :
      return redirect("/",code=302)
  else : 
     return render_template("login.html")


#register handle
@app.route("/register",methods=['GET','POST']) 
def register() : 
  if request.method == 'POST' : 
    user = request.form["username"]
    password = request.form["password"]
    sql ="INSERT INTO USERS (username,password) VALUES(%s,%s)"
    val = (user, password)
    mycursor.execute(sql,val)
    mydb.commit()
    data = {
      "username":user,
      "First_name":"",
      "Last_name":"",
      "fcount":0,
      "files":[
      ],
      "notes":[]
    }
    f = open(f"{user}.json","w")
    f.close()
    with open(f'{user}.json', 'w') as f:
      json.dump(data, f, ensure_ascii=False)
    return redirect("/login",code=302)
  else : 
     return render_template("register.html")

@app.route("/")
def index() : 
  username = request.cookies.get('userID')
  if username == None : 
    return redirect("/login",code=302)
  json_content = ""
  with open(f'{username}.json','r') as jsonfile:
    json_content = json.load(jsonfile)
  return render_template("index.html",Username=json_content['username'],files=json_content['files'])

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      f.save(f"uploads/{secure_filename(f.filename)}")
      json_content = ""
      username = request.cookies.get('userID')
      with open(f'{username}.json','r') as jsonfile:
       json_content = json.load(jsonfile)
      json_content['files'].append(
        {
          "fileName":f.filename,
          "date": datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
          }
      )
      with open(f'{username}.json','w') as jsonfile:
           json.dump(json_content, jsonfile) 
      return redirect("/",code=302)
      
@app.route('/logout')
def logout() : 
  res = make_response(render_template("index.html"))
  res.set_cookie('userID','',expires=0)
  return redirect("/login",code=302)

@app.route("/profile") 
def profile() : 
  username = request.cookies.get('userID')
  if username == None : 
    return redirect("/login",code=302)
  with open(f'{username}.json','r') as jsonfile:
       json_content = json.load(jsonfile)
  
  return render_template("profile.html",Username=username,data=json_content)

@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory("uploads/", filename)
@app.route("/update",methods=['GET','POST'])
def update() :
  if request.method == 'POST' :
    username = request.cookies.get('userID')
    First_name = request.form['fname']
    Last_name = request.form['lname']
    with open(f'{username}.json','r') as jsonfile:
       json_content = json.load(jsonfile)
    json_content['First_name'] = First_name
    json_content['Last_name'] = Last_name
    with open(f'{username}.json','w') as jsonfile:
           json.dump(json_content, jsonfile) 
    return redirect("/profile",code=302)
@app.route("/notes")
def notes() :
  username = request.cookies.get('userID')
  with open(f'{username}.json','r') as jsonfile:
       json_content = json.load(jsonfile)
  return render_template("notes.html",Username=username,notes=json_content["notes"])
@app.route("/addnotes",methods=['GET','POST'])
def addnote() :
   username = request.cookies.get('userID')
   if request.method == 'POST' :
     title = request.form['title']
     note  = request.form['note']
     f = open(f"notes/{title}.txt","w")
     f.write(note)
     f.close()
     with open(f'{username}.json','r') as jsonfile:
       json_content = json.load(jsonfile)
     json_content['notes'].append(
       {
         "title":title,
         "note":f"{title}.txt"
       }
     )
     with open(f'{username}.json','w') as jsonfile:
           json.dump(json_content, jsonfile) 
   return redirect("/notes",code=302)
@app.route('/notes/<filename>')
def notehref(filename):
    return send_from_directory("notes/", filename)
@app.route("/fileupdate",methods=['GET','POST'])
def fileupdate() : 
  if request.method == 'POST' :
    rr = request.form['options']
    name = request.form['filename']
    print(name)
    return redirect("/",code=302)
if __name__ == "__main__":
    app.run(debug=True)