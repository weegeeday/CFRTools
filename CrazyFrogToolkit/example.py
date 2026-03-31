import os
from CrazyFrogLib import CFRLevel

# Configuration (Relative to this script)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BMS_EXE = os.path.join(BASE_DIR, "bin", "quickbms.exe")
BMS_SCRIPT = os.path.join(BASE_DIR, "bin", "extract_lzss.bms")

# Example usage (Point this to your game's data folder)
GAME_DATA_ROOT = r"C:\Path\To\CrazyFrogRacer\data"
TEMP_DIR = os.path.join(BASE_DIR, "temp_mod")

def main():
    print("--- CrazyFrog Toolkit Example ---")
    
    if not os.path.exists(GAME_DATA_ROOT):
        print(f"ERROR: Please update GAME_DATA_ROOT in this script to point to your game data!")
        return

    # Initialize level L1
    lvl = CFRLevel(GAME_DATA_ROOT, "L1", BMS_EXE, BMS_SCRIPT)
    
    print(f"Loading {lvl.level_name}...")
    try:
        count = lvl.load(TEMP_DIR)
        print(f"Found {count} textures mapped.")
        
        # Example replacement (if you have an image)
        # lvl.replace_all_with_image("my_new_texture.png")
        # lvl.save()
        
        print("\nToolkit is ready for modding!")
    except Exception as e:
        print(f"Failed to load level: {e}")

if __name__ == "__main__":
    main()
