'''
Attempt #3
https://github.com/realpython/book2-exercises/tree/master/flask-blog
http://www.sqlitetutorial.net/sqlite-python/sqlite-python-select/
https://stackoverflow.com/questions/16311974/connect-to-a-database-in-flask-which-approach-is-better
K, I'M HIGH,
BUT_REVIEW_THOSE(3_LINKS^)
IF DATABASE_CONNECTION = FALSE:
    RETURN REDO_ALL_DATABASE_CONNECTION_STUFF()
ELSE:
    RETURN CELEBRATE()


TODO: Add in a check if logged in - else --> redirect(url_for(/login))
        JK that already exists. I think I need an auto logout like session.pop(logged_in, none) but automatically
            maybe put it at the start of every refresh, but that might get annoying
                can you time it somehow? At what point would you stop?
                    what are the common rules here?
TODO: Figure out flask_login
TODO: Figure out how to return the username i.e. "you are logged in as {{username}}"
TODO: Add timestamp to posts

'''

# imports!
from flask import Flask, render_template, request, session, flash, redirect, url_for, g
# from flask_login import LoginManager #Project for later
## https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
from functools import wraps
from flask_bootstrap import Bootstrap
from flask_mysqldb   import MySQL
import yaml
import os
import mysql.connector
import sqlite3
import MySQLdb

app = Flask(__name__) # instantiate object
Bootstrap(app) # Make app bootstrap enabled

app.config.from_object(__name__)
mysql  = MySQL(app)

#Config
db = yaml.full_load(open('db.yaml')) #someone on stack said use 'full_load' not 'load'
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['USERNAME'] = db['username']
app.config['PASSWORD'] = db['password']
app.config['SECRET_KEY'] = db['secret_key']
mysql = MySQL(app)
# print(os.getcwd())
#
# function used for connecting to the database
# Creates the connection object
def connect_db():
    return MySQLdb.Connection(host = app.config['MYSQL_HOST'],
                              user = app.config['MYSQL_USER'],
                              passwd =app.config['MYSQL_PASSWORD'],
                              database = app.config['MYSQL_DB']
                              )

def login_required(test):
    @wraps(test)
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
        if request.form['username'] != app.config['USERNAME'] or request.form['password'] != app.config['PASSWORD']:
            error = 'you are invalid'
            status_code = 401
        else:
            session['logged_in'] = True
            return redirect(url_for('main'))
    return render_template('login.html', error=error), status_code

@app.route('/main')
@login_required
def main():
    g.db = connect_db()
    cur = g.db.cursor()
    cur.execute('select * from user')  # Problem <<<<<< AttributeError: 'Connection' object has no attribute 'execute'
    # posts = [dict(title=row[0], post=row[1]) for row in cur.fetchall()] # No, I don't fully understand this. Why do you ask?
    texttext = cur.fetchall()
    # return str(texttext)
    return render_template('main.html')#, posts=posts)

@app.route('/add', methods=['POST'])
@login_required
def add():
    title = request.form['title']
    post = request.form['post']
    if not title or not post: # If blank return error
        flash("All fields are required. Please try again.",'error')
        return redirect(url_for('main'))
    else:
        g.db = connect_db()
        cur = g.db.cursor()
        cur.execute('''INSERT INTO user (title, posts) VALUES (%s ,%s) ''' , (title,post)
         # (?, ?)', [request.form['title'], request.form['post']]
        )
        cur.close()
        g.db.commit()
        cur.close()
        flash('New entry was successfully posted!')
        return redirect(url_for('main'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None) # To release a session variable use pop() method!!!
    flash('You were logged out')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug = True)


















#
