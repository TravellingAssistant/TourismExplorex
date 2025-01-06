import os
import mysql.connector
from flask import Flask, session, redirect, request, render_template, flash, abort, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
import requests
import pandas as pd
import re
from flask import Flask, request, jsonify
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

app = Flask("Google Login App")
app.secret_key = "vijay"

# MySQL connection details
MYSQL_HOST = "brow9lqutiwrruahzy6j-mysql.services.clever-cloud.com"
MYSQL_PORT = "3306"
MYSQL_USER = "udefe2bkflhfhjl7"  # replace with your MySQL username
MYSQL_PASSWORD = "gl9H6qwdjVQl3SbQqqmc"  # replace with your MySQL password
MYSQL_DB = "tourism"  # replace with your MySQL database name

# Google OAuth details
GOOGLE_CLIENT_ID = "282021514569-pdsnov6vqp2cegkj271cvdcs87ogj4q5.apps.googleusercontent.com"
client_secrets_file = os.path.join(os.path.dirname(__file__),
                                   "client_secret.json")

# OAuth flow setup
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email", "openid"
    ],
    redirect_uri="http://127.0.0.1:5000/callback")

# Allow insecure transport (only for local development)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


# Establish MySQL connection
def get_db_connection():
    connection = mysql.connector.connect(host=MYSQL_HOST,
                                         user=MYSQL_USER,
                                         password=MYSQL_PASSWORD,
                                         database=MYSQL_DB,
                                         port=MYSQL_PORT)
    return connection


# Function to create the necessary tables if they don't exist
def create_tables():
    connection = get_db_connection()
    cursor = connection.cursor()

    # Create google_users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS google_users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        email VARCHAR(100) UNIQUE,
        google_id VARCHAR(255) UNIQUE
    );
    """)

    # Create traditional_users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS traditional_users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        email VARCHAR(100) UNIQUE,
        password VARCHAR(255)
    );
    """)

    connection.commit()
    connection.close()


# Check if the email is already registered in traditional_users table
def is_email_registered_traditional(email):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM traditional_users WHERE email = %s",
                   (email, ))
    user = cursor.fetchone()
    connection.close()
    return user is not None


# Check if the email is already registered in google_users table
def is_email_registered_google(email):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM google_users WHERE email = %s", (email, ))
    user = cursor.fetchone()
    connection.close()
    return user is not None


# Login required decorator (for routes that require login)
def login_is_required(function):

    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required

        else:
            return function()

    return wrapper


@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    # Check if the email exists in traditional users table
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM traditional_users WHERE email = %s",
                   (email, ))
    user = cursor.fetchone()

    if user:
        # Check if the password matches
        stored_password = user["password"]
        if check_password_hash(stored_password, password):
            session[
                "google_id"] = None  # Ensure Google login doesn't interfere
            session["name"] = user["first_name"]
            flash("Login successful!", "success")
            return redirect("/protected_area")
        else:
            flash("Invalid password.", "danger")
    else:
        flash("Email not found.", "danger")

    connection.close()
    return redirect("/")  # Redirect back to login form or home page


@app.route("/register", methods=["POST"])
def register():
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    email = request.form["email"]
    password = request.form["password"]

    # Check if the email already exists in traditional_users table
    if is_email_registered_traditional(email):
        flash("Email is already registered, please choose another one.",
              "danger")
        return redirect(
            "/")  # Redirect back to the home page or registration form

    # Hash the password before storing it
    hashed_password = generate_password_hash(password)

    # Insert new user into the traditional_users table
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO traditional_users (first_name, last_name, email, password) VALUES (%s, %s, %s, %s)",
        (first_name, last_name, email, hashed_password))
    connection.commit()
    connection.close()

    flash("Registration successful. You can now log in.", "success")
    return render_template("dashboard.html", name=first_name)


@app.route("/login_with_google")
def login_with_google():
    # Initiates the Google login process
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    # Check if state matches
    if not session["state"] == request.args["state"]:
        abort(500)  # State mismatch!

    credentials = flow.credentials
    request_session = requests.session()
    token_request = google.auth.transport.requests.Request(
        session=request_session)

    id_info = id_token.verify_oauth2_token(id_token=credentials._id_token,
                                           request=token_request,
                                           audience=GOOGLE_CLIENT_ID)

    google_id = id_info.get("sub")
    name = id_info.get("name")
    email = id_info.get("email")

    # Check if the email is already registered in the google_users table
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM google_users WHERE google_id = %s OR email = %s",
        (google_id, email))
    user = cursor.fetchone()

    if user is None:
        # User doesn't exist, so register them with Google login details
        first_name, last_name = name.split(" ", 1) if " " in name else (name,
                                                                        "")
        cursor.execute(
            "INSERT INTO google_users (first_name, last_name, email, google_id) VALUES (%s, %s, %s, %s)",
            (first_name, last_name, email, google_id))
        connection.commit()
        session["name"] = first_name  # Store the name in the session
        flash("Google login successful! Account created.", "success")
    else:
        # User already exists, so just log them in
        session["name"] = user["first_name"]
        flash("Google login successful!", "success")

    session["google_id"] = google_id
    connection.close()

    return redirect("/protected_area")


@app.route("/logout")
def logout():
    session.clear()  # Clears session data
    return redirect("/")  # Redirect to home page


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/protected_area")
@login_is_required
def protected_area():
    return render_template("dashboard.html", name=session['name'])


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Default to 8080 if PORT is not set
    app.run(host='0.0.0.0', port=port)