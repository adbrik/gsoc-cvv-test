from flask import Flask
import flask
import sqlite3
import simplejson as json
from xml.dom import minidom
import os
import markdown
import markdown.extensions.fenced_code

app = Flask(__name__)

app.config.from_pyfile('config.py')

#Get's the Database Connection

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

def get_db():
    db = getattr(Flask, '_database', None)
    if db is None:
        db = Flask._database = sqlite3.connect(DATABASE)
    db.row_factory = make_dicts
    return db

#Query's the database

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

#Routes
@app.route('/')
def index():
    readme_file = open("README.md", "r")
    md_template_string = markdown.markdown(
        readme_file.read(), extensions=["fenced_code"]
    )

    return md_template_string

@app.route('/posts')
def show_posts():
    SQLquerystring = "SELECT * FROM posts"
    sortby = flask.request.args.get('sortby')
    if sortby == "view":
        SQLquerystring = "SELECT * FROM posts ORDER BY ViewCount ASC"
    else:
        if sortby == "score":
            SQLquerystring = "SELECT * FROM posts ORDER BY Score DESC"
    with app.app_context():
        post = query_db(SQLquerystring)
        return flask.jsonify(post)

@app.route('/postsearch')
def search_posts():
    SQLquerystring = "SELECT * FROM posts"
    searchterm = flask.request.args.get('search')
    isThereSearchTerm = True
    if searchterm is None or searchterm is "":
        isThereSearchTerm = False
    with app.app_context():
        posts = query_db(SQLquerystring)
        if isThereSearchTerm is True:
            return flask.jsonify([{k:v for (k,v) in post.items()} for post in posts if (searchterm in post['Body'] or searchterm in post['Title'])])
        else:
            return flask.jsonify(posts)

#Builds the database, and adds the xml to 

def build_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            try:
                db.cursor().executescript(f.read())
            except Exception as e:
                print(e)
        db.commit()
        xmldoc = minidom.parse(r"data/bioinformatics_posts_se.xml")
        rows = xmldoc.getElementsByTagName("row")
        lod = []
        for element in rows:
            if not element.attributes.keys() in lod:
                lod.append(element.attributes.keys())
        loa = []
        for x in lod:
            for y in x:
                loa.append(y)
        dictkeys = set(loa)
        dictKeys = dict.fromkeys(dictkeys,"")
        c = db.cursor()
        for element in rows:
            for key in dictKeys.keys():
                dictKeys[key] = "" 
            for attrName, attrValue in element.attributes.items():
                dictKeys[attrName] = attrValue
            insertIntoDb = (dictKeys['Id'], 
                            dictKeys['PostTypeId'], 
                            dictKeys['ParentId'], 
                            dictKeys['CreationDate'], 
                            dictKeys['Score'], 
                            dictKeys['Body'], 
                            dictKeys['OwnerUserId'], 
                            dictKeys['LastEditorUserId'], 
                            dictKeys['LastEditDate'], 
                            dictKeys['LastActivityDate'], 
                            dictKeys['CommentCount'],
                            dictKeys['FavoriteCount'],
                            dictKeys['AnswerCount'],
                            dictKeys['ViewCount'],
                            dictKeys['AcceptedAnswerId'],
                            dictKeys['Tags'],
                            dictKeys['Title'],
                            dictKeys['ClosedDate'],
                            dictKeys['OwnerDisplayName'])   
            c.execute("INSERT INTO posts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",insertIntoDb)
        db.commit()

if __name__ == "__main__":
    app_dir = os.path.realpath(os.path.dirname(__file__))
    DATABASE = os.path.join(app_dir, app.config['DATABASE'])
    if not os.path.exists(DATABASE):
        build_db()
    app.run(debug=True)

#Closes connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(Flask, '_database', None)
    if db is not None:
        db.close()