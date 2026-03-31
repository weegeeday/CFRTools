# CrazyFrogLib

A Python library for reverse engineering and modding *Crazy Frog Racer* (PC) game data.

## Features
- **PCArchive**: Decompress and re-inject files into LZSS-compressed `.PC` archives.
- **PS2Texture**: Handle PS2-style swizzled palettes and 4-bit/8-bit pixel formats.
- **CFRLevel**: Manage level-specific texture mapping (`tin` + `gfx`).

## Usage Example

### Mass Replace All Textures in a Level
```python
from CrazyFrogLib import CFRLevel

# Paths
DATA_DIR = r"c:\Users\simon\Downloads\CrazyFrog\GAME_TEST\data"
BMS_EXE = r"c:\Users\simon\Downloads\CrazyFrog\data\L1\quickbms\quickbms.exe"
BMS_SCRIPT = r"c:\Users\simon\Downloads\CrazyFrog\data\L1\extract_lzss.bms"
TEMP_DIR = r"c:\Users\simon\Downloads\CrazyFrog\GAME_TEST_P\temp_lib"

# Initialize level
level = CFRLevel(DATA_DIR, "L1", BMS_EXE, BMS_SCRIPT)

# Load data and metadata
level.load(TEMP_DIR)

# Global replacement
level.replace_all_with_image("newImage.jpg")

# Save back to .pc
level.save()
```
