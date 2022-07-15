from asyncio.windows_events import NULL
import cv2
import random
import os
import base64
import face_recognition
from PIL import Image
import io 
from flask import Flask, flash, redirect,Response, render_template, request, session
from flask_mysqldb import MySQL
from flask_session import Session


app = Flask(__name__)
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# connect to mysql server via XAMPP
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "users"
#changed default port 3306 to 4306 due to error connecting
app.config['MYSQL_PORT'] = 4306

mysql = MySQL(app)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#initialize webcam(default is zero) as global variable
camera1=cv2.VideoCapture(0)

#dataset sourcecode
#https://gist.github.com/Learko/8f51e58ac0813cb695f3733926c77f52
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

#face detection source code
#https://github.com/adarsh1021/facedetection/blob/master/detect_face_video.py
def camera0():
    camera1=cv2.VideoCapture(0)
    while True:
        success,frame = camera1.read()
        #allow webcam to behave like a mirror
        frame = cv2.flip(frame,1)
        if not success:
            break
        else:
            # convert to gray scale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Detects faces  in a frame
            faces = face_cascade.detectMultiScale(gray, 1.3, 4)
            for (x,y,w,h) in faces:
                # To draw a rectangle in a face
                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
                
#streaming webcam in flask
#https://stackoverflow.com/questions/54786145/web-cam-in-a-webpage-using-flask-and-python
            #convert into streaming data
            ret,buffer=cv2.imencode('.jpg',frame)
            frame=buffer.tobytes()
            # generate video frame by frame
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
@app.route('/webcam')
def video_feed():
    return Response(camera0(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/camera')
def camera():
    return render_template("camera.html")

@app.route('/recognition')
def recogntition():
    return render_template("recognition.html")


#face recognition
#https://pypi.org/project/face-recognition/#description
@app.route('/identification',methods=['POST','GET'])
def identification():
    if request.method == 'POST':
        camera1=cv2.VideoCapture(0)
        if request.form.get('proceed') == 'identify':
            result, image = camera1.read()
            if result:
                #save image file to the same directory opened in visual studio
                path = 'C:/Users/a/Desktop/Project' 
                cv2.imwrite(os.path.join(path,"logged_user.jpg"), image)
                
                img = cv2.imread('logged_user.jpg')
                # flip to RGB
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img_encoding = face_recognition.face_encodings(rgb_img)[0]
                
                db = mysql.connection.cursor()
                db.execute("SELECT photo FROM photos WHERE ID=(%s)",(session["user_id"],))
                profile_pic = db.fetchall()            
                image1 = profile_pic[0][0]
                db.close()
                # decodes BLOB type to 64 bit string
                data = base64.b64decode(image1)
                # convert into PIL image
                image2 = Image.open(io.BytesIO(data))
                #save as jpg file format
                image2 = image2.save("current_user.jpg")
                
                img2 = cv2.imread('current_user.jpg')
                # flip to RGB
                rgb_img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
                img_encoding2 = face_recognition.face_encodings(rgb_img2)[0]
                #compare if 2 images are the same person
                bool_result = face_recognition.compare_faces([img_encoding],img_encoding2)
                
                # convert result to str for condition to pass
                session["verified"] = str(bool_result[0])
                if str(bool_result[0]) == 'False':
                    message='Not verified'
                    camera1.release()
                    return render_template("login.html",message=message)
                else:
                    flash("Welcome")
                    camera1.release()
                    return redirect('/')
                                                
    elif request.method == 'GET':
        return render_template("recognition.html")

@app.route('/take_photo',methods=['POST','GET'])
def photo():
    if request.method == 'POST':
        camera1=cv2.VideoCapture(0)
        if request.form.get('photo') == 'Take_photo':
            result, image = camera1.read()
            if result:
                #save image file to the same directory opened in visual studio
                path = 'C:/Users/a/Desktop/Project' 
                cv2.imwrite(os.path.join(path,"taken_photo.jpg"), image)
                message='Account created'
                camera1.release()
                return render_template("camera.html",message=message)
  
    elif request.method == 'GET':
        return render_template("camera.html")
    
    
@app.route("/login", methods=["GET","POST"])
def login():
    
    session.clear()

    if request.method == "GET":
            return render_template("login.html")
    else:
        name = request.form.get("username")
        
        if not name:
            message="Please insert a Username"
            return render_template("login.html",message=message)

        password = request.form.get("password")
        
        if not password:
            message="Please insert a password"
            return render_template("login.html",message=message)
        
        db = mysql.connection.cursor()
        
        db.execute("SELECT * FROM profiles WHERE username=%s",(name,))
        username = db.fetchall()
        
        db.execute("SELECT passwords FROM profiles WHERE username=%s",(name,))
        password = db.fetchone()
        #check if username and password exists
        if (len(username)==1) or password:
            #take current user ID
            session["user_id"]=username[0][0]
            
            file = open('C:/Users/a/Desktop/Project/taken_photo.jpg','rb').read()
            #encode blob type as 64 bit string
            file = base64.b64encode(file)

            #check user has photo
            try:
                # store current user photo into the database
                sql_query = "INSERT INTO photos(ID,name,photo) VALUES (%s,%s,%s)"                
                db.execute(sql_query,(session["user_id"],name,file))
                mysql.connection.commit()
                db.close()
                return redirect('/recognition')

            except:
                pass
                
            return redirect('/recognition')
        else: 
            message="Invalid username or password"
            return render_template("login.html",message=message)
            
        
@app.route("/logout")
def logout():
    session["user_id"] = None
    session.clear()
    return redirect("/")            

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        name = request.form.get("username")
        
        if not name:
            message="Please insert a Username"
            return render_template("register.html",message=message)

        password = request.form.get("password")
        if not password:
            message="Please insert a password"
            return render_template("register.html",message=message)
        if len(password) < 8:
            message="Password must be at least 8 characters"
            return render_template("register.html",message=message)
            
        # list of special characters to be used in a loop
        s_characers = ["!", "@", "#", "$", "%", "^", "&", "*",
                    "(", ")", "_", "-", "+", "=", "{", "}", "[", "]", ".", "<", ">", "?", "/", ";", "'"]
        count = 0
        for special in s_characers:
            count += 1
            if special in password:
                break
            # check if any special characters are found
            elif count == len(s_characers):
                message="Insert at least 1 special character"
                return render_template("register.html",message=message)
         
        confirm_password = request.form.get("confirmation")   
        if password != confirm_password:
            message="Password confirmation do not match"
            return render_template("register.html",message=message)
        
        random_id = random.randint(1,999)
        
        db = mysql.connection.cursor()
        try:
            db.execute("INSERT INTO profiles(PersonID,username,passwords) VALUES (%s,%s,%s)",(random_id,name,password))
            mysql.connection.commit()
            db.close()
        except:
            message="Username or password already exits"
            return render_template("register.html",message=message)
        
                
        return redirect("/camera")
        
if __name__ == "__main__":
    app.run(debug=True)