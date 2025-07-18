## Deployment
To deploy this project you need to have the modules
- flask 
- psycopg2

```bash
$ pip install -r requirements.txt
```

# prerequisites
### Install requirements
```bash
$ pip install -r requirements.txt
```

### Enviroment file
Change the name of the env file to .env and update variables if needed.
 - NOTE: It's important that there is no spaces, otherwise it will not work for the .sh script

### Change psql authentication
Postgres by default uses peer authentication meaning that it expect the user to have the same username as the system username. Lucikly this can easily be changed: 

Locate the configuration file
```
sudo find / -name "pg_hba.conf"
```

Edit the file to use md5
```
sudo nano /etc/postgresql/<version>/main/pg_hba.conf
```

Change the following line:
```
local   all             postgres                                peer
```
to
```
local   all             postgres                                md5
```

### Create the database
Create the database by running the script: `./beerdata.sh`
 - You may need to mark is as an executable `chmod +x beerdata.sh`

