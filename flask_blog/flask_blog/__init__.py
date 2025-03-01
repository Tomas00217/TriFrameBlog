from flask import Flask

from flask_blog.config import Config
from flask_blog.blogs import bp as blogs_bp
from flask_blog.extensions import db

def create_app(config_class=Config):
    app = Flask(__name__, static_folder=str(config_class.STATIC_FOLDER))
    app.config.from_object(config_class)

    # Initialize Flask extensions here
    db.init_app(app)

    # Register blueprints here
    app.register_blueprint(blogs_bp)

    return app