DROP TABLE IF EXISTS Beer;
DROP TABLE IF EXISTS country_table;
CREATE table Beer(brewer VARCHAR(265),
				  name VARCHAR(265),
				  alc NUMERIC,
				  country VARCHAR(265),
				  rating NUMERIC,
				  price NUMERIC
);

-- the FROM line should be changed, to match correct dir
COPY Beer(brewer, name, alc, country, rating, price)
FROM 'C:\Users\Public\new_data.csv'
DELIMITER ','
CSV HEADER
encoding 'latin1';

CREATE TABLE country_table AS
SELECT country, CONCAT(UPPER(LEFT(country,1)),
LOWER(RIGHT(country,LENGTH(country)-1)))
AS print FROM contry_table 
ORDER BY print ASC;