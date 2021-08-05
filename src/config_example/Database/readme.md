# The env file format

```ini
host=""
database=""
user=""
password=""
ssl=""
```

## host

The hostname of the database server.

## database

The name of the database.

## user

The username to use when connecting to the database.

## password

The password to use when connecting to the database.

## ssl

Whether to use ssl encrypton when connecting to the database
<br>

### Local Machine

------------------------------------------------------------
If you run the database on the local machine, postgresql sets some default values for the host user and password, if you wish to keep those then this is what your env should look like

```ini
host="localhost"
database="postgres"
user="postgres"
password="password"
ssl="disable"
```
