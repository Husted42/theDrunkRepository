############### ---------- Imports ---------- ###############
import os
import pandas as pd
from flask import Flask, render_template, request, url_for, redirect
import psycopg2
import numpy as np
import matplotlib.pyplot as plt
import re

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

'''Saves a plot in static/plots/'''
def donoutChart():
    fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))
    data = createDataframe()
    data = data['country'].value_counts().reset_index()
    data = data.sort_values(by=['count'], ascending=False)
    data.loc[data['count'] < 3, 'country'] = "other"
    data = data.groupby(['country'])['count'].sum().reset_index()
    labels = list(data.pop('country'))
    count = list(data.pop('count'))
    wedges, texts = ax.pie(count, wedgeprops=dict(width=0.5), startangle=-40)

    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"),
        bbox=bbox_props, zorder=0, va="center")

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1)/2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = f"angle,angleA=0,angleB={ang}"
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(labels[i], xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y),
            horizontalalignment=horizontalalignment, **kw)

    ax.set_title("Distribution of beer count by country", y=1.05)
    plt.savefig('static/plots/donoutChart.png')

##### ----- background scheduler ----- #####
# Create a background scheduler, that runs every hour: 
scheduler = BackgroundScheduler()
# Create the job
scheduler.add_job(func=avgByCoun, trigger="interval", seconds=3600)
scheduler.add_job(func=avgByBrew, trigger="interval", seconds=3600)
scheduler.add_job(func=avgByBrew, trigger="interval", seconds=3600)
# Start the scheduler
scheduler.start()

# /!\ IMPORTANT /!\ : Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())
############### ---------- Functions ---------- ###############
''' Cleans the string input from range slider on brewer page '''
def cleanStringAlc(string):
    m = re.sub(r'%', '', string)
    m = re.findall(r'\d?\d', m)
    return m[0], m[1]

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
        if 'countries' in request.form: #Checks wich form is requsted (dropdown <--, searchBrew, searchBeer) 
            alcPer = request.form['alcPer']
            alcMin, alcMax = cleanStringAlc(alcPer)
            country = request.form['countries']
            cur.execute ("SELECT * FROM Beer WHERE country = '{}' AND {} <= alc AND alc <= {}".format(country, alcMin, alcMax))
            Beer = cur.fetchall()
            return render_template('brew.html', Beer = Beer, country_table=country_table)
        if 'breweries' in request.form: #Checks wich form is requsted (dropdown , searchBrew<--, searchBeer)
            brewery = request.form['breweries']
            cur.execute ("SELECT * FROM BEER WHERE LOWER(brewer) LIKE LOWER('%{}%')".format(brewery))
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
        for elm in request.form: print(elm)
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
    donoutChart()
    app.run(debug=True)

############### ---------- Section ---------- ###############
##### ----- Subsection ----- #####
''' FunctionDescriotion '''
#--> ToDo
#comment