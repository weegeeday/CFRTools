from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QFileDialog, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QImage
from PIL import Image, ImageOps
import os

class ReplaceDialog(QDialog):
    def __init__(self, original_pil, target_w, target_h, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Replace Texture")
        self.setMinimumSize(800, 500)
        
        self.original_pil = original_pil
        self.target_w = target_w
        self.target_h = target_h
        self.new_pil = None
        self.final_pil = None
        
        layout = QVBoxLayout(self)
        
        # Comparison Area
        comp_layout = QHBoxLayout()
        comp_layout.setSpacing(20)
        
        # Left: Original
        orig_v = QVBoxLayout()
        orig_v.addWidget(QLabel("Original"))
        self.orig_preview = QLabel()
        self.orig_preview.setFixedSize(300, 300)
        self.orig_preview.setStyleSheet("border: 1px solid #444;")
        self.set_label_image(self.orig_preview, original_pil)
        orig_v.addWidget(self.orig_preview)
        comp_layout.addLayout(orig_v)
        
        # Right: New Preview (Live with settings)
        new_v = QVBoxLayout()
        new_v.addWidget(QLabel("Modified Preview"))
        self.new_preview = QLabel()
        self.new_preview.setFixedSize(300, 300)
        self.new_preview.setStyleSheet("border: 1px solid #444; background: #000;")
        new_v.addWidget(self.new_preview)
        comp_layout.addLayout(new_v)
        
        layout.addLayout(comp_layout)
        
        # Settings
        settings_layout = QHBoxLayout()
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Stretch", "Fit (Aspect)", "Center"])
        self.mode_combo.currentIndexChanged.connect(self.update_preview)
        settings_layout.addWidget(QLabel("Resizing:"))
        settings_layout.addWidget(self.mode_combo)
        
        self.select_btn = QPushButton("Select Image...")
        self.select_btn.setObjectName("primaryButton")
        self.select_btn.clicked.connect(self.on_select_image)
        settings_layout.addWidget(self.select_btn)
        
        layout.addLayout(settings_layout)
        
        # Bottom Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.apply_btn = QPushButton("Apply (Temp)")
        self.apply_btn.setEnabled(False)
        self.apply_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(self.apply_btn)
        layout.addLayout(btn_layout)

    def set_label_image(self, label, pil_img):
        if not pil_img: return
        tmp = pil_img.copy()
        if tmp.mode != "RGBA": tmp = tmp.convert("RGBA")
        data = tmp.tobytes("raw", "RGBA")
        qim = QImage(data, tmp.width, tmp.height, QImage.Format_RGBA8888)
        pix = QPixmap.fromImage(qim)
        label.setPixmap(pix.scaled(label.width(), label.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def on_select_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Replacement Image", "", "Images (*.png *.jpg *.bmp *.tga)")
        if path:
            self.new_pil = Image.open(path)
            self.update_preview()
            self.apply_btn.setEnabled(True)

    def update_preview(self):
        if not self.new_pil: return
        
        mode = self.mode_combo.currentText()
        w, h = self.target_w, self.target_h
        
        if mode == "Stretch":
            self.final_pil = self.new_pil.resize((w, h), Image.Resampling.LANCZOS)
        elif mode == "Fit (Aspect)":
            self.final_pil = ImageOps.pad(self.new_pil, (w, h), color=(0,0,0,0), centering=(0.5, 0.5))
        else: # Center/Crop
            self.final_pil = ImageOps.fit(self.new_pil, (w, h), centering=(0.5, 0.5))
            
        self.set_label_image(self.new_preview, self.final_pil)

    def get_result(self):
        return self.final_pil, self.mode_combo.currentText().lower().split(' ')[0]

class HelpDialog(QDialog):
    debugDumpRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About CFTX")
        self.setFixedWidth(400)
        
        # Adjustable variables
        self.github_url = "https://github.com/Weegeeday/CrazyFrogToolkit"
        self.version = "1.1.0"
        self.tool_name = "Crazy Frog Texture Tool (CFTX)"
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        title = QLabel(self.tool_name)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ff9800;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        info = QLabel(f"Version: {self.version}\n\nDeveloper: Weegeeday\nLink: {self.github_url}")
        info.setOpenExternalLinks(True)
        info.setTextInteractionFlags(Qt.TextBrowserInteraction)
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        
        layout.addSpacing(10)
        
        self.debug_btn = QPushButton("🐞 Export Debug Dump")
        self.debug_btn.clicked.connect(self.debugDumpRequested.emit)
        layout.addWidget(self.debug_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

class ImageViewerDialog(QDialog):
    def __init__(self, pil_img, title="Texture Viewer", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(800, 700)
        self.original_pil = pil_img.convert("RGBA") if pil_img.mode != "RGBA" else pil_img
        
        layout = QVBoxLayout(self)
        
        # Header with Channel Selection
        header = QHBoxLayout()
        header.addWidget(QLabel("View Channel:"))
        
        btn_frame = QFrame()
        btn_frame.setObjectName("buttonGroupFrame")
        self.button_group = QHBoxLayout(btn_frame)
        self.button_group.setContentsMargins(2, 2, 2, 2)
        self.button_group.setSpacing(2)
        
        self.channels = ["RGBA", "Red", "Green", "Blue", "Alpha"]
        self.btns = []
        for i, name in enumerate(self.channels):
            btn = QPushButton(name)
            btn.setObjectName("viewButton")
            btn.setCheckable(True)
            if i == 0: btn.setChecked(True)
            btn.clicked.connect(lambda _, n=name: self.show_channel(n))
            self.button_group.addWidget(btn)
            self.btns.append(btn)
            
        header.addWidget(btn_frame)
        header.addStretch()
        layout.addLayout(header)
        
        # Image Display Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background-color: #000; border: 1px solid #333;")
        
        self.img_label = QLabel()
        self.img_label.setAlignment(Qt.AlignCenter)
        self.scroll.setWidget(self.img_label)
        layout.addWidget(self.scroll)
        
        self.show_channel("RGBA")

    def show_channel(self, name):
        # Update button states
        for btn in self.btns:
            btn.setChecked(btn.text() == name)
            
        pil = self.original_pil
        if name == "RGBA":
            display_pil = pil
        else:
            r, g, b, a = pil.split()
            mapping = {"Red": r, "Green": g, "Blue": b, "Alpha": a}
            display_pil = mapping[name]
            # Convert single channel to grayscale L for display
            display_pil = display_pil.convert("L")
            
        self.set_display_image(display_pil)

    def set_display_image(self, pil_img):
        # Scale for fit but allow original size
        tmp = pil_img.copy()
        if tmp.mode == "L":
            data = tmp.tobytes("raw", "L")
            qim = QImage(data, tmp.width, tmp.height, QImage.Format_Grayscale8)
        else:
            if tmp.mode != "RGBA": tmp = tmp.convert("RGBA")
            data = tmp.tobytes("raw", "RGBA")
            qim = QImage(data, tmp.width, tmp.height, QImage.Format_RGBA8888)
            
        pix = QPixmap.fromImage(qim)
        # Scaled to a reasonable viewing size but keeping detail
        max_size = 2048
        if pix.width() > max_size or pix.height() > max_size:
            pix = pix.scaled(max_size, max_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
        self.img_label.setPixmap(pix)
