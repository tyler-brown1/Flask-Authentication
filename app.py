from flask import Flask, request, redirect,url_for, render_template,session,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from methods import valid_char,sha_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///accounts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '123'

db = SQLAlchemy(app)

class users(db.Model): # create database for users, storing the dates
    name = db.Column(db.String(100),primary_key=True)
    password = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime)

    def __repr__(self):
        return f'User {self.name}, date: {self.date}, password: {self.password}'
    
    def __init__(self,name,password):
        self.name = name
        self.password = password
        self.date = datetime.utcnow()
        self.last_login = datetime.utcnow()

@app.route('/',methods=['GET','POST']) # home page, can either login or create account
def index():
    if 'username' in session: # in session so we redirect to logged page
        return redirect(url_for('logged'))

    if request.method == 'GET':
        return render_template('index.html')
    
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        user = users.query.filter_by(name=name).first()

        if user is None: # user not in database
            flash('User not found')
            return render_template('index.html')
        
        if user.password == sha_hash(password): # check if password hash matches
            old_last = user.last_login
            user.last_login = datetime.utcnow() # update last login
            db.session.commit()

            session['username'] = name
            session['last'] = old_last
            session['date'] = user.date

            return redirect(url_for('logged'))

        flash('wrong password')
        return render_template('index.html')

@app.route('/create') # send to create page
def create():
    return render_template('create.html')

@app.route('/check_new_account',methods=['POST']) # check if username and password are valid
def check():
    name_input = request.form['username']
    password_input = request.form['password']

    if not 4<=len(name_input)<=12 or not 5<=len(password_input)<=12: # server side validation for length
        flash('length error')
        return redirect(url_for('create'))
    
    for letter in name_input:   # validation for all valid characters in username
        if not valid_char(letter):
            flash(f'You cannot use: "{letter}" in your username.')
            return redirect(url_for('create'))

    for letter in password_input: # validation for all valid characters in password
        if not valid_char(letter):
            flash(f'You cannot use: "{letter}" in your password.')
            return redirect(url_for('create'))

    if users.query.filter_by(name=name_input).first(): # make sure user will be unique
        flash(f'Someone with this username already exists')
        return redirect(url_for('create'))
    
    usr = users(name_input,sha_hash(password_input)) # store user in database and create
    db.session.add(usr)
    db.session.commit()
    flash('Account Created')
    return redirect(url_for('index'))

@app.route('/users')
def look():
    s = ''
    for usr in users.query.all():
        s+= f"<h3>{str(usr)}</h3>" # format data
    return s

@app.route('/logged')
def logged():
    if 'username' not in session: 
        return "not allowed"
    return render_template('user.html',name=session['username'],last=session['last'],date=session['date'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/users/<username>')
def user(username):
    usr = users.query.filter_by(name=username).first()
    if usr is None: return "user does not exist"
    return f"<h3>{str(usr)}</h3>"

if __name__ == '__main__':
    with app.app_context(): # create database if it does not exist
        db.create_all()

    app.run(debug=True,port=3000) # run the app