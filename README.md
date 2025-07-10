# Postgresql on Linux (Raspberry Pi)
## Authentication mode
By default, after installation, a new user `postgres` is created, this will be the default username, with no password required for login, as `peer` mode is the default.
To turn on password authentication, follow https://stackoverflow.com/questions/18664074/getting-error-peer-authentication-failed-for-user-postgres-when-trying-to-ge and change `peer` -> `md5`

# Start Redis
`redis-server --daemonize yes`

# New Postgresql Cluster on Mac
## Create seprate postgresql database cluster
`initdb <cluster_name>`
Uses system current username as the default username for postgresql

## Start cluster
`pg_ctl -D <cluster_name> -l ./logfile start`

## Connect to cluster
`psql -h <address> -p <port_number> -d <database_name> -U <username>`
On first connect, use `postgres` as <database_name> since it is one of the default database name created with a new cluster

# Create database
`CREATE DATABASE <DATABASE_NAME>;`

# Create Migration
`flask --app app db init`

# Migrate database model
`flask --app app db migrate`

Run this first if migration failed due to "database not up to date" from migrations being off-synced
`flask --app app db stamp head`

# Commit migration
`flask --app app db upgrade`

# Create super user
`flask --app cli create_super_user`

# Create API key for user manually
`flask --app cli create_api_key`

# Start development server
# "run" is from run.py
`flask --app run(.py) run --host 0.0.0.0 --port 5001`
`--debug`: Optional
`--no-reload`: Optional

# Start production server
# equivalent to 'from run(.py) import app' and app.run()
`gunicorn  -c gunicorn.py "run:app"`
