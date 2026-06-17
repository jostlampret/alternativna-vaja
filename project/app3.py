from flask import Flask, render_template, request, redirect, session, jsonify
from tinydb import TinyDB, Query

app = Flask(__name__, template_folder="templates3", static_folder="static")
app.secret_key = "secret4321"

db = TinyDB("database/db2.json")
users = db.table("users")
listings = db.table("listings")
requests_table = db.table("join_requests")

User = Query()
Listing = Query()
JoinRequest = Query()


# --- HOME ---
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")


# --- REGISTER ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        game = request.form.get("game", "")

        if users.search(User.username == username):
            return render_template("register.html", error="Uporabnik že obstaja!")

        users.insert({
            "username": username,
            "password": password,
            "game": game
        })
        return redirect("/login")

    return render_template("register.html", error=None)


# --- LOGIN ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = users.get(User.username == username)

        if user and user["password"] == password:
            session["user"] = username
            session["user_id"] = users.search(User.username == username)[0].doc_id
            return redirect("/dashboard")

        return render_template("login.html", error="Napačno uporabniško ime ali geslo")

    return render_template("login.html", error=None)


# --- LOGOUT ---
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# --- DASHBOARD ---
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    all_listings = listings.all()

    # enrich with username
    enriched = []
    for l in all_listings:
        owner = users.get(User.username == l["owner"])
        req_count = len(requests_table.search(JoinRequest.listing_id == l["id"]))
        enriched.append({**l, "req_count": req_count})

    return render_template("dashboard.html", user=session["user"], listings=enriched)


# --- CREATE LISTING ---
@app.route("/create_listing", methods=["POST"])
def create_listing():
    if "user" not in session:
        return jsonify({"success": False})

    game = request.form.get("game", "")
    rank = request.form.get("rank", "")
    description = request.form.get("description", "")
    spots = int(request.form.get("spots", 1))

    listing_id = len(listings) + 1

    listings.insert({
        "id": listing_id,
        "owner": session["user"],
        "game": game,
        "rank": rank,
        "description": description,
        "spots": spots,
        "filled": 0
    })

    return jsonify({"success": True})


# --- DELETE LISTING ---
@app.route("/delete_listing/<int:listing_id>", methods=["POST"])
def delete_listing(listing_id):
    if "user" not in session:
        return jsonify({"success": False})

    listings.remove((Listing.id == listing_id) & (Listing.owner == session["user"]))
    requests_table.remove(JoinRequest.listing_id == listing_id)
    return jsonify({"success": True})


# --- JOIN REQUEST ---
@app.route("/join/<int:listing_id>", methods=["POST"])
def join_listing(listing_id):
    if "user" not in session:
        return jsonify({"success": False, "msg": "Nisi prijavljen"})

    listing = listings.get(Listing.id == listing_id)
    if not listing:
        return jsonify({"success": False, "msg": "Oglas ne obstaja"})

    if listing["owner"] == session["user"]:
        return jsonify({"success": False, "msg": "Ne moreš se pridružiti svojemu oglasu"})

    existing = requests_table.get(
        (JoinRequest.listing_id == listing_id) & (JoinRequest.username == session["user"])
    )
    if existing:
        return jsonify({"success": False, "msg": "Že si poslal prošnjo"})

    requests_table.insert({
        "listing_id": listing_id,
        "username": session["user"],
        "status": "pending"
    })

    return jsonify({"success": True, "msg": "Prošnja poslana!"})


# --- MY LISTINGS PAGE ---
@app.route("/my_listings")
def my_listings():
    if "user" not in session:
        return redirect("/login")

    my = listings.search(Listing.owner == session["user"])
    enriched = []
    for l in my:
        reqs = requests_table.search(JoinRequest.listing_id == l["id"])
        enriched.append({**l, "requests": reqs})

    return render_template("my_listings.html", user=session["user"], listings=enriched)


# --- ACCEPT / REJECT REQUEST ---
@app.route("/handle_request/<int:listing_id>/<string:requester>/<string:action>", methods=["POST"])
def handle_request(listing_id, requester, action):
    if "user" not in session:
        return jsonify({"success": False})

    listing = listings.get((Listing.id == listing_id) & (Listing.owner == session["user"]))
    if not listing:
        return jsonify({"success": False})

    if action == "accept":
        requests_table.update(
            {"status": "accepted"},
            (JoinRequest.listing_id == listing_id) & (JoinRequest.username == requester)
        )
        listings.update(
            {"filled": listing["filled"] + 1},
            Listing.id == listing_id
        )
    elif action == "reject":
        requests_table.update(
            {"status": "rejected"},
            (JoinRequest.listing_id == listing_id) & (JoinRequest.username == requester)
        )

    return jsonify({"success": True})


# --- SEARCH LISTINGS ---
@app.route("/search_listings")
def search_listings():
    if "user" not in session:
        return jsonify([])

    q = request.args.get("q", "").lower()
    all_l = listings.all()

    filtered = []
    for l in all_l:
        if q in l["game"].lower() or q in l["description"].lower() or q in l["rank"].lower():
            filtered.append(l)

    return jsonify(filtered)


app.run(debug=True, port=5001)