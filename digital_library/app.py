from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "library123"

# Database Helper
def query(sql, args=()):
    conn = sqlite3.connect("library.db")
    cur = conn.cursor()
    cur.execute(sql, args)
    conn.commit()
    return cur.fetchall()

# Login Page
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        pwd = request.form["password"]

        user = query("SELECT * FROM users WHERE email=? AND password=?", (email, pwd))
        if user:
            session["user"] = user[0]
            return redirect("/admin" if user[0][4]=="admin" else "/user")
        else:
            return "Invalid Login"
    return render_template("login.html")

# Admin Dashboard
@app.route("/admin")
def admin():
    if "user" not in session or session["user"][4] != "admin":
        return "Unauthorized"
    books = query("SELECT * FROM books")
    users = query("SELECT * FROM users WHERE role='user'")
    return render_template("admin_dashboard.html", books=books, users=users)

# Add Book
@app.route("/add_book", methods=["POST"])
def add_book():
    query("INSERT INTO books(title,author,status) VALUES(?,?,?)",
          (request.form["title"], request.form["author"], "Available"))
    return redirect("/admin")

# Delete Book
@app.route("/delete_book/<id>")
def delete_book(id):
    query("DELETE FROM books WHERE id=?", (id,))
    return redirect("/admin")

# ✅ Books Page Route
@app.route("/books")
def books_page():
    books = query("SELECT * FROM books")
    return render_template("books.html", books=books)

# User Dashboard
@app.route("/user")
def user():
    if "user" not in session:
        return redirect("/")
    books = query("SELECT * FROM books")
    return render_template("user_dashboard.html", books=books)

# Issue Book
@app.route("/issue/<book_id>")
def issue(book_id):
    uid = session["user"][0]
    query("INSERT INTO issued(user_id,book_id) VALUES(?,?)",(uid,book_id))
    query("UPDATE books SET status='Issued' WHERE id=?", (book_id,))
    return redirect("/user")

# Return Book
@app.route("/return/<book_id>")
def ret(book_id):
    uid = session["user"][0]
    query("DELETE FROM issued WHERE user_id=? AND book_id=?", (uid,book_id))
    query("UPDATE books SET status='Available' WHERE id=?", (book_id,))
    return redirect("/user")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

app.run(debug=True)
