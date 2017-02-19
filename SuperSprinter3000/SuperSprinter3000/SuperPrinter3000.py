from flask import Flask, render_template, g, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'sprinter.db'),
                       SECRET_KEY='development key',
                       USERNAME='admin',
                       PASSWORD='default'
                       ))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
app.config['DEBUG'] = True

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

@app.route("/index")
def index():
    session["add"] = True
    session["edit"] = False
    query = ["", "", "", "", "", "", ""]
    return render_template('form.html', stories=query)

@app.route("/add_story", methods=["POST"])
def add_story():
    db = get_db()
    db.execute('INSERT INTO stories (title,story_text,criteria,value,estimation,status) VALUES(?,?,?,?,?,?)', (
    request.form["title"], request.form["story"], request.form["criteria"], request.form["bvalue"],
    request.form["estimation"], request.form["status"]))
    db.commit()
    query = ["", "", "", "", "", "", ""]
    flash('New user story succesfully added!')
    return redirect(url_for('.show_table'))


@app.route("/show_table", methods=["GET"])
def show_table():
    db = get_db()
    table = db.execute('SELECT id,title,story_text,criteria,value,estimation,status FROM stories')
    stories = table.fetchall()
    if session["edit"]:
        flip_session()
    for i in stories:
        print(i[1])
    return render_template('list.html', stories=stories)


@app.route("/get_id", methods=["POST"])
def get_id():
    x = request.form.keys()[0]
    return redirect(url_for('.load_results', query=x))


@app.route('/index/<query>')
def load_results(query):
    db = get_db()
    table = db.execute('SELECT id,title,story_text,criteria,value,estimation,status FROM stories WHERE id=?', (query,))
    stories = table.fetchall()
    if not session["edit"]:
        flip_session()
    return render_template('form.html', stories=stories[0])


@app.route("/edit_table", methods=["POST"])
def edit_table():
    db = get_db()
    db.execute('UPDATE stories SET title=?,story_text=?,criteria=?,value=?,estimation=?,status=? WHERE id=?', (
    request.form["title"], request.form["story"], request.form["criteria"], request.form["bvalue"],
    request.form["estimation"], request.form["status"], int(request.form["hid_id"])))
    db.commit()
    if session["edit"]:
        flip_session()
    flash('Row edited with id ' + str(request.form["hid_id"]) + "!")
    return redirect(url_for('.index'))
    #return render_template('form.html', stories=["", "", "", "", "", "", ""])


@app.route("/delete_row", methods=["POST"])
def delete_row():
    db = get_db()
    print("is this happening?")
    row_id = request.form.keys()[0]
    print(int(row_id))
    sql_string='DELETE FROM stories WHERE id=%d'% (int(row_id))
    db.execute(sql_string)
    db.commit()
    flash('Row deleted with id ' + str(row_id) + "!")
    print(sql_string)
    return redirect(url_for('show_table'))


def flip_session():
    session["edit"] = not session["edit"]
    session["add"] = not session["add"]


if __name__ == "__main__":
    app.run(debug=True)
