from flask import Flask, render_template, redirect
import sqlite3

conn = sqlite3.connect("database/db1.sqlite3")
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXSISTS PODATKI(ID INTEGER PRIMARY KEY AUTOINCREMENT, USERNAME TEXT, PASSWORD TEXT)")
cursor.execute("CREATE TABLE IF NOT EXSISTS BESEDILO(ID INTEGER PRIMARY KEY AUTOINCREMENT, ZAPISKI TEXT, USER_ID INTEGET)")

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static1"
)

@app.route("/")
def hello_world():
        return render_template("templates1.html")


@app.route("/register", methods = ["GET","POST"])
def register():
    if request.method == "POST":
        username=request.form["username"]
        password=request.form["password"]
        
       if 

        cursor.execute("INSERT INTO PODATKI(USERNAME,PASSWORD) VALUES ("{username}","{password}")")
        return redirect("/login")      

    return render_template("register.html")


@app.route("/login", methods = ["GET","POST"])
def login():

    if request.method == "POST":
        username=request.form["username"]
        password=request.form["password"]


app.run(debug=True)