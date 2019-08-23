'''
Attempt #3

TODO: Figure out how to return the username i.e. "you are logged in as {{username}}"
TODO: Figure out flask_login {
    TODO: Add in Forgot password button? (flask-login)
    TODO: Add in a check if logged in - else --> redirect(url_for(/login))
            JK that already exists. I think I need an auto logout like session.pop(logged_in, none) but automatically
            maybe put it at the start of every refresh, but that might get annoying
            can you time it somehow? At what point would you stop? What are the rules here?
            TODO: From flask_login import LoginManager #Project for later
            https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
}
TODO: Add an ABOUT ME page
        Or add in a photo in sidebar with a short About Me paragraph
TODO: Add in an edit button
        Send to EDIT page
        Retrieve post and save changes
TODO: Add in a delete button
        send "Are you sure",'warning'
        remove from db
TODO: Add functionality for photos
        upload your photo and display on post
TODO: Create multiple accounts
TODO: Connect to www.nielssmith.com
TODO: Make it pretty


Notes:
 * Statements {%  %} / Expressions {{  }}
 * Use backslash \ to indicate code is continued on the next line
'''

# imports!
from flask import Flask, render_template, request, session, flash, redirect, url_for, g
from functools import wraps
from flask_bootstrap import Bootstrap
from flask_mysqldb   import MySQL
from datetime import datetime
import yaml
import os
import MySQLdb

app = Flask(__name__) # instantiate object
db = yaml.full_load(open('db.yaml')) #someone on stack said use 'full_load' not 'load' (they were right)
mysql = MySQL(app)
Bootstrap(app) # Make app bootstrap enabled

#Config
app.config.from_object(__name__)
app.config['MYSQL_HOST']     = db['mysql_host']
app.config['MYSQL_DB']       = db['mysql_db']
app.config['MYSQL_USER']     = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['USERNAME']       = db['username']
app.config['PASSWORD']       = db['password']
app.config['SECRET_KEY']     = db['secret_key']

# function used for connecting to the database
mysql = MySQL(app)

# Creates the connection object
def connect_db():
    return MySQLdb.Connection(host     = app.config['MYSQL_HOST'],
                              user     = app.config['MYSQL_USER'],
                              passwd   = app.config['MYSQL_PASSWORD'],
                              database = app.config['MYSQL_DB']
                              )

def login_required(test):
    @wraps(test) # I still don't understand the @wraps(...)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You\'ll need to login first.')
            return redirect(url_for('login'))
    return wrap

@app.route('/', methods = ['GET','POST'])
def login():
    error = None
    status_code = 200
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME'] or \
        request.form['password'] != app.config['PASSWORD']:
            error = 'You are invalid'
            status_code = 401
        else:
            username = request.form['username']
            session['logged_in'] = True
            return redirect(url_for('main', username = username))
    return render_template('login.html', error=error), status_code

@app.route('/about', methods = ['GET'])
def about():
    return render_template('about.html')

@app.route('/main')
@login_required
def main():
    #flash("Hello ", name) # error: "name not found" I'm assuming because it's
    g.db = connect_db()
    cur = g.db.cursor()
    cur.execute('select * from user')
    posts = [dict(title=row[0], post=row[1], time= row[2]) for row in cur.fetchall()]
    g.db.close()
    return render_template('main.html', posts=posts)

@app.route('/add', methods=['POST'])
@login_required
def add():
    title = request.form['title']
    post  = request.form['post']
    time  = datetime.today()
    if not title or not post:
        flash("All fields are required. Please try again.",'error')
        return redirect(url_for('main'))
    else:
        g.db = connect_db()
        cur = g.db.cursor()
        cur.execute('''INSERT INTO user (title, posts, time)
                       VALUES (%s ,%s, %s)
                    ''' , (title,post,time)
                    )
        cur.close()
        g.db.commit()
        cur.close()
        flash('New entry was successfully posted!')
        return redirect(url_for('main'))

@login_required
@app.route('/logout')
def logout():
    session.pop('logged_in', None) # To release a session use pop() method! "Gotta pop off"
    flash('Loggout Successful')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug = True)
# I had a lot of fun with this!
