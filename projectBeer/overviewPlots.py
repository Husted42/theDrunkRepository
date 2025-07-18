############### ---------- Imports ---------- ###############
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv, dotenv_values
import matplotlib.pyplot as plt
from utils import createDataframe, dataframeFix
import numpy as np

############### ---------- Variables ---------- ###############
load_dotenv()  # Load env
DB = os.getenv('DB')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
BEER_TABLE = os.getenv('BEER_TABLE')

############### ---------- Function ---------- ###############
def avgByCoun(color, test=False, db=None):
    '''
        Creates a bar chart of the average rating based on country.
        Saves the chart as 'avgByCoun.png' in the static/plots directory.
    '''
    # Create a dataframe from the database and filter countries with more than 3 beers
    df = createDataframe(db, BEER_TABLE)
    keepers = df['country'].value_counts().reset_index()
    keepers = dataframeFix(keepers)
    keepers = keepers[keepers['country'] > 3]
    keepers = list(keepers.pop('index'))

    # Create a dataframe with the average rating by country
    df_avgByCoun = df.groupby(['country'])['rating'].mean().reset_index()
    df_avgByCoun = df_avgByCoun[df_avgByCoun['country'].isin(keepers)]
    df_avgByCoun = df_avgByCoun.sort_values(by=['rating'])
    df_avgByCoun['country'] = df_avgByCoun['country'].str.capitalize()
    
    # Create a horizontal bar chart
    xRange = (round(min(df_avgByCoun['rating']))) - 1, (round(max(df_avgByCoun['rating'])) + 1)
    y = list(df_avgByCoun.pop('country'))
    x = list(df_avgByCoun.pop('rating'))
    plt.figure(figsize=(10,6))
    plt.barh(width=x, y=y, color = color)
    plt.xlim(xRange)
    plt.xlabel('Rating', fontdict={'size': 20})
    plt.title("Average rating based on Country", fontdict={'size': 20})
    if test:
        plt.show()
    else:
        plt.savefig('static/plots/avgByCoun.png', transparent=True)

def avgByBrew(color, test=False, db=None):
    '''
        Creates a bar chart of the average rating based on brewer.
        Saves the chart as 'avgByBrew.png' in the static/plots directory.
    '''
    # Create a dataframe from the database and filter brewers with more than 2 beers
    df = createDataframe(db, BEER_TABLE)
    keepers = df['brewer'].value_counts().reset_index()
    keepers = dataframeFix(keepers)
    keepers = keepers[keepers['brewer'] > 2]
    keepers = list(keepers.pop('index'))
    keepers.remove('na')

    # Create a dataframe with the average rating by brewer
    df_avgByCoun = df.groupby(['brewer'])['rating'].mean().reset_index()
    df_avgByCoun = df_avgByCoun[df_avgByCoun['brewer'].isin(keepers)]
    df_avgByCoun = df_avgByCoun.sort_values(by=['rating'], ascending=False)
    df_avgByCoun['brewer'] = df_avgByCoun['brewer'].str.capitalize()
    
    # Create a bar chart
    x = list(df_avgByCoun.pop('brewer'))[-15:]
    y = list(df_avgByCoun.pop('rating'))[-15:]
    plt.figure(figsize=(10,6))
    plt.bar(x=x, height=y, color = color)
    plt.title("Average rating based on Brewer", fontdict={'size': 20})
    plt.ylim((5,10))
    plt.ylabel('Rating', fontdict={'size': 20})
    plt.xticks(rotation = 45)
    if test:
        plt.show()
    else:
        plt.savefig('static/plots/avgByBrew.png', transparent=True)

def donoutChart(color, test=False, db=None):
    '''
        Creates a pie chart of the distribution of beer count by country.
        Saves the chart as 'donoutChart.png' in the static/plots directory.
    '''
    # Create a dataframe from the database and count beers by country
    fig, ax = plt.subplots(figsize=(10, 6), subplot_kw=dict(aspect="equal"))
    data = createDataframe(db, BEER_TABLE)
    data = data['country'].value_counts().reset_index()
    data = dataframeFix(data)
    data = data.sort_values(by=['country'], ascending=False)
    data.loc[data['country'] < 3, 'index'] = "other"
    data = data.groupby(['index'])['country'].sum().reset_index()
    data = dataframeFix(data)
    labels = list(data.pop('index'))
    labels = list(map(str.capitalize, labels))
    count = list(data.pop('country'))

    # Create a donut chart
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
    if test:
        plt.show()
    else:
        plt.savefig('static/plots/donoutChart.png', transparent=True)

def main():
    db = f"dbname='{DB}' user='{DB_USER}' host='{DB_HOST}' password='{DB_PASSWORD}'"
    avgByCoun(color='#F78914', test=True, db=db)
    avgByBrew(color='#F78914', test=True, db=db)
    donoutChart(color='#F78914', test=True, db=db)

if __name__ == "__main__":
    main()