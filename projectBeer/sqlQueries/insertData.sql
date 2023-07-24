DROP TABLE IF EXISTS Beer;
CREATE table Beer(brewer VARCHAR(265),
				  name VARCHAR(265),
				  alc NUMERIC,
				  county VARCHAR(265),
				  rating NUMERIC,
				  price NUMERIC
);

-- the FROM line should be changed, to match correct dir
COPY Beer(brewer, name, alc, county, rating, price)
FROM 'C:\Users\Public\new_data.csv'
DELIMITER ','
CSV HEADER
encoding 'latin1';