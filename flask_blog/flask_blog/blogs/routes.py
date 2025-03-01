from flask_blog.blogs import bp
from flask import render_template

@bp.get('/')
def index():
    return render_template('base.html')