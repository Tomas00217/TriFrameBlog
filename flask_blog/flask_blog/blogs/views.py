from flask import render_template
from flask import Blueprint

blogs_bp = Blueprint("blogs", __name__, template_folder="templates")

@blogs_bp.get("/")
def index():
    return render_template("index.html")