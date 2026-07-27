"""
controllers/palette_controller.py
-----------------------------------
CRUD routes for saved palettes, plus the dashboard listing view.
Every route that touches a specific palette re-checks that it belongs to
the logged-in user before reading or writing (ownership check), so one
user can never modify another user's data by guessing an id.
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify

from models.palette import Palette
from utils.validators import validate_palette_name
from utils.color_utils import is_valid_hex, normalize_hex

palette_bp = Blueprint("palette", __name__)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to continue.", "error")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


@palette_bp.route("/dashboard")
@login_required
def dashboard():
    palettes = Palette.find_by_user(session["user_id"])
    return render_template("dashboard.html", palettes=palettes)


@palette_bp.route("/palettes", methods=["POST"])
@login_required
def save_palette():
    """Save a newly generated palette. Accepts JSON (fetch from generator.js)."""
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    colors = data.get("colors") or []
    harmony = data.get("harmony") or "random"

    errors = validate_palette_name(name)

    if not colors or not isinstance(colors, list):
        errors.append("A palette needs at least one color.")
    else:
        cleaned = []
        for c in colors:
            if not is_valid_hex(str(c)):
                errors.append(f"'{c}' is not a valid hex color.")
                break
            cleaned.append(normalize_hex(str(c)))
        colors = cleaned

    if Palette.count_by_user(session["user_id"]) >= 200:
        errors.append("You've reached the 200 saved palette limit. Delete one to save more.")

    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    palette_id = Palette.create(session["user_id"], name, colors, harmony)
    return jsonify({"success": True, "id": palette_id}), 201


@palette_bp.route("/palettes/<int:palette_id>", methods=["GET"])
@login_required
def view_palette(palette_id):
    palette = Palette.find_by_id(palette_id)
    if not palette or palette.user_id != session["user_id"]:
        flash("Palette not found.", "error")
        return redirect(url_for("palette.dashboard"))
    return render_template("palette_detail.html", palette=palette)


@palette_bp.route("/palettes/<int:palette_id>", methods=["PUT"])
@login_required
def rename_palette(palette_id):
    palette = Palette.find_by_id(palette_id)
    if not palette or palette.user_id != session["user_id"]:
        return jsonify({"success": False, "errors": ["Palette not found."]}), 404

    data = request.get_json(silent=True) or {}
    new_name = (data.get("name") or "").strip()
    errors = validate_palette_name(new_name)
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    Palette.rename(palette_id, session["user_id"], new_name)
    return jsonify({"success": True})


@palette_bp.route("/palettes/<int:palette_id>", methods=["DELETE"])
@login_required
def delete_palette(palette_id):
    palette = Palette.find_by_id(palette_id)
    if not palette or palette.user_id != session["user_id"]:
        return jsonify({"success": False, "errors": ["Palette not found."]}), 404

    Palette.delete(palette_id, session["user_id"])
    return jsonify({"success": True})
