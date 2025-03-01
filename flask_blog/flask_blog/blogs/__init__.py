from flask import Blueprint

bp = Blueprint('blogs', __name__)

from flask_blog.blogs import routes