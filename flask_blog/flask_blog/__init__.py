import os
from pathlib import Path
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import Flask, send_from_directory
from flask_admin import Admin
from flask_blog.accounts.commands import register_commands
from flask_blog.container import container
from flask_blog.accounts.models import EmailUser
from flask_blog.admin import AdminModelView, MyAdminIndexView
from flask_blog.blogs.admin import BlogPostAdminView
from flask_blog.blogs.models import BlogPost, Tag
from flask_blog.extensions import login_manager, db, migrate, bcrypt, csrf, seeder
from flask_blog.accounts.admin import EmailUserAdminView

BASE_DIR = Path(__file__).resolve().parent.parent

default_env = os.environ.get("FLASK_ENV", "development")
env_file = BASE_DIR / (".env" if default_env == "development" else f".env.{default_env}")
load_dotenv(dotenv_path=env_file if env_file.exists() else None)

from flask_blog.config import config

def create_app(config_name = None):
    app = Flask(__name__)
    
    if not config_name:
        config_name = os.environ.get("FLASK_ENV", "default")
    app.config.from_object(config[config_name])

    if app.config["USE_LOCAL_STORAGE"]:
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

        @app.route('/media/<path:filename>')
        def uploaded_file(filename):
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    app.static_folder = app.config["STATIC_FOLDER"]


    # Extensions
    login_manager.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    csrf.init_app(app)
    seeder.init_app(app, db)

    # Blueprints
    from flask_blog.accounts.views import accounts_bp
    from flask_blog.blogs.views import blogs_bp
    app.register_blueprint(accounts_bp)
    app.register_blueprint(blogs_bp)

    # Admin
    admin = Admin(app, name='TriFrameBlog', template_mode='bootstrap3', index_view=MyAdminIndexView())
    admin.add_view(EmailUserAdminView(EmailUser, db.session))
    admin.add_view(BlogPostAdminView(BlogPost, db.session, blog_service=container.blog_service))
    admin.add_view(AdminModelView(Tag, db.session))

    login_manager.login_view = "accounts.login"
    login_manager.login_message_category = "danger"

    # CLI commands
    register_commands(app)

    @login_manager.user_loader
    def load_user(user_id):
        return container.user_repo.get_by_id(user_id)

    @app.template_filter("striptags")
    def striptags(value):
        return BeautifulSoup(value, "html.parser").get_text()
    
    return app