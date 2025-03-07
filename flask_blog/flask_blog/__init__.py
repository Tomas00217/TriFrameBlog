from bs4 import BeautifulSoup
from flask import Flask
from flask_blog.config import Config
from flask_blog.extensions import login_manager, db, migrate, bcrypt, csrf
from flask_blog.repositories.blog_post_repository import BlogPostRepository
from flask_blog.repositories.tag_repository import TagRepository
from flask_blog.services.blog_post_service import BlogPostService
from flask_blog.services.tag_service import TagService

app = Flask(__name__, static_folder=str(Config.STATIC_FOLDER))
app.config.from_object(Config)

# Extensions
login_manager.init_app(app)
db.init_app(app)
migrate.init_app(app, db)
bcrypt.init_app(app)
csrf.init_app(app)

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

@app.template_filter("striptags")
def striptags(value):
    return BeautifulSoup(value, "html.parser").get_text()