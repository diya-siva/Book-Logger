
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import pytz

from helpers import apology, login_required

# create the application object
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///book_log.db")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == 'POST':
        post_id = request.form['deletebutton']

        db.execute("DELETE FROM user_posts WHERE id=?;", post_id)

        return redirect("/")
    else:
        """show all the book reviews the user has created"""
        userInfo = db.execute("SELECT * FROM users WHERE id=?;", session["user_id"])

        userPosts = db.execute("SELECT * FROM user_posts WHERE username=?", userInfo[0]["username"])

        book_titles = [] # string values
        book_authors = [] # string values
        book_ratings = [] # integer values
        book_summaries = [] # string values
        book_takeaways = [] # string values
        post_datetimes = [] # datetime values
        indeces = []
        post_ids = []


        # loop through database and store the data for the posts that were already created in lists
        # lists are used render index.html which is the home page and will display the current posts

        for i in range(0, len(userPosts)):
            post_ids.append(userPosts[i]["id"])
            indeces.append(i+1)
            book_titles.append(userPosts[i]["title"])
            book_authors.append(userPosts[i]["author"])
            book_ratings.append(userPosts[i]["rating"])
            book_summaries.append(userPosts[i]["summary"])
            book_takeaways.append(userPosts[i]["takeaway"])
            post_datetimes.append(userPosts[i]["datetime"])


        return render_template("index.html", titles=book_titles, author=book_authors, rating=book_ratings, summary=book_summaries, takeaway=book_takeaways, datetime=post_datetimes, index=indeces, ids=post_ids, length=len(indeces))


@app.route("/post/<title>", methods=["GET", "POST"])
@login_required
def post(title):
    if request.method == 'POST':
        post_id = request.form['button']

        post = db.execute("SELECT * FROM user_posts WHERE id=?", post_id)

        if len(post) != 1:
            return apology("Multiple Posts detected", 400)

        post_title = post[0]['title']
        post_author = post[0]['author']
        post_summary = post[0]['summary']
        post_takeaway = post[0]['takeaway']
        post_rating = post[0]['rating']
        post_datetime = post[0]['datetime']

        return render_template("post.html", title=post_title, author=post_author, summary=post_summary, takeaway=post_takeaway, rating=post_rating, datetime=post_datetime)

    else:
        return redirect("/")


@app.route("/new_post", methods=["GET", "POST"])
@login_required
def new_post():
    if request.method == "POST":

        if request.form.get("title") == None:
            return apology("MISSING TITLE", 400)

        post_title = request.form.get("title")

        if request.form.get("author") == None:
            return apology("MISSING AUTHOR", 400)

        post_author = request.form.get("author")

        if request.form.get("rating") == None:
            return apology("MISSING RATING", 400)

        post_rating = request.form.get("rating")

        if request.form.get("summary") == None:
            return apology("MISSING SUMMARY", 400)

        post_summary = request.form.get("summary")

        if request.form.get("takeaway") == None:
            return apology("MISSING TAKEAWAY", 400)

        post_takeaway = request.form.get("takeaway")


        tz_NY = pytz.timezone('America/New_York')
        datetime_NY = datetime.now(tz_NY)

        userInfo = db.execute("SELECT * FROM users WHERE id=?", session["user_id"])

        db.execute("INSERT INTO user_posts (username, datetime, title, author, rating, summary, takeaway) VALUES(?, ?, ?, ?, ?, ?, ?)",
                   userInfo[0]["username"], datetime_NY, post_title, post_author, post_rating, post_summary, post_takeaway)

        return redirect("/")
    else:
        return render_template("new_post.html")




@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password") or not request.form.get("confirmation"):
            return apology("must provide password", 400)

        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("Passwords Do Not Match", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct

        if len(rows) == 1:
            return apology("Username already exists. Please choose another one.", 400)

        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", request.form.get(
            "username"), generate_password_hash(request.form.get("password")))

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)