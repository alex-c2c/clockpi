# Initial Setup
- Run `pip install -r requirements.txt` to install all required packages
- Run `flask --app clockpi init-db` to initialize the database.
- Run `flask --app auth createsuperuser` to create a admin account.

# Starting Application
## Running in development server
- Run `flask --app main run --host 0.0.0.0 --port 5001`
- To run in debug mode, add options `--debug --no-reload`, note that redis-subscriber receiving message twice while in debug mode is a bug.

## Running in production server
- Run `/path/to/gunicorn -w 2 -b 0.0.0.0:5001 main:app`

# Setting up Systemctl
# New service file
Create a new service file with the following content and modify the values accordingly
[Unit]
Description=Useful description
After=network.target

[Service]
WorkingDirectory=/path/to/app
Environment=/path/to/venv/bin
ExecStart=/path/to/venv/bin/gunicorn --workers 2 --bind 0.0.0.0:5001 main:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
