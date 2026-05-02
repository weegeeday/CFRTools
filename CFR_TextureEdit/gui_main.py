import os
import sys
import shutil
import tempfile
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QScrollArea, QGridLayout, QFileDialog, QMessageBox, QProgressDialog,
    QMenuBar, QMenu, QStatusBar
)
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PIL import Image

# Ensure CrazyFrogToolkit is in the path
ROOT = os.path.dirname(os.path.abspath(__file__))
TOOLKIT_PATH = os.path.join(ROOT, "CrazyFrogToolkit")
if TOOLKIT_PATH not in sys.path:
    sys.path.insert(0, TOOLKIT_PATH)

# Import local GUI modules
from gui_style import STYLE_SHEET
from gui_workers import LoadWorker, SaveWorker, ExportWorker
from gui_components import TextureTile, FileSidebar
from gui_dialogs import ReplaceDialog, HelpDialog, ImageViewerDialog

class CFTXMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crazy Frog Texture Tool (CFTX)")
        self.resize(1200, 800)
        self.setStyleSheet(STYLE_SHEET)
        
        self.current_level = None
        self.current_level_path = None
        self.temp_dir = tempfile.mkdtemp(prefix="cftx_")
        
        # Paths for BMS (relative to script)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.bms_exe = os.path.join(base_dir, "CrazyFrogToolkit", "bin", "quickbms.exe")
        self.bms_script = os.path.join(base_dir, "CrazyFrogToolkit", "extract_lzss.bms")
        
        self.init_ui()
        self.create_menu()
        self.statusBar().showMessage("Ready")

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar (Left)
        self.sidebar = FileSidebar()
        self.sidebar.fileSelected.connect(self.load_level)
        main_layout.addWidget(self.sidebar)
        
        # Grid Area (Right)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.grid_content = QWidget()
        self.grid_content.setObjectName("scrollContent")
        self.grid_layout = QGridLayout(self.grid_content)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        scroll.setWidget(self.grid_content)
        main_layout.addWidget(scroll)

    def create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        
        open_act = file_menu.addAction("&Open Level...")
        open_act.setShortcut("Ctrl+O")
        open_act.triggered.connect(self.on_open_file)
        
        save_act = file_menu.addAction("&Save")
        save_act.setShortcut("Ctrl+S")
        save_act.triggered.connect(self.on_save)
        
        save_as_act = file_menu.addAction("Save &As...")
        save_as_act.triggered.connect(self.on_save_as)
        
        file_menu.addSeparator()
        
        export_all_act = file_menu.addAction("&Export All Textures...")
        export_all_act.triggered.connect(self.on_export_all)
        
        exit_act = file_menu.addAction("&Exit")
        exit_act.triggered.connect(self.close)
        
        help_menu = menu_bar.addMenu("&Help")
        about_act = help_menu.addAction("&About...")
        about_act.triggered.connect(self.on_about)
        
        debug_act = help_menu.addAction("&Debug Dump")
        debug_act.triggered.connect(self.on_debug_dump)

    def on_open_file(self):
        # We look for a *gfx.pc file usually
        path, _ = QFileDialog.getOpenFileName(self, "Open Crazy Frog Level GFX", "", "GFX Archive (*gfx.pc)")
        if path:
            item = self.sidebar.add_file(path)
            self.sidebar.setCurrentItem(item)
            self.load_level(path)

    def load_level(self, path):
        if not os.path.exists(self.bms_exe):
            QMessageBox.critical(self, "Error", f"QuickBMS not found at: {self.bms_exe}")
            return
            
        self.current_level_path = path
        self.statusBar().showMessage(f"Loading {os.path.basename(path)}...")
        
        # Clear grid
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)
        
        # Start background load
        self.load_thread = QThread()
        self.worker = LoadWorker(path, self.bms_exe, self.bms_script, self.temp_dir)
        self.worker.moveToThread(self.load_thread)
        self.load_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_load_finished)
        self.load_thread.start()

    @Slot(object, str)
    def on_load_finished(self, level, error):
        self.load_thread.quit()
        if error:
            QMessageBox.critical(self, "Error", f"Failed to load level: {error}")
            self.statusBar().showMessage("Load failed.")
            return
            
        self.current_level = level
        self.statusBar().showMessage(f"Loaded {len(level.textures)} textures.")
        
        # Populate grid
        cols = 4 # Might want to dynamic scaling based on width
        for i, t in enumerate(level.textures):
            try:
                # Need access to the raw texture extraction for preview
                # We'll import it here to avoid bloat
                from CrazyFrogLib.texture import PS2Texture
                img, _ = PS2Texture.extract(level._gfx_data, t['offset'], t['size'], t['pitch'], t['bit_depth'])
                
                tile = TextureTile(i, img, t)
                tile.replaceRequested.connect(self.on_replace_requested)
                tile.exportRequested.connect(self.on_export_requested)
                tile.doubleClicked.connect(self.on_texture_double_clicked)
                
                row, col = divmod(i, cols)
                self.grid_layout.addWidget(tile, row, col)
            except Exception as e:
                print(f"Error loading texture {i}: {e}")

    def on_replace_requested(self, tex_id):
        t = self.current_level.textures[tex_id]
        from CrazyFrogLib.texture import PS2Texture
        img, _ = PS2Texture.extract(self.current_level._gfx_data, t['offset'], t['size'], t['pitch'], t['bit_depth'])
        
        dlg = ReplaceDialog(img, t['pitch'], img.height, self)
        if dlg.exec_():
            new_pil, mode = dlg.get_result()
            self.current_level.replace_texture(tex_id, new_pil, mode)
            # Refresh tile preview
            widget = self.grid_layout.itemAt(tex_id).widget()
            if isinstance(widget, TextureTile):
                widget.set_image(new_pil)
            self.statusBar().showMessage(f"Texture {tex_id} replaced in memory.")

    def on_texture_double_clicked(self, tex_id):
        t = self.current_level.textures[tex_id]
        from CrazyFrogLib.texture import PS2Texture
        img, _ = PS2Texture.extract(self.current_level._gfx_data, t['offset'], t['size'], t['pitch'], t['bit_depth'])
        
        dlg = ImageViewerDialog(img, f"Texture {tex_id} ({t['pitch']}px width)", self)
        dlg.exec_()

    def on_export_requested(self, tex_id):
        t = self.current_level.textures[tex_id]
        from CrazyFrogLib.texture import PS2Texture
        img, _ = PS2Texture.extract(self.current_level._gfx_data, t['offset'], t['size'], t['pitch'], t['bit_depth'])
        
        path, _ = QFileDialog.getSaveFileName(self, "Export Texture", f"tex_{tex_id}.png", "PNG Images (*.png)")
        if path:
            img.save(path)
            self.statusBar().showMessage(f"Texture {tex_id} exported to {os.path.basename(path)}")

    def on_export_all(self):
        if not self.current_level: return
        dir_path = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if dir_path:
            self.current_level.export_all(dir_path)
            QMessageBox.information(self, "Done", f"All textures exported to {dir_path}")

    def on_about(self):
        dlg = HelpDialog(self)
        dlg.debugDumpRequested.connect(self.on_debug_dump)
        dlg.exec_()

    def on_debug_dump(self):
        if not self.current_level:
            QMessageBox.warning(self, "Debug", "No level loaded to dump.")
            return
            
        dump_path = os.path.join(os.path.dirname(__file__), "debug_dump.txt")
        try:
            with open(dump_path, "w") as f:
                f.write(f"Level: {self.current_level.level_name}\n")
                f.write(f"Texture Count: {len(self.current_level.textures)}\n")
                f.write("-" * 30 + "\n")
                for t in self.current_level.textures:
                    f.write(f"ID: {t['id']}, Offset: {hex(t['offset'])}, Size: {t['size']}, Pitch: {t['pitch']}, Depth: {t['bit_depth']}\n")
            
            QMessageBox.information(self, "Debug Dump", f"Debug information exported to:\n{dump_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export debug dump: {e}")

    def on_save(self):
        if not self.current_level: return
        
        reply = QMessageBox.question(
            self, "Save Level", 
            "Do you want to overwrite the original level file?", 
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
        )
        
        if reply == QMessageBox.Yes:
            self.perform_save()
        elif reply == QMessageBox.No:
            self.on_save_as()

    def on_save_as(self):
        if not self.current_level: return
        path, _ = QFileDialog.getSaveFileName(self, "Save Level As", self.current_level_path, "GFX Archive (*gfx.pc)")
        if path:
            # Re-importing into a NEW file path 
            # We must first copy the original to the new path because quickbms -r -w modifies in-place
            shutil.copy2(self.current_level_path, path)
            # Update the level object's archive path internally
            self.current_level.gfx_pc = path
            self.perform_save()

    def perform_save(self):
        self.statusBar().showMessage("Saving/Re-importing...")
        self.save_thread = QThread()
        self.worker = SaveWorker(self.current_level)
        self.worker.moveToThread(self.save_thread)
        self.save_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_save_finished)
        self.save_thread.start()

    @Slot(bool, str)
    def on_save_finished(self, success, error):
        self.save_thread.quit()
        if success:
            QMessageBox.information(self, "Success", "Level saved and re-imported successfully!")
            self.statusBar().showMessage("Save complete.")
        else:
            QMessageBox.critical(self, "Error", f"Save failed: {error}")
            self.statusBar().showMessage("Save failed.")

    def closeEvent(self, event):
        # Cleanup temp
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CFTXMainWindow()
    window.show()
    sys.exit(app.exec_())
