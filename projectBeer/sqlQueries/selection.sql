SELECT * FROM Beer ORDER BY brewer ASC;
SELECT * FROM country_table;

SELECT * FROM BEER 
WHERE LOWER(brewer)
LIKE LOWER('%han%');

SELECT * FROM Beer WHERE country = 'denmark'
AND 8 <= alc AND alc <= 15;

SELECT * FROM account;

SELECT brewer, name, alc, CONCAT(UPPER(LEFT(country,1)),LOWER(RIGHT(country,LENGTH(country)-1))), rating FROM Beer;

SELECT brewer, name, alc, CONCAT(UPPER(LEFT(country,1)),LOWER(RIGHT(country,LENGTH(country)-1))), rating FROM Beer WHERE LOWER(name) LIKE LOWER('%guld%') ORDER BY rating DESC;