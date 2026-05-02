# CrazyFrogLib

Python library for modding **Crazy Frog Racer** (PC).

## Features

- **Archive**: Decompress/reimport LZSS-compressed `.PC` archives via QuickBMS
- **Texture**: Extract and inject PS2 TIM2 paletted textures (4-bit/8-bit, BGRA swizzle)
- **Mesh**: Parse DLWM 3D geometry (vertices, UVs, faces, materials)
- **Level**: High-level API combining all of the above

## Quick Start

```python
from CrazyFrogLib import CFRLevel

level = CFRLevel(
    data_dir="data",
    level_name="L1",
    bms_exe="quickbms/quickbms.exe",
    bms_script="extract_lzss.bms"
)

# Export textured OBJ (mesh + textures in one call)
level.export_textured_obj("output/L1_export")

# Or work with textures independently
level.load("temp")
level.export_all("output/textures")

# Replace all textures
level.replace_all_with_image("my_image.jpg")
level.save()
```

## Mesh Format (DLWM)

| Field | Format | Notes |
|-------|--------|-------|
| Vertex | 16 bytes | `int16 X,Y,Z,W, U,V, A,B` |
| Face | 20 bytes | `u16 mat, pad, i1,f1, i2,f2, i3,f3, tA,tB` |
| UV range | 0–4095 | Fixed-point, divide by 4096 |

## Requirements

- Python 3.8+
- Pillow (`pip install Pillow`)
- QuickBMS (included in toolkit)
