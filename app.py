from flask import Flask, render_template, redirect, url_for, abort, g, request, session
from functools import wraps
import random
import sqlite3

app = Flask(__name__)

app.secret_key = 'tigerbootylickle707'

db_file = "app.db"

def get_db():
    connection = g.get('db', None)
    if connection is None:
        connection = sqlite3.connect(db_file)
        connection.row_factory = sqlite3.Row 
        g.db = connection
    return connection

def create_table():
    connection = get_db()
    sql = connection.cursor()
    sql.execute('''create table if not exists monsters ("monsterId" integer primary key autoincrement, "name" Text, "armor" Text, "hp" Text) ''')

def create_monster(name, armor, hp):
    connection = get_db()
    sql = connection.cursor()
    sql.execute('''insert into monsters (name, armor, hp) values (?,?,?) ''', [name,armor,hp])
    connection.commit()

with app.app_context():
    create_table()

#def tracker_screen(func):
#    @wraps(func)
#    def decorated():
#        monster_data = get_monsters()
#        return render_template('tracker.html', monsters=monster_data)
#    return decorated

@app.route('/', methods=['GET', 'POST'])
#@tracker_screen
def home_page():
    if 'selected_monsters' not in session:
        session['selected_monsters'] = []

    if request.method == 'POST':
        selected_monster = request.form.get('active-monsters')
        if selected_monster:
            session['selected_monsters'].append(selected_monster)
            session.modified = True
    monster_data = get_monsters()
    return render_template('tracker.html', monsters=monster_data, selected_monsters=session['selected_monsters'])

@app.route('/remove', methods=['POST'])
def remove_monster():
    monster_to_remove = request.form.get('monster_to_remove')

    if 'selected_monsters' in session and monster_to_remove in session['selected_monsters']:
        session['selected_monsters'].remove(monster_to_remove)  # Removes the first match
        session.modified = True

    return redirect(url_for('home_page'))

@app.route('/delete', methods=['POST'])
def delete_monster():
    monster_id = request.form.get('monster_id')

    if monster_id:
        connection = get_db()
        sql = connection.cursor()
        sql.execute('DELETE FROM monsters WHERE monsterId = ?', (monster_id,))
        connection.commit()

    return redirect(url_for('list_page'))

@app.route('/update', methods=['POST'])
def update_monster():
    monster_id = request.form.get('monster_id')
    new_armor = request.form.get('armor')
    new_hp = request.form.get('hp')

    if monster_id and new_armor is not None and new_hp is not None:
        connection = get_db()
        sql = connection.cursor()
        sql.execute('''
            UPDATE monsters
            SET armor = ?, hp = ?
            WHERE monsterId = ?
        ''', (new_armor, new_hp, monster_id))
        connection.commit()

    return redirect(url_for('list_page'))

@app.route('/tracker')
def tracker_page():
    return render_template('tracker.html')

@app.route('/create', methods=['GET', 'POST'])
def create_page():
    if request.method == 'POST':
        name = request.form['name']
        armor = request.form['armor']
        hp = request.form['hp']
        create_monster(name, armor, hp)
    return render_template('create.html')





def get_monsters():
    connection = get_db()
    sql = connection.cursor()
    data = sql.execute('''select * from monsters order by monsterId desc''')
    saved_monsters = data.fetchall()
    return saved_monsters



@app.route('/list')
def list_page():
    monster_data = get_monsters()
    return render_template('list.html', monsters=monster_data)


if __name__ == '__main__':
  app.run()


    
