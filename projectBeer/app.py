############### ---------- Imports ---------- ###############
# Backend
import os
from flask import Flask, render_template, request, url_for, redirect, session
import psycopg2
import hashlib
from datetime import datetime
from dotenv import load_dotenv, dotenv_values 

# Import custom functions
from utils import createDataframe, dataframeFix
from overviewPlots import avgByCoun, avgByBrew, donoutChart

# Graphs
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Scheduler
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

############### ---------- Variables ---------- ###############
orange_ = '#F78914'
# Flask constructor
app = Flask(__name__)

app.secret_key = 'OsmanAndJeppe'

load_dotenv()  # Load env
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB = os.getenv('DB')
BEER_SCHEMA = os.getenv('BEER_SCHEMA')
BEER_TABLE = os.getenv('BEER_TABLE')
LOCAL_IP = os.getenv('LOCAL_IP')

# Setup database: postgres
db = f"dbname='{DB}' user='{DB_USER}' host='{DB_HOST}' password='{DB_PASSWORD}'"

# Update matplotlib parameters to automattically adjust layout
rcParams.update({'figure.autolayout': True})

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
def getBrewerCount(db):
    data = createDataframe(db, BEER_TABLE)
    return data['brewer'].unique().size

''' Returns number of diffrent countries'''
def getCountryCount(db):
    data = createDataframe(db, BEER_TABLE)
    return data['country'].unique().size

def getBeerCount(db):
    data = createDataframe(db, BEER_TABLE)
    return len(data)

############### ---------- background scheduler ---------- ###############
# Background scheduler, that runs every hour: 
scheduler = BackgroundScheduler()
# Create the jobs
time_hour = 3600  # seconds
time_day = time_hour * 24  # seconds in a day
scheduler.add_job(
    func=avgByCoun, 
    trigger="interval", 
    seconds=time_hour, 
    kwargs={'color': orange_, 'test': False, 'db': db})
scheduler.add_job(
    func=avgByBrew, 
    trigger="interval", 
    seconds=time_hour, 
    kwargs={'color': orange_, 'test': False, 'db': db})
scheduler.add_job(
    func=donoutChart, 
    trigger="interval", 
    seconds=time_hour, 
    kwargs={'color': orange_, 'test': False, 'db': db})
scheduler.add_job(
    func=autoBackup, 
    trigger="interval", 
    seconds=time_day)
# Start the scheduler
scheduler.start()

# /!\ IMPORTANT /!\ : Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


############### ---------- Routes ---------- ###############
@app.route('/')
def home():
    diffBeer = getBeerCount(db)
    diffBrew = getBrewerCount(db)
    diffCoun = getCountryCount(db)
    return render_template('home.html', diffBeer = diffBeer, diffBrew = diffBrew, diffCoun = diffCoun )

@app.route("/brewers", methods=('GET', 'POST'))
def brew():
    conn = psycopg2.connect(db)
    cur = conn.cursor()

    # Fetch all beers from the database, ordered by rating
    query_all_data = f'''
        SELECT 
            brewer, 
            name, 
            alc, 
            CONCAT(UPPER(LEFT(country,1)), LOWER(RIGHT(country,LENGTH(country)-1))) AS country, 
            rating 
        FROM {BEER_TABLE};
    '''
    query_country_table = f'''
        SELECT 
            country,
            print
        FROM {BEER_SCHEMA}.country_table;
    '''
    
    # Execute the queries
    cur.execute(query_all_data)
    Beer = cur.fetchall() #Database of beers
    cur.execute(query_country_table)
    country_table = cur.fetchall() #table of (key, name) of countries, used for dropdown menu. 
    
    
    if request.method == 'POST':
        if 'countries' in request.form: #Checks wich form is requsted (dropdown <--, searchBrew, searchBeer) 
            alcPer = request.form['alcPer']
            alcMin, alcMax = cleanStringAlc(alcPer)
            country = request.form['countries']
            if country == 'All':
                databaseQuery = f"SELECT brewer, name, alc, CONCAT(UPPER(LEFT(country,1)),LOWER(RIGHT(country,LENGTH(country)-1))), rating FROM {BEER_TABLE} WHERE {alcMin} <= alc AND alc <= {alcMax} ORDER BY rating DESC"
            else:
                databaseQuery = f"SELECT brewer, name, alc, CONCAT(UPPER(LEFT(country,1)),LOWER(RIGHT(country,LENGTH(country)-1))), rating FROM {BEER_TABLE} WHERE country = '{country}' AND {alcMin} <= alc AND alc <= {alcMax} ORDER BY rating DESC"
            cur.execute (databaseQuery)
            Beer = cur.fetchall()
            return render_template('brew.html', Beer = Beer, country_table=country_table)
        if 'breweries' in request.form: #Checks wich form is requsted (dropdown , searchBrew<--, searchBeer)
            brewery = request.form['breweries']
            databaseQuery = f"SELECT brewer, name, alc, CONCAT(UPPER(LEFT(country,1)),LOWER(RIGHT(country,LENGTH(country)-1))), rating FROM {BEER_TABLE} WHERE LOWER(brewer) LIKE LOWER('%{brewery}%') ORDER BY rating DESC"
            cur.execute (databaseQuery)
            Beer = cur.fetchall()
            return render_template('brew.html', Beer = Beer, country_table=country_table)
        if 'beerName' in request.form: #Checks wich form is requsted (dropdown , searchBrew, searchBeer<--)
            beerName = request.form['beerName']
            databaseQuery = f"SELECT brewer, name, alc, CONCAT(UPPER(LEFT(country,1)),LOWER(RIGHT(country,LENGTH(country)-1))), rating FROM {BEER_TABLE} WHERE LOWER(name) LIKE LOWER('%{beerName}%') ORDER BY rating DESC"
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
                databaseQuery = f"INSERT INTO {BEER_TABLE}(brewer, name, alc, country, rating) VALUES ('{brewer}', '{name}', '{alc}', '{country}', '{rating}');"
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
        databaseQuery = "SELECT * FROM beerdata.users WHERE username = '{}' AND password = '{}'".format(username, password)
        cursor.execute(databaseQuery)
        users = cursor.fetchone() #Fetches a single record
        if users:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = users[0]
            session['username'] = users[1]
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
    avgByCoun(color=orange_, test=False, db=db)
    avgByBrew(color=orange_, test=False, db=db)
    donoutChart(color=orange_, test=False, db=db)
    app.run(host=LOCAL_IP, port=9000, debug=True)


############### ---------- Section ---------- ###############
##### ----- Subsection ----- #####
''' FunctionDescriotion '''
#--> ToDo
#comment