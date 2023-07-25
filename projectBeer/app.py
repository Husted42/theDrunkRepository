##### ----- Imports ----- #####
import os
import pandas as pd
from flask import Flask, render_template, request, url_for, redirect
import psycopg2
import numpy as np
import matplotlib.pyplot as plt

#scheduler
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

##### ----- Variables ----- #####
# Flask constructor
app = Flask(__name__)

# set your own database
db = "dbname='postgres' user='postgres' host='127.0.0.1' password = 'password'"

##### ----- plots ----- #####
def createDataframe():
    conn = psycopg2.connect(db)
    cur = conn.cursor()
    cur.execute('SELECT * FROM Beer;')
    df = cur.fetchall()
    df = pd.DataFrame(df, columns = ['brewer', 'name', 'alc', 'country', 'rating', 'price'])
    print(type(df))
    print(df)
    return df

def avgByCoun():
    df = createDataframe()
    keepers = df['country'].value_counts().reset_index()
    keepers = keepers[keepers['count'] > 3]
    keepers = list(keepers.pop('country'))

    df_avgByCoun = df.groupby(['country'])['rating'].mean().reset_index()
    df_avgByCoun = df_avgByCoun[df_avgByCoun['country'].isin(keepers)]
    df_avgByCoun = df_avgByCoun.sort_values(by=['rating'])
    df_avgByCoun['country'] = df_avgByCoun['country'].str.capitalize()
    
    default_x_ticks = (round(min(df_avgByCoun['rating']))) - 1, (round(max(df_avgByCoun['rating'])) + 1)
    y = list(df_avgByCoun.pop('country'))
    x = list(df_avgByCoun.pop('rating'))
    plt.barh(width=x, y=y, color = 'Blue')
    plt.xlim(default_x_ticks)
    plt.title("Average rating based on Country")
    plt.savefig('static/plots/avgByCoun.png')
    print(default_x_ticks)
    return default_x_ticks

# Create the background scheduler
scheduler = BackgroundScheduler()
# Create the job
scheduler.add_job(func=avgByCoun(), trigger="interval", seconds=3)
# Start the scheduler
scheduler.start()

# /!\ IMPORTANT /!\ : Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

##### ----- Routes ----- #####
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
    avgByCoun()
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