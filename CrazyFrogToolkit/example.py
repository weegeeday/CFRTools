"""
CrazyFrog Toolkit - Example Script
Export a textured 3D model from any Crazy Frog Racer level.

Requirements:
  - Python 3.8+, Pillow (pip install Pillow)
  - QuickBMS (download from https://aluigi.altervista.org/quickbms.htm)
  - extract_lzss.bms script (included)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from CrazyFrogLib import CFRLevel, DLWMMesh

# ── Configuration (edit these paths) ──────────────────────
GAME_DATA   = r"C:\path\to\CrazyFrogRacer\data"
BMS_EXE     = r"C:\path\to\quickbms\quickbms.exe"
BMS_SCRIPT  = os.path.join(os.path.dirname(__file__), "extract_lzss.bms")
LEVEL       = "L1"     # L1 through L16
OUTPUT      = "output"

# ── Export textured OBJ ───────────────────────────────────
print(f"Exporting {LEVEL} as textured OBJ...")
level = CFRLevel(GAME_DATA, LEVEL, BMS_EXE, BMS_SCRIPT)
obj_path = level.export_textured_obj(
    output_dir=os.path.join(OUTPUT, f"{LEVEL}_export")
)
print(f"Done! Open in Blender: {obj_path}")
print(f"  Vertices: {level.mesh.vert_count}")
print(f"  Faces:    {level.mesh.face_count}")
print(f"  Textures: {len(level.textures)}")

# ── Replace all textures (optional) ──────────────────────
# level.replace_all_with_image("my_image.jpg")
# level.save()
