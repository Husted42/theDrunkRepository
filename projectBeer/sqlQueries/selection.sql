SELECT * FROM Beer ORDER BY brewer ASC;
SELECT * FROM country_table;

SELECT * FROM BEER 
WHERE LOWER(brewer)
LIKE LOWER('%han%');

SELECT * FROM Beer WHERE country = 'denmark'
AND 8 <= alc AND alc <= 15;