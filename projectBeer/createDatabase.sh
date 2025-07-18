#!/bin/bash

# Export all variables from .env file
set -a
source .env
set +a

##### ----- Gloval Variables ----- #####
# Define your DB credentials
DB_NAME="beerdb"
DB_USER=$DB_USER
DB_DEFAULT="postgres"
CSV_PATH="/home/husted42/Documents/github/theDrunkRepository/projectBeer/backupout.csv"

##### ----- Queries ----- #####
# Create table to store beer data
create_beer_table="
CREATE TABLE IF NOT EXISTS beerdata.Beer (
    id SERIAL PRIMARY KEY,
    brewer VARCHAR(255),
    name VARCHAR(255),
    alc DECIMAL(5, 2),
    country VARCHAR(100),
    rating DECIMAL(4, 1),
    price DECIMAL(5, 2)
);
"

create_user_table="
CREATE TABLE IF NOT EXISTS beerdata.Users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"

insert_user="
INSERT INTO beerdata.Users(username, password) VALUES (
    'husted42', 
    'e177c5cfc7b27e9c4aa1549d01b372f6'
);
"

##### ----- Run ----- #####
# Create the database if it doesn't exist
psql -U "$DB_USER" -d "$DB_DEFAULT" -c "CREATE DATABASE $DB_NAME;"
if [ $? -ne 0 ]; then # Check if exit status is not zero, indicating an error
    echo "Database '$DB_NAME' already exists or could not be created."
    exit 1
fi
echo "Database '$DB_NAME' created successfully."


# Create the schema if it doesn't exist
psql -U "$DB_USER" -d "$DB_NAME" -c "CREATE SCHEMA IF NOT EXISTS beerdata;"
if [ $? -ne 0 ]; then
    echo "Schema 'beerdata' could not be created."
    exit 1
fi
echo "Schema 'beerdata' created successfully."  

# Create the tables
psql -U "$DB_USER" -d "$DB_NAME" -c "$create_beer_table"
if [ $? -ne 0 ]; then
    echo "Table 'Beer' could not be created."
    exit 1
fi
echo "Table 'Beer' created successfully."

psql -U "$DB_USER" -d "$DB_NAME" -c "$create_user_table"
if [ $? -ne 0 ]; then
    echo "Table 'Users' could not be created."
    exit 1
fi
echo "Table 'Users' created successfully."

# Insert initial data
psql -U "$DB_USER" -d "$DB_NAME" -c "$insert_user"
if [ $? -ne 0 ]; then
    echo "User could not be inserted."
    exit 1
fi
echo "User inserted successfully."

# Import data from CSV file
psql -U "$DB_USER" -d "$DB_NAME" -c "\COPY beerdata.Beer(brewer, name, alc, country, rating, price) FROM '$CSV_PATH' WITH (FORMAT csv, HEADER true);"
if [ $? -ne 0 ]; then
    echo "Data could not be imported from CSV file."
    exit 1
fi
echo "Data imported successfully from '$CSV_PATH'."