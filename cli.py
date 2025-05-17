import getpass
import secrets

from app import create_app, db
from app.auth.logic import is_password_valid, is_username_valid
from app.models import AccountModel, ApiKeyModel

from werkzeug.security import generate_password_hash


app = create_app()


@app.cli.command("create_super_user")
def cli_create_super_user() -> None:
	username: str = str(input(f"Username: "))
	if not is_username_valid(username):
		print(f"[ERROR] Unable to create super user")
		return

	password: str = getpass(f"Password: ")
	if not is_password_valid(password):
		print(f"[ERROR] Unable to create super user")
		return

	new_acct: AccountModel = AccountModel(username, generate_password_hash(password))
	db.session.add(new_acct)
	db.session.commit()

	print(f"Created super user {new_acct.id}:{new_acct.username}")


@app.cli.command("create_api_key")
def cli_create_api_key() -> None:
	id: str = str(input(f"Account ID: "))
	if not id.isdigit():
		print(f"[ERROR] Invalid account ID")
		return

	id: int = int(id)
	account: AccountModel = AccountModel.query.filter_by(id=id).first()
	if account is None:
		print(f"[ERROR] ID: {id} does not exists")
		return

	comment: str = str(input(f"API Key comment: "))
	key: str = secrets.token_hex(128)

	new_api_key: ApiKeyModel = ApiKeyModel(id, key, comment)
	db.session.add(new_api_key)
	db.session.commit()

	print(f"Created new API key for account {account.id}:{account.username} {key}")
