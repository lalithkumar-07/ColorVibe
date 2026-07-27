"""
utils/color_utils.py
---------------------
Pure color math: conversions between hex/RGB/HSL, and the harmony rules
used to generate a palette (complementary, analogous, triadic, monochromatic,
random). No Flask or database code lives here, so it's easy to unit test.
"""

import random
import re

HEX_RE = re.compile(r"^#?[0-9a-fA-F]{6}$")


def is_valid_hex(value):
    """True if value looks like a 6-digit hex color, with or without '#'."""
    return bool(value) and bool(HEX_RE.match(value.strip()))


def normalize_hex(value):
    """Ensure a hex string is upper-case and prefixed with '#'."""
    value = value.strip()
    if not value.startswith("#"):
        value = "#" + value
    return value.upper()


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    r, g, b = (max(0, min(255, round(c))) for c in rgb)
    return "#{:02X}{:02X}{:02X}".format(r, g, b)


def rgb_to_hsl(rgb):
    r, g, b = (c / 255.0 for c in rgb)
    max_c, min_c = max(r, g, b), min(r, g, b)
    l = (max_c + min_c) / 2.0

    if max_c == min_c:
        h = s = 0.0
    else:
        d = max_c - min_c
        s = d / (2.0 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
        if max_c == r:
            h = (g - b) / d + (6.0 if g < b else 0.0)
        elif max_c == g:
            h = (b - r) / d + 2.0
        else:
            h = (r - g) / d + 4.0
        h /= 6.0

    return h * 360.0, s * 100.0, l * 100.0


def _hue_to_rgb(p, q, t):
    if t < 0:
        t += 1
    if t > 1:
        t -= 1
    if t < 1 / 6:
        return p + (q - p) * 6 * t
    if t < 1 / 2:
        return q
    if t < 2 / 3:
        return p + (q - p) * (2 / 3 - t) * 6
    return p


def hsl_to_rgb(h, s, l):
    h, s, l = (h % 360) / 360.0, s / 100.0, l / 100.0

    if s == 0:
        r = g = b = l
    else:
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = _hue_to_rgb(p, q, h + 1 / 3)
        g = _hue_to_rgb(p, q, h)
        b = _hue_to_rgb(p, q, h - 1 / 3)

    return r * 255, g * 255, b * 255


def hex_to_hsl(hex_color):
    return rgb_to_hsl(hex_to_rgb(hex_color))


def hsl_to_hex(h, s, l):
    return rgb_to_hex(hsl_to_rgb(h, s, l))


def relative_luminance(hex_color):
    """Perceived brightness (0-255), used to decide black/white text on a swatch."""
    r, g, b = hex_to_rgb(hex_color)
    return (0.299 * r) + (0.587 * g) + (0.114 * b)


def readable_text_color(hex_color):
    """Return '#111111' or '#FAFAFA' depending on which reads better on hex_color."""
    return "#111111" if relative_luminance(hex_color) > 150 else "#FAFAFA"


def random_hsl(h_range=(0, 360), s_range=(45, 85), l_range=(35, 70)):
    h = random.uniform(*h_range)
    s = random.uniform(*s_range)
    l = random.uniform(*l_range)
    return h, s, l


# ---------------------------------------------------------------------
# Harmony generators. Each returns a list of `count` hex strings, given
# a base hue (0-360) to build the relationship around.
# ---------------------------------------------------------------------

def _jitter(value, spread):
    return value + random.uniform(-spread, spread)


def harmony_complementary(base_h, count):
    colors = []
    for i in range(count):
        h = base_h if i % 2 == 0 else base_h + 180
        h = _jitter(h, 8)
        s = random.uniform(50, 85)
        l = random.uniform(30, 75) if i % 2 == 0 else random.uniform(25, 70)
        colors.append(hsl_to_hex(h, s, l))
    return colors


def harmony_analogous(base_h, count):
    step = 28
    start = base_h - (step * (count // 2))
    colors = []
    for i in range(count):
        h = start + i * step
        s = random.uniform(45, 80)
        l = random.uniform(30, 72)
        colors.append(hsl_to_hex(h, s, l))
    return colors


def harmony_triadic(base_h, count):
    anchors = [base_h, base_h + 120, base_h + 240]
    colors = []
    for i in range(count):
        h = _jitter(anchors[i % 3], 6)
        s = random.uniform(50, 82)
        l = random.uniform(30, 72)
        colors.append(hsl_to_hex(h, s, l))
    return colors


def harmony_monochromatic(base_h, count):
    colors = []
    lights = [92, 74, 56, 38, 20][:count]
    while len(lights) < count:
        lights.append(random.uniform(15, 90))
    for l in lights:
        s = random.uniform(35, 65)
        colors.append(hsl_to_hex(base_h, s, l))
    return colors


def harmony_random(base_h, count):
    colors = []
    for _ in range(count):
        h, s, l = random_hsl()
        colors.append(hsl_to_hex(h, s, l))
    return colors


HARMONIES = {
    "complementary": harmony_complementary,
    "analogous": harmony_analogous,
    "triadic": harmony_triadic,
    "monochromatic": harmony_monochromatic,
    "random": harmony_random,
}


def generate_palette(count=5, harmony="random", locked=None, base_hex=None):
    """
    Build a palette of `count` hex colors following the given harmony rule.

    locked: optional dict of {index: hex} for swatches that must stay fixed
            (e.g. the user locked a swatch before regenerating).
    base_hex: optional hex color to derive the base hue from. If omitted,
              a random hue is chosen (or taken from the first locked color).
    """
    locked = locked or {}
    harmony = harmony if harmony in HARMONIES else "random"

    if base_hex and is_valid_hex(base_hex):
        base_h, _, _ = hex_to_hsl(normalize_hex(base_hex))
    elif locked:
        first_locked = next(iter(locked.values()))
        base_h, _, _ = hex_to_hsl(normalize_hex(first_locked))
    else:
        base_h = random.uniform(0, 360)

    generated = HARMONIES[harmony](base_h, count)

    # Overlay any locked swatches back onto the generated list, preserving position.
    result = []
    for i in range(count):
        if i in locked:
            result.append(normalize_hex(locked[i]))
        else:
            result.append(generated[i] if i < len(generated) else generated[-1])
    return result
