from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re, md5
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
# PASSWORD_REGEX = re.compile(r'\d.*[A-Z]|[A-Z].*\d') #searches for a upper case followed by a number and the |(or operator) looks for a number then a upper case
NAME_REGEX = re.compile(r'\W.*[A-Za-z]|[A-Za-z]\.*\W|\d.*[A-Za-z]|[A-Za-z].*\d')
app = Flask(__name__)
app.secret_key = "SecretBox"
mysql = MySQLConnector(app,'logregdb')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def new_user():
    count = 0
    if len(request.form['email']) < 1:
        flash("Email is blank!", "email")
    elif not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid Email Address!", "email")
    else:
        count += 1
    if len(request.form['first_name']) <1:
        flash("First name is blank!", "first_name")
    elif len(request.form['first_name']) > 0 and len(request.form['first_name']) < 2:
        flash("First name needs to be AT LEAST 2 characters long!", "first_name")
    elif NAME_REGEX.search(request.form['first_name']):
        flash("Invalid First Name!", "first_name")
    else:
        count += 1
    if len(request.form['last_name']) <1:
        flash("Last name is blank!", "last_name")
    elif len(request.form['last_name']) > 0 and len(request.form['last_name']) < 2:
        flash("Last name needs to be AT LEAST 2 characters long!", "first_name")
    elif NAME_REGEX.search(request.form['last_name']):
        flash("Invalid Last Name!", "last_name")
    else:
        count += 1
    if len(request.form['password']) <1:
        flash("Password is blank!", "password")
    elif len(request.form['password']) > 0 and len(request.form['password']) < 9:
        flash("Password is shorter than 8 characters!", "password")
    # elif not PASSWORD_REGEX.match(request.form['password']):
    #     flash("Password needs at least 1 Upper case and 1 number", "password")
    else:
        count += 1
    if len(request.form['confirm_password']) <1:
        flash("Password Confirmation is blank!", "confirm_password")
    elif request.form['confirm_password'] != request.form['password']:
        flash("Password and confirmation password do not match!", "confirm_password")
    else:
        count += 1

    if count == 5:
        session['first_name'] = request.form['first_name']
        session['last_name'] = request.form['last_name']
        query = "INSERT INTO users (first_name, last_name, email, password, confirm_password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, :confirm_password, NOW(), NOW())"
        data = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email'],
            'password': md5.new(request.form['password']).hexdigest(),
            'confirm_password': md5.new(request.form['confirm_password']).hexdigest()
            }
        mysql.query_db(query, data)
        return redirect('/successreg')
    return redirect('/')

@app.route('/successreg')
def yay_reg():
    return render_template('successreg.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    session['email'] = email
    password = md5.new(request.form['password']).hexdigest()
    query = "SELECT * FROM users WHERE users.email = :email"
    data = { 'email': email }
    user = mysql.query_db(query, data)
    if len(user) != 0:
        if user[0]['password'] == password:
            return redirect('/success')
        else:
            flash("PASSWORD DOES NOT MATCH!", "login")
    else:
        flash("EMAIL ADDRESS INVALID", "login")
    return redirect('/')
@app.route('/success')
def success():
    return render_template('success.html')

app.run(debug=True)