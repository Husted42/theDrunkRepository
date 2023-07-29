############### ---------- Imports ---------- ###############
#Backend
import os
from flask import Flask, render_template, request, url_for, redirect, session
import psycopg2
import hashlib
from datetime import datetime

#Graphs
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

#scheduler
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler


############### ---------- Variables ---------- ###############
orange_ = '#F78914'
# Flask constructor
app = Flask(__name__)

app.secret_key = 'OsmanAndJeppe'

# Setup database: postgres
db = "dbname='postgres' user='postgres' host='127.0.0.1' password = 'password'"


############### ---------- plots ---------- ###############
rcParams.update({'figure.autolayout': True})
''' Turns Beer table into dataframe '''
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
    keepers = keepers[keepers['country'] > 3]
    keepers = list(keepers.pop('index'))

    df_avgByCoun = df.groupby(['country'])['rating'].mean().reset_index()
    df_avgByCoun = df_avgByCoun[df_avgByCoun['country'].isin(keepers)]
    df_avgByCoun = df_avgByCoun.sort_values(by=['rating'])
    df_avgByCoun['country'] = df_avgByCoun['country'].str.capitalize()
    
    xRange = (round(min(df_avgByCoun['rating']))) - 1, (round(max(df_avgByCoun['rating'])) + 1)
    y = list(df_avgByCoun.pop('country'))
    x = list(df_avgByCoun.pop('rating'))
    plt.figure(figsize=(10,6))
    plt.barh(width=x, y=y, color = orange_)
    plt.xlim(xRange)
    plt.xlabel('Rating', fontdict={'size': 20})
    plt.title("Average rating based on Country", fontdict={'size': 20})
    plt.savefig('static/plots/avgByCoun.png', transparent=True)

'''Saves a plot in static/plots/'''
def avgByBrew():
    df = createDataframe()
    keepers = df['brewer'].value_counts().reset_index()
    print(keepers)
    for elm in keepers: print(elm)
    keepers = keepers[keepers['brewer'] > 2]
    keepers = list(keepers.pop('index'))
    keepers.remove('na')

    df_avgByCoun = df.groupby(['brewer'])['rating'].mean().reset_index()
    df_avgByCoun = df_avgByCoun[df_avgByCoun['brewer'].isin(keepers)]
    df_avgByCoun = df_avgByCoun.sort_values(by=['rating'], ascending=False)
    df_avgByCoun['brewer'] = df_avgByCoun['brewer'].str.capitalize()
    
    x = list(df_avgByCoun.pop('brewer'))[-15:]
    y = list(df_avgByCoun.pop('rating'))[-15:]
    plt.figure(figsize=(10,6))
    plt.bar(x=x, height=y, color = orange_)
    plt.title("Average rating based on Brewer", fontdict={'size': 20})
    plt.ylim((5,10))
    plt.ylabel('Rating', fontdict={'size': 20})
    plt.xticks(rotation = 45)
    plt.savefig('static/plots/avgByBrew.png', transparent=True)

'''Saves a plot in static/plots/'''
def donoutChart():
    fig, ax = plt.subplots(figsize=(10, 6), subplot_kw=dict(aspect="equal"))
    data = createDataframe()
    data = data['country'].value_counts().reset_index()
    data = data.sort_values(by=['country'], ascending=False)
    data.loc[data['country'] < 3, 'index'] = "other"
    data = data.groupby(['index'])['country'].sum().reset_index()
    labels = list(data.pop('index'))
    labels = list(map(str.capitalize, labels))

    count = list(data.pop('country'))

    #Add % for labels
    total = sum(count)
    lst = []
    for elm in count:
        per = elm / total
        per = round(per, 2)
        per = ' ' + str(per) + '%'
        lst.append(per)
    print(lst)
    labels = [i + j for i, j in zip(labels, lst)]

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

    
    ax.set_title("Distribution of beer count by country", y=1.05, fontdict={'size': 20})
    plt.savefig('static/plots/donoutChart.png', transparent=True)


############### ---------- Functions ---------- ###############
''' Cleans the string input from range slider on brewer page '''
def cleanStringAlc(string):
    m = re.sub(r'%', '', string)
    m = re.findall(r'\d?\d', m)
    return m[0], m[1]

''' Backup table-Beer in a csv file'''
def autoBackup():
    data = createDataframe()
    datetime_obj = datetime.now()
    filename = str(datetime_obj.date()) + '.csv'
    filepath = os.path.join(os.getcwd(), "backup")
    filepath = filepath + '\\' + filename
    data.to_csv(filepath, header=True)

##### ----- Values for home page ----- #####
''' Returns number of diffrent brewers'''
def getBrewerCount():
    data = createDataframe()
    return data['brewer'].unique().size

''' Returns number of diffrent countries'''
def getCountryCount():
    data = createDataframe()
    return data['country'].unique().size


############### ---------- background scheduler ---------- ###############
# Create a background scheduler, that runs every hour: 
scheduler = BackgroundScheduler()
# Create the job
scheduler.add_job(func=avgByCoun, trigger="interval", seconds=7200)
scheduler.add_job(func=avgByBrew, trigger="interval", seconds=7200)
scheduler.add_job(func=avgByBrew, trigger="interval", seconds=7200)
scheduler.add_job(func=autoBackup, trigger="interval", seconds=604800)
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
    cur.execute('SELECT brewer, name, alc, CONCAT(UPPER(LEFT(country,1)),LOWER(RIGHT(country,LENGTH(country)-1))), rating FROM Beer ORDER BY rating DESC;')
    Beer = cur.fetchall() #Database of beers
    cur.execute('SELECT * FROM country_table;')
    country_table = cur.fetchall() #table of (key, name) of countries, used for dropdown menu. 
    if request.method == 'POST':
        if 'countries' in request.form: #Checks wich form is requsted (dropdown <--, searchBrew, searchBeer) 
            alcPer = request.form['alcPer']
            alcMin, alcMax = cleanStringAlc(alcPer)
            country = request.form['countries']
            if country == 'All':
                databaseQuery = "SELECT brewer, name, alc, CONCAT(UPPER(LEFT(country,1)),LOWER(RIGHT(country,LENGTH(country)-1))), rating FROM Beer WHERE {} <= alc AND alc <= {} ORDER BY rating DESC".format(alcMin, alcMax)
            else:
                databaseQuery = "SELECT brewer, name, alc, CONCAT(UPPER(LEFT(country,1)),LOWER(RIGHT(country,LENGTH(country)-1))), rating FROM Beer WHERE country = '{}' AND {} <= alc AND alc <= {} ORDER BY rating DESC".format(country, alcMin, alcMax)
            cur.execute (databaseQuery)
            Beer = cur.fetchall()
            return render_template('brew.html', Beer = Beer, country_table=country_table)
        if 'breweries' in request.form: #Checks wich form is requsted (dropdown , searchBrew<--, searchBeer)
            brewery = request.form['breweries']
            databaseQuery = "SELECT brewer, name, alc, CONCAT(UPPER(LEFT(country,1)),LOWER(RIGHT(country,LENGTH(country)-1))), rating FROM Beer WHERE LOWER(brewer) LIKE LOWER('%{}%') ORDER BY rating DESC".format(brewery)
            cur.execute (databaseQuery)
            Beer = cur.fetchall()
            return render_template('brew.html', Beer = Beer, country_table=country_table)
        if 'beerName' in request.form: #Checks wich form is requsted (dropdown , searchBrew, searchBeer<--)
            beerName = request.form['beerName']
            databaseQuery = "SELECT brewer, name, alc, CONCAT(UPPER(LEFT(country,1)),LOWER(RIGHT(country,LENGTH(country)-1))), rating FROM Beer WHERE LOWER(name) LIKE LOWER('%{}%') ORDER BY rating DESC".format(beerName)
            cur.execute (databaseQuery)
            Beer = cur.fetchall()
            return render_template('brew.html', Beer = Beer, country_table=country_table)
    return render_template('brew.html', Beer = Beer, country_table=country_table)

@app.route("/admin", methods=('GET', 'POST'))
def admin():
    if 'loggedin' in session:
        conn = psycopg2.connect(db)
        cur = conn.cursor()
        if request.method == 'POST':
            if 'brewer' in request.form:
                brewer = request.form['brewer']
                name = request.form['name']
                alc = request.form['alc']
                country = request.form['country']
                rating = request.form['rating']
                brewer, name, country = brewer.lower(), name.lower(), country.lower()
                databaseQuery = "INSERT INTO Beer(brewer, name, alc, country, rating) VALUES ('{}', '{}', {}, '{}', '{}');".format(brewer, name, alc, country, rating)
                cur.execute(databaseQuery)
                conn.commit()
                return render_template('admin.html')
            if 'logout' in request.form:
                return redirect(url_for('logout'))
            else: 
                return 'Error'
    else:
        return redirect(url_for('login'))
    return render_template('admin.html')


############### ---------- Login/Logout ---------- ###############
@app.route("/login", methods=['GET', 'POST'])
def login():
    msg = '' #has to be initialized otherwise render error in msg=msg
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        # Security:
        password = password + 'boatsAreCool' #Non random salting
        password = hashlib.md5(password.encode()) #Hash password
        password = password.hexdigest() #convert password to string
        print(password)
        # verification:
        conn = psycopg2.connect(db)
        cursor = conn.cursor()
        databaseQuery = "SELECT * FROM account WHERE username = '{}' AND password = '{}'".format(username, password)
        cursor.execute(databaseQuery)
        account = cursor.fetchone() #Fetches a single record
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            return redirect(url_for('admin'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)

@app.route('/login/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


############### ---------- Run ---------- ###############
if __name__ == "__main__":
    #Function to run on startup
    avgByCoun()
    avgByBrew()
    donoutChart()
    app.run(debug=True)


############### ---------- Section ---------- ###############
##### ----- Subsection ----- #####
''' FunctionDescriotion '''
#--> ToDo
#comment