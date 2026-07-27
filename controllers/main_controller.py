"""
controllers/main_controller.py
--------------------------------
The public landing page: the palette generator itself. No login required
to generate and play with a palette — an account is only needed to save one.
"""

from flask import Blueprint, render_template
from utils.color_utils import generate_palette

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    # Render an initial palette server-side so the page has color the
    # instant it loads, before any JavaScript runs.
    initial_colors = generate_palette(count=5, harmony="random")
    return render_template("index.html", initial_colors=initial_colors)
