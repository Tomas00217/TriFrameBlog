from flask import Flask
from flask_blog.config import Config
from flask_bcrypt import Bcrypt
from flask_blog.models import Base
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_folder=str(Config.STATIC_FOLDER))
app.config.from_object(Config)

# Extensions
login_manager = LoginManager()
login_manager.init_app(app)
db = SQLAlchemy(app, model_class=Base)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

# Blueprints
from flask_blog.accounts.views import accounts_bp
from flask_blog.blogs.views import blogs_bp
app.register_blueprint(accounts_bp)
app.register_blueprint(blogs_bp)

from flask_blog.accounts.models import EmailUser

login_manager.login_view = "accounts.login"
login_manager.login_message_category = "danger"

@login_manager.user_loader
def load_user(user_id):
    return EmailUser.query.get(int(user_id))