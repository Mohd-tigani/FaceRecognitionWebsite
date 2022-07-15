
# Logging in the website using Face recognition

### Description:

The purpose of this project is to add an extra layer of security when a user logs in into a website using facial recognition.
The project is a web app created by using HTML,Flask,Python, OpenCv and MYSQL.

The project allows the user to create an account by inserting their username, password and uploading their face image using their webcam. Once created, user information is added into a database using MYSQL queries.

Once user inserts their username and password, he will be redirected to a page where the user is required take a photo of his face using webcam once he sees a bounding box created made from OpenCV. Once Photo is taken, its encoded as 64 bit string and it is stored in the database as a BLOB file as soon as the user logs in.

So when user visits the website again, not only will the user insert his username and password, but will have to use his face to identify the user in order to access the websites features. His face will be identified using a python package called face_recognition and this library will compare the current face of the user from the webcam and the other face of the logged user from the database extracted using MYSQL quries. If the comparison is True the user is logged in, otherwise user is redirected to the login page to try again


### folders
Project contains the following folders:

**.vscode**: modifying or using default setting on visual studio

**static**: Designing the web app using javascript

**templates**: templates folder has 6 htmls files: camera,index,layout,login,recognition and register.

**app.py**: Where the required python packages are used to implement the flask app.

**requirements.txt**: list of required Python packages and additional information needed for this project to work

**user.sql**: User database that contains 2 tables used for this project

### face_recognition
This line of code shown below 

source: https://pypi.org/project/face-recognition/#description

Allows the user to compare between an known image and an unknown image. If both are equal result shall yield it to be True otherwise its will be false.
the result is generate in the code shown below:

import face_recognition

known_image = face_recognition.load_image_file("user.jpg")
unknown_image = face_recognition.load_image_file("logged_user.jpg")

known_encoding = face_recognition.face_encodings(known_image)[0]
unknown_encoding = face_recognition.face_encodings(unknown_image)[0]

results = face_recognition.compare_faces([Known_encoding], unknown_encoding)

visit the source link for more information.

### xampp
Source: https://www.apachefriends.org/download.html

downloading xampp is needed for this project to work so it can connect to the mysql server in order to use its database.

Note: you may require to change ports since the default port 3306 doesnt usually work all the time.














