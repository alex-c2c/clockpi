# Getting Started

## Dependencies
1. Python 3.13
2. Redis 8.2.2
3. Postgres 17.6

## Postgresql on Linux (Raspberry Pi)
### Authentication mode
By default, after installation, a new user `postgres` is created, this will be the default username, with no password required for login, as `peer` mode is the default.
To turn on password authentication, follow https://stackoverflow.com/questions/18664074/getting-error-peer-authentication-failed-for-user-postgres-when-trying-to-ge and change `peer` -> `md5`

### Create new Postgresql database cluster
`initdb <cluster_name>`
Uses system current username as the default username for postgresql

### Start cluster
`pg_ctl -D <cluster_name> -l ./logfile start`

### Connect to cluster
`psql -h <address> -p <port_number> -d <database_name> -U <username>`
On first connect, use `postgres` as <database_name> since it is one of the default database name created with a new cluster

### Create database
`CREATE DATABASE <DATABASE_NAME>;`

## Application Database Migration
### Create migration
`flask --app app db init`

### Migrate database model
`flask --app app db migrate`

### Commit migration
`flask --app app db upgrade`

## Misc
### Create additional file
Create `<dir_to_clockpi>/.flaskenv`
```bash
FLASK_APP=clockpi.py
FLASK_RUN_HOST=127.0.0.1
FLASK_RUN_PORT=5001
```
Create `<dir_to_clockpi>/.env`
```bash
DATABASE_URL=postgresql://<postgres_user>:<postgres_password>@<postgres_url>:<postgres_port>/clockpi
APP_SETTING=config.ProdConfig
SECRET_KEY=<create_secret_1>
REDIS_URL=redis://:<redis_password>@<redis_url>:<redis_port>/0
LOCAL_API_KEY=<create_secret_2>

DEFAULT_SUPERUSER_USERNAME=<value>
DEFAULT_SUPERUSER_PASSWORD=<value>
DEFAULT_SUPERUSER_DISPNAME=<value>
DEFAULT_SUPERUSER_ROLE=<value>
```

### Create super user
`flask --app cli create_super_user`

### Create API key for user manually
`flask --app cli create_api_key`

## Run Application
### Start postgres
`pg_ctl -D <cluster_name> -l ./logfile start`

### Start Redis
`redis-server --daemonize yes`

### Start Flask App
#### Development server
`flask --app clockpi run --host 127.0.0.1 --port 5001`

#### Production server
`python clockpi.py`
*Uses python-waitress to server the application.*
