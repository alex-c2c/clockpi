from app import create_app
from app import clockpi

app = create_app()

# Blueprints
app.register_blueprint(clockpi.bp)

# Add URL
app.add_url_rule("/", endpoint="index")
