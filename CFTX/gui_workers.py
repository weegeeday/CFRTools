import os
import sys
from PySide6.QtCore import QObject, Signal, QThread
from PIL import Image

# Ensure CrazyFrogToolkit is in the path
ROOT = os.path.dirname(os.path.abspath(__file__))
TOOLKIT_PATH = os.path.join(ROOT, "CrazyFrogToolkit")
if TOOLKIT_PATH not in sys.path:
    sys.path.insert(0, TOOLKIT_PATH)

from CrazyFrogLib import CFRLevel

class LoadWorker(QObject):
    finished = Signal(object, str)  # level_obj, error_msg
    progress = Signal(int, int)     # current, total

    def __init__(self, level_path, bms_exe, bms_script, temp_dir):
        super().__init__()
        self.level_path = level_path
        self.bms_exe = bms_exe
        self.bms_script = bms_script
        self.temp_dir = temp_dir

    def run(self):
        try:
            # Determine data_dir and level_name from path
            # Expected path: .../LEVEL_NAME/LEVEL_NAMEgfx.pc
            data_dir = os.path.dirname(os.path.dirname(self.level_path))
            level_name = os.path.basename(os.path.dirname(self.level_path))
            
            level = CFRLevel(data_dir, level_name, self.bms_exe, self.bms_script)
            level.load(self.temp_dir)
            self.finished.emit(level, "")
        except Exception as e:
            self.finished.emit(None, str(e))

class SaveWorker(QObject):
    finished = Signal(bool, str)

    def __init__(self, level, save_path=None):
        super().__init__()
        self.level = level
        self.save_path = save_path

    def run(self):
        try:
            # If save_path is provided, we might need to handle "Save As" 
            # currently CFRLevel.save() overwrites. 
            # We'll handle custom save paths by copying the result if needed.
            self.level.save()
            self.finished.emit(True, "")
        except Exception as e:
            self.finished.emit(False, str(e))

class ExportWorker(QObject):
    finished = Signal(bool, str)

    def __init__(self, level, output_dir):
        super().__init__()
        self.level = level
        self.output_dir = output_dir

    def run(self):
        try:
            self.level.export_all(self.output_dir)
            self.finished.emit(True, "")
        except Exception as e:
            self.finished.emit(False, str(e))
