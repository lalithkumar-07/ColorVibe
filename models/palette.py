"""
models/palette.py
-------------------
Database access for saved palettes. `colors` is persisted as a JSON array
of hex strings in a MySQL JSON column.
"""

import json
from database.db import execute


class Palette:
    def __init__(self, id, user_id, name, colors, harmony, is_public=0,
                 created_at=None, updated_at=None):
        self.id = id
        self.user_id = user_id
        self.name = name
        # MySQL's connector already decodes JSON columns to Python lists,
        # but guard against a raw string just in case.
        self.colors = json.loads(colors) if isinstance(colors, str) else colors
        self.harmony = harmony
        self.is_public = bool(is_public)
        self.created_at = created_at
        self.updated_at = updated_at

    # ---- Create ------------------------------------------------------
    @staticmethod
    def create(user_id, name, colors, harmony="random"):
        new_id = execute(
            "INSERT INTO palettes (user_id, name, colors, harmony) VALUES (%s, %s, %s, %s)",
            (user_id, name, json.dumps(colors), harmony),
            commit=True,
        )
        return new_id

    # ---- Read ----------------------------------------------------------
    @staticmethod
    def find_by_id(palette_id):
        row = execute("SELECT * FROM palettes WHERE id = %s", (palette_id,), fetchone=True)
        return Palette(**row) if row else None

    @staticmethod
    def find_by_user(user_id):
        rows = execute(
            "SELECT * FROM palettes WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,),
            fetchall=True,
        )
        return [Palette(**row) for row in rows]

    @staticmethod
    def count_by_user(user_id):
        row = execute(
            "SELECT COUNT(*) AS total FROM palettes WHERE user_id = %s",
            (user_id,),
            fetchone=True,
        )
        return row["total"] if row else 0

    # ---- Update ----------------------------------------------------------
    @staticmethod
    def rename(palette_id, user_id, new_name):
        """Only renames if the palette belongs to user_id (ownership check)."""
        execute(
            "UPDATE palettes SET name = %s WHERE id = %s AND user_id = %s",
            (new_name, palette_id, user_id),
            commit=True,
        )

    # ---- Delete ----------------------------------------------------------
    @staticmethod
    def delete(palette_id, user_id):
        """Only deletes if the palette belongs to user_id (ownership check)."""
        execute(
            "DELETE FROM palettes WHERE id = %s AND user_id = %s",
            (palette_id, user_id),
            commit=True,
        )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "colors": self.colors,
            "harmony": self.harmony,
            "created_at": str(self.created_at) if self.created_at else None,
        }
