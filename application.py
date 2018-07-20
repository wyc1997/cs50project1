import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["POST", "GET"])
def index():
    return render_template("index.html")

@app.route("/registration", methods=["POST"])
def register():
    username = request.form.get("Username")
    password = request.form.get("Password")

    if (db.execute("SELECT * FROM users WHERE username=:un", {"un": username}).rowcount) != 0:
        return render_template("error.html", message="username already exists")
    db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username": username, "password": password})
    return render_template("success.html")

@app.route("/login")
def login():
    return
