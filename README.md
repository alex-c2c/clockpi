# Create seprate postgresql database cluster
`initdb <cluster_name>`

# Start cluster
`pg_ctl -D <cluster_name> -l ./logfile start`

# Connect to cluster
`psql -h <address> -p <port_number> -d <database_name> -U <username>`
On first connect, use `postgres` as <database_name> since it is one of the default database name created with a new cluster

# Create database
`CREATE DATABASE <DATABASE_NAME>;`

# Create Migration
`flask db init`

# Migrate database model
`flask db migrate`

# Commit migration
`flask db upgrade`

# Start development server
# "app" is from run.py
`flask --app app run --host 0.0.0.0 --port 5001`
`--debug`: Optional
`--no-reload`: Optional

# Start production server
# equivalent to 'from run(.py) import app' and app.run()
`gunicorn  -c gunicorn.py "run:app"`
