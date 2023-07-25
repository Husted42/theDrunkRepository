############### ---------- Imports ---------- ###############
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

############### ---------- Variables ---------- ###############
# Flask constructor
app = Flask(__name__)

# set your own database
db = "dbname='postgres' user='postgres' host='127.0.0.1' password = 'password'"

############### ---------- plots ---------- ###############
def createDataframe():
    conn = psycopg2.connect(db)
    cur = conn.cursor()
    cur.execute('SELECT * FROM Beer;')
    df = cur.fetchall()
    df = pd.DataFrame(df, columns = ['brewer', 'name', 'alc', 'country', 'rating', 'price'])
    return df

'''Saves a plot in static/plots/'''
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
    plt.figure(figsize=(10,6))
    plt.barh(width=x, y=y, color = 'Blue')
    plt.xlim(default_x_ticks)
    plt.title("Average rating based on Country")
    plt.savefig('static/plots/avgByCoun.png')

'''Saves a plot in static/plots/'''
def avgByBrew():
    df = createDataframe()
    keepers = df['brewer'].value_counts().reset_index()
    keepers = keepers[keepers['count'] > 2]
    keepers = list(keepers.pop('brewer'))
    keepers.remove('na')

    df_avgByCoun = df.groupby(['brewer'])['rating'].mean().reset_index()
    df_avgByCoun = df_avgByCoun[df_avgByCoun['brewer'].isin(keepers)]
    df_avgByCoun = df_avgByCoun.sort_values(by=['rating'], ascending=False)
    df_avgByCoun['brewer'] = df_avgByCoun['brewer'].str.capitalize()
    
    x = list(df_avgByCoun.pop('brewer'))[-15:]
    y = list(df_avgByCoun.pop('rating'))[-15:]
    plt.figure(figsize=(10,6))
    plt.bar(x=x, height=y, color = 'Blue')
    plt.title("Average rating based on Brewer")
    plt.ylim((5,10))
    plt.xticks(rotation = 45)
    plt.savefig('static/plots/avgByBrew.png')


##### ----- background scheduler ----- #####
# Create a background scheduler, that runs every hour: 
scheduler = BackgroundScheduler()
# Create the job
scheduler.add_job(func=avgByCoun, trigger="interval", seconds=3600)
scheduler.add_job(func=avgByBrew, trigger="interval", seconds=3600)
# Start the scheduler
scheduler.start()

# /!\ IMPORTANT /!\ : Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

############### ---------- Routes ---------- ###############
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

#--> Admin page works as it should, but doesn't require login
#--> Add login feature, only need one user: admin
@app.route("/admin", methods=('GET', 'POST'))
def admin():
    conn = psycopg2.connect(db)
    cur = conn.cursor()
    if request.method == 'POST':
        brewer = request.form['brewer']
        name = request.form['name']
        alc = request.form['alc']
        country = request.form['country']
        rating = request.form['rating']
        brewer, name, country = brewer.lower(), name.lower(), country.lower()
        cur.execute("INSERT INTO Beer(brewer, name, alc, country, rating) VALUES ('{}', '{}', {}, '{}', '{}');".format(brewer, name, alc, country, rating))
        conn.commit()
    return render_template('admin.html')

if __name__ == "__main__":
    #Function to run on startup
    avgByBrew()
    avgByCoun()
    app.run(debug=True)

############### ---------- Section ---------- ###############
##### ----- Subsection ----- #####
''' FunctionDescriotion '''
#--> ToDo
#comment