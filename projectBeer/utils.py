############### ---------- Imports ---------- ###############
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv, dotenv_values

############### ---------- Variables ---------- ###############
load_dotenv()  # Load env
DB = os.getenv('DB')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
BEER_TABLE = os.getenv('BEER_TABLE')

############### ---------- Functions ---------- ###############
''' Turns Beer table into dataframe '''
def createDataframe(db, BEER_TABLE):
    conn = psycopg2.connect(db)
    cur = conn.cursor()
    cur.execute(f'SELECT brewer, name, alc, country, rating, price FROM {BEER_TABLE};')
    df = cur.fetchall()
    df = pd.DataFrame(df, columns = ['brewer', 'name', 'alc', 'country', 'rating', 'price'])
    return df

def dataframeFix(inp):
    '''
        Fixes the dataframe column names to ensure consistency across different environments.
    '''
    if inp.keys()[0] == 'country':
        inp.rename(columns = {'country' : 'index'}, inplace = True)
        inp.rename(columns = {'count' : 'country'}, inplace = True)
    if inp.keys()[0] == 'brewer':
        inp.rename(columns = {'brewer' : 'index'}, inplace = True)
        inp.rename(columns = {'count' : 'brewer'}, inplace = True)
    return inp

############### ---------- Test ---------- ###############
def main():
    db = f"dbname='{DB}' user='{DB_USER}' host='{DB_HOST}' password='{DB_PASSWORD}'"
    print(f"Connecting to database: {db}")
    df = createDataframe(db, BEER_TABLE)
    print(df.head())

if __name__ == "__main__":
    main()