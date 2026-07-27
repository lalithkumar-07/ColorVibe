"""
controllers/api_controller.py
-------------------------------
Small JSON API the frontend calls to generate colors server-side. Keeping
the harmony math in Python (utils/color_utils.py) means the same logic
could later be reused by a CLI, tests, or another client without
duplicating it in JavaScript.
"""

from flask import Blueprint, request, jsonify
from utils.color_utils import generate_palette, is_valid_hex, normalize_hex

api_bp = Blueprint("api", __name__, url_prefix="/api")

VALID_HARMONIES = {"random", "complementary", "analogous", "triadic", "monochromatic"}


@api_bp.route("/generate", methods=["POST"])
def generate():
    """
    Body: { "count": 5, "harmony": "analogous", "locked": {"0": "#FF0000"} }
    Returns: { "colors": ["#...", ...], "harmony": "analogous" }
    """
    data = request.get_json(silent=True) or {}

    count = data.get("count", 5)
    try:
        count = int(count)
    except (TypeError, ValueError):
        count = 5
    count = max(2, min(count, 10))

    harmony = data.get("harmony", "random")
    if harmony not in VALID_HARMONIES:
        harmony = "random"

    raw_locked = data.get("locked") or {}
    locked = {}
    for key, hex_value in raw_locked.items():
        try:
            idx = int(key)
        except (TypeError, ValueError):
            continue
        if is_valid_hex(str(hex_value)):
            locked[idx] = normalize_hex(str(hex_value))

    colors = generate_palette(count=count, harmony=harmony, locked=locked)
    return jsonify({"colors": colors, "harmony": harmony})
