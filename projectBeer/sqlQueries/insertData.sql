DROP TABLE IF EXISTS Beer;
DROP TABLE IF EXISTS country_table;
DROP TABLE IF EXISTS account;
CREATE table Beer(brewer VARCHAR(265),
				  name VARCHAR(265),
				  alc NUMERIC,
				  country VARCHAR(265),
				  rating NUMERIC,
				  price NUMERIC
);

CREATE table account(id SERIAL,
					username VARCHAR(265),
					password VARCHAR(265),
					PRIMARY KEY(id)
);
INSERT INTO account(username, password) VALUES ('husted42', 'e177c5cfc7b27e9c4aa1549d01b372f6');


-- the FROM line should be changed, to match correct dir
COPY Beer(brewer, name, alc, country, rating, price)
FROM 'C:\Users\Public\new_data.csv'
DELIMITER ','
CSV HEADER
encoding 'latin1';

-- Table for dropdown form
CREATE TABLE country_table AS
SELECT DISTINCT country, CONCAT(UPPER(LEFT(country,1)),
LOWER(RIGHT(country,LENGTH(country)-1)))
AS print FROM Beer 
ORDER BY print ASC;