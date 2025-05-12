from app import create_app
from app import auth, clockpi

app = create_app()

# Blueprints
print(f"Adding blueprints")
app.register_blueprint(clockpi.bp)
app.register_blueprint(auth.bp)

# Add URL
print(f"Adding URLs")
app.add_url_rule("/", endpoint="index")

if __name__ == "__main__":
    app.run()
