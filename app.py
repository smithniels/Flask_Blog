'''
This code was written by Charles Leifer
https://charlesleifer.com/blog/how-to-make-a-flask-blog-in-one-hour-or-less/
I'm just adding comments to understand how it works

TODO: What is a slug?
    Slugs are used to generate 'clean'ish end bits of url's
    www.google.com/this-is-what-the-slug-makes

TODO:

TODO: Learn Regex (REGulerEXpressions)
TODO:
TODO:
TODO:
TODO: Split this up into seperate modules

Notes:
    FTS: Full Text Search
    Single quotes? Dict. Double quotes? JSON!
    pip install markdown && pip install peewee && pip install micawber && pip install flask
    *args & **kwargs
        *args     Used to pass a number of arguments
        *kwargs   Used to pass a number of KeyWord arguments
    DRY: Don't Repeat Yourself

'''
import datetime # Gets the time
import functools
# from functools import wraps # This breaks the everything. It wants "import functools" just.
import os
import re # Regex
import urllib
from flask import (Flask, abort, flash, Markup, redirect, render_template,
                   request, Response, session, url_for)
from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from micawber import bootstrap_basic, parse_html # Micawber is a small library for extracting rich content from urls
from micawber.cache import Cache as OEmbedCache
from peewee import *
from playhouse.flask_utils import FlaskDB, get_object_or_404, object_list
from playhouse.sqlite_ext import *

ADMIN_PASSWORD = 'password' # Consider at least using a one-way hash to store the password.
APP_DIR = os.path.dirname(os.path.realpath(__file__))    # Return the directory name of pathname path.
                                                         # This is the first element of the pair returned
                                                         # by passing path to the function split()
DATABASE = 'sqliteext:///%s' % os.path.join(APP_DIR, 'blog.db')
DEBUG = False
SECRETKEY = 'secret'
SITE_WIDTH = 800
FLASK_ENV = 'Development'
app = Flask(__name__)
app.config.from_object(__name__)
flask_db = FlaskDB(app)
database = flask_db.database

oembed_providers = bootstrap_basic(OEmbedCache())

# Defining the model classes!
class Entry(flask_db.Model):
    title = CharField()
    slug  = CharField(unique = True)
    content = TextField
    published = BooleanField(index = True)
    timestamp = DateTimeField(default = datetime.datetime.now, index = True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = re.sub('[^\w]+', '-', self.title.lower())
            # \w : Find "any word character"
        ret = super(Entry, self).save(*args,**kwargs)

        #store search content
        self.update_search_index()
        return ret

    def update_search_index(self):
        search_content = '\n'.join((self.title,self.content)) # \n newline
        try:
            fts_entry = FTSEntry.get(FTSEntry.docid == self.id)
        except FTSEntry.DoesNotExist:
            FTSEntry.create(docid = self.id, content= search_content)
        else:
            fts_entry.content = search_content
            fts_entry.save()

class FTSEntry(FTSModel):
    content = SearchField()
    class Meta:
        database = database

@app.template_filter('clean_querystring')
def clean_querystring(request_args, *keys_to_remove, **new_values):
    querystring = dict((key, value) for key, value in request_args.items())
    for key in keys_to_remove:
        querystring.pop(key, None)
    querystring.update(new_values)
    return urlib.urlencode(querystring)

@app.errorhandler(404)
def not_found(exc):
    return Response('<h2>Not Found</h2>', 404)

def main():
    database.create_tables([Entry,FTSEntry])
    app.run()
    # app.run(debug= True) # Running Flask in Development automatically switching debug to True
    # but they had me add in "DEBUG = False" earlier, so that line is unnecessary/ redundant

def login_required(fn):
    @functools.wraps(fn)
    def inner(*args,**kwarg):
        if session.get('logged_in'):
            return fn(*args,**kwargs)
        return redirect(url_for('login', next = request.path))
    return inner

@app.route('/login/', methods= ['GET','POST'])
def login():
    next_url = request.args.get('next') or request.form.get('next')
    if request.get == 'POST' and request.form.get('password'):
        password = request.form.get('password')
        if password == app.config['ADMIN_PASSWORD']:
            session['logged_in'] = True
            session.permanent = True #use the cookies to store session from cookie (monster)
            flash('You might be logged in!', 'success')
            return redirect(next_url or url_for('index'))
        else:
            flash('Whelp that wasn\'t right','danger')
    return render_template('login.html', next_url = next_url)

    @app.route('/logout/', methods = ['GET','POST'])
    def logout():
        if request.method == 'POST':
            session.clear()
            return redirect(url_for('login'))
        return render_template #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

@app.route('/')
def index():
    search_query = request.args.get('q')
    if search_query:
        query = Entry.search(search_query)
    else:
        query = Entry.public().order_by(Entry.timestamp.desc()) # return all published in chronological order
    return object_list('index.html', query ,search=search_query)

@classmethod
def public(cls): # cls stands for class
    return Entry.select().where(Entry.published == True)

@classmethod
def search(cls, query):
    words = [word.strip() for word in query.split() if word.strip()]
    if not words:
        #return empty query
        return Entry.select().where(Entry.id == 0)
    else:
        search = ' '.join(words)
    return (Entry
            .select(Entry, FTSEntry.rank().alias('score'))
            .join(FTSEntry, on =(Entry.id == FTSEntry.docid))
            .where(
                (Entry.published == True)  &
                (FTSEntry.match(search))
            .order_by(SQL('score'))
                  )
            )

@classmethod
def drafts(cls):
    return Entry.select().where(Entry.published == False)

@app.route('/drafts')
@login_required
def drafts():
    query = Entry.drafts().order_by(Entry.timestamp.desc())
    return object_list('index.html', query)

@app.route('/slugs/')
def detail(slug): # get the details on a post. Must be logged in
    if session.get('logged_in'):
        query = Entry.select()
    else:
        query = Entry.public()
    entry = get_object_or_404(query, Entry.slug == slug)
    return render_template('detail.html', entry = entry)

@property
def html_content(self):
    hilite = CodeHiliteExtension(linenums = False, css_class= 'highlight')
    extras = ExtraExtension()
    markdown_content = markdown(self.content, extentions = [hilite,extras])
    oembed_content = parse_html(
        markdown_content,
        oembad_providers,
        urlize_all = True,
        maxwidth = app.config([SITE_WIDTH]))
    return Markup(oembed_content)

#If the request method is GET, then we will display a form
# allowing the user to create or edit the given entry.

#If the method is POST we will assume they submitted the form
#on the page (which we'll get to when we cover templates), and
#after doing some simple validation, we'll either create a new
#entry or update the existing one.

@app.route('/create',methods = ['GET','POST'])
@login_required
def create():
    if request.method == 'POST':
        if request.form.get('title') and request.form.get('content'):
            entry = Entry.create(
                title= request.form['title'],
                content= request.form['content'],
                published = request.form.get('published') or False)
            flash('Entry created sucessfully! Wow!','sucesss')
            if entry.published:
                return redirect(url_for('detail', slug = entry.slug))
            else:
                return redirect(url_for('edit', slug = entry.slug))
        else:
            flash('Title and Content are Required!!!','danger')
    return render_template('create.html')

@app.route('/<slug>/edit', methods = ['GET','POST'])
@login_required # My legs hurt
def edit(slug):
    entry = get_object_or_404(Entry,  Entry.slug == slug)
    if request.method == 'POST':
        if request.form.get('title') and request.form.get('content'):
            entry.title = request.form['title']
            entry.content = request.form['content']
            entry.published = request.form.get('published') or False
            entry.save()

            flash('Entry saved successfully','sucess')
            if entry.published:
                return redirect(url_for('detail', slug =entry.slug))
            else:
                return redirect(url_for('edit',slug = entry.slug))
        else:
            flash('Title/Content are required','danger')
    return render_template('edit.html', entry= entry)

if __name__ == '__main__':
    main()

print('Shut it down')
