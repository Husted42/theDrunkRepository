import os
from flask import Flask, render_template, request, url_for, redirect
import psycopg2

app = Flask(__name__)

# set your own database
db = "dbname='postgres' user='postgres' host='127.0.0.1' password = 'password'"

#Other
@app.route('/')
def home():
    return render_template('home.html')

@app.route("/brewers", methods=('GET', 'POST'))
def brew():
    conn = psycopg2.connect(db)
    cur = conn.cursor()
    cur.execute('SELECT * FROM Beer;')
    Beer = cur.fetchall() #Database of beers
    cur.execute('SELECT * FROM country_table;')
    country_table = cur.fetchall() #table of (key, name) of countries, used for dropdown menu. 
    if request.method == 'POST':
        if 'countries' in request.form: #Checks wich form is requsted (dropdown <--, search ...) 
            country = request.form['countries']
            cur.execute ("SELECT * FROM Beer WHERE country = '{}'".format(country))
            Beer = cur.fetchall()
            return render_template('brew.html', Beer = Beer, country_table=country_table)
    return render_template('brew.html', Beer = Beer, country_table=country_table)

@app.route("/test")
def test():
    conn = psycopg2.connect(db)
    cur = conn.cursor()
    cur.execute('SELECT * FROM Beer;')
    Beer = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('test.html', Beer = Beer)

@app.route("/admin", methods=('GET', 'POST'))
def admin():
    conn = psycopg2.connect(db)
    cur = conn.cursor()
    if request.method == 'POST':
        nm = request.form['nm']
        brew = request.form['brew']
        typee = request.form['type']
        alc = request.form['alc']
        desc = request.form['desc']
        cur.execute("INSERT INTO Beers(name, type, alc, description, brewery) VALUES ('{}', '{}', {}, '{}', '{}');".format(nm, typee, alc, desc, brew))
        conn.commit()
    return render_template('admin.html')

if __name__ == "__main__":
    app.run(debug=True)