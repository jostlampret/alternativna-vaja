from flask import Flask, render_template, redirect, request, session
from tinydb import TinyDB, Query

db = TinyDB("database/db1.json")
users = db.table("users")
zapiski = db.table("zapiski")

User = Query()
Zapis = Query()

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

app.secret_key = "123456789"



@app.route("/")
def index():
    if "uporabnik" not in session:
        return redirect("/login")
    moji_zapiski = zapiski.search(Zapis.username == session["uporabnik"])
    return render_template("templates1.html", zapiski=moji_zapiski, zapis=None) 


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if users.search(User.username == username):
            return render_template("register.html", napaka="Ime je že zasedeno.")

        users.insert({"username": username, "password": password})
        return redirect("/login")

    return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = users.search((User.username == username) & (User.password == password))

        if user:
            session["uporabnik"] = username
            return redirect("/")
        else:
            return render_template("login.html", napaka="Napačno ime ali geslo.")

    return render_template("login.html")



@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")



@app.route("/nov", methods=["GET", "POST"])
def nov():
    if "uporabnik" not in session:
        return redirect("/login")
    if request.method == "POST":
        naslov  = request.form["naslov"]
        vsebina = request.form["vsebina"]
        zapiski.insert({"naslov": naslov, "vsebina": vsebina, "username": session["uporabnik"]})
        return redirect("/")
    moji_zapiski = zapiski.search(Zapis.username == session["uporabnik"])
    return render_template("templates1.html", zapiski=moji_zapiski, zapis=None)



@app.route("/uredi/<int:id>", methods=["GET", "POST"])
def uredi(id):
    if "uporabnik" not in session:
        return redirect("/login")
    zapis = zapiski.get(doc_id=id)
    if request.method == "POST":
        naslov  = request.form["naslov"]
        vsebina = request.form["vsebina"]
        zapiski.update({"naslov": naslov, "vsebina": vsebina}, doc_ids=[id])
        return redirect("/")
    moji_zapiski = zapiski.search(Zapis.username == session["uporabnik"])
    return render_template("templates1.html", zapiski=moji_zapiski, zapis=zapis)



@app.route("/brisi/<int:id>")
def brisi(id):
    if "uporabnik" not in session:
        return redirect("/login")
    zapiski.remove(doc_ids=[id])
    return redirect("/")



app.run(debug=True)