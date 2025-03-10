from flask_blog.models import Base
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect


login_manager = LoginManager()
db = SQLAlchemy(model_class=Base)
migrate = Migrate()
bcrypt = Bcrypt()
csrf = CSRFProtect()