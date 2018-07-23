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
    else:
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username": username, "password": password})
    db.commit()
    return render_template("success.html")

@app.route("/login/", methods=["POST"])
def login():
    user = request.form.get("Registered_name")
    pas = request.form.get("Registered_Password")

    if (db.execute("SELECT password FROM users WHERE username=:u", {"u":user}).fetchone())[0] != pas:
        return render_template("error.html", message = "Incorrect username or password")
    else:
        return render_template("search.html", name=user)

@app.route("/result/", methods=["POST"])
def result():
    isbn = request.form.get("isbn")
    title = request.form.get("title")
    author = request.form.get("author")
    if isbn == '' and title == '' and author == '':
        return render_template("error.html", message="Please key in something to find a book")

    select_dic = {}
    select_clause = "SELECT * FROM books WHERE"
    if isbn != '':
        select_clause += " isbn LIKE :isbn AND"
        select_dic["isbn"] = '%'+isbn+'%'
    if title != '':
        select_clause += " title LIKE :title AND"
        select_dic["title"] = '%'+title+'%'
    if author != '':
        select_clause += " author LIKE :author"
        select_dic["author"] = '%'+author+'%'
    if select_clause[-3:] == "AND":
        select_clause = select_clause[0:-3]

    rs = db.execute(select_clause, select_dic).fetchall()

    if len(rs) == 0:
        return render_template("error.html", message="No matching result found")

    return render_template("select.html", rs=rs)

@app.route("/book/<string:book_id>", methods=["POST", "GET"])
def book(book_id):
    bk = db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn": book_id}).fetchone()
    new_rv = request.form.get("new_rv")
    if new_rv != ('' or None):
        db.execute("INSERT INTO reviews (isbn, review) VALUES (:isbn, :review)", {"isbn": book_id, "review": new_rv})
        db.commit()
    rvs = db.execute("SELECT * FROM reviews WHERE isbn=:isbn", {"isbn": book_id}).fetchall()
    return render_template("book.html", book = bk, rvs = rvs)
