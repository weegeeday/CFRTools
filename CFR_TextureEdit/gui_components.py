from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QMenu,
    QListWidget, QListWidgetItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QPixmap, QImage, QAction
import os

class TextureTile(QFrame):
    clicked = Signal(int)
    doubleClicked = Signal(int)
    replaceRequested = Signal(int)
    exportRequested = Signal(int)

    def __init__(self, tex_id, pil_image, metadata, parent=None):
        super().__init__(parent)
        self.tex_id = tex_id
        self.setObjectName("textureTile")
        self.setFixedSize(180, 220)
        
        layout = QVBoxLayout(self)
        
        # Image Preview
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.set_image(pil_image)
        layout.addWidget(self.preview_label)
        
        # Info Labels
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        self.id_label = QLabel(f"Texture ID: {tex_id}")
        self.id_label.setObjectName("tileLabel")
        info_layout.addWidget(self.id_label)
        
        dim_text = f"{metadata['pitch']}x{pil_image.height} ({metadata['bit_depth']}b)"
        self.dim_label = QLabel(dim_text)
        self.dim_label.setObjectName("tileLabel")
        info_layout.addWidget(self.dim_label)
        
        layout.addLayout(info_layout)
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def set_image(self, pil_img):
        # Convert PIL to QImage/QPixmap
        if pil_img.mode != "RGBA":
            pil_img = pil_img.convert("RGBA")
        data = pil_img.tobytes("raw", "RGBA")
        qim = QImage(data, pil_img.width, pil_img.height, QImage.Format_RGBA8888)
        pix = QPixmap.fromImage(qim)
        scaled_pix = pix.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview_label.setPixmap(scaled_pix)

    def show_context_menu(self, pos):
        menu = QMenu(self)
        
        export_act = QAction("Export to PNG...", self)
        export_act.triggered.connect(lambda: self.exportRequested.emit(self.tex_id))
        
        replace_act = QAction("Replace Texture...", self)
        replace_act.triggered.connect(lambda: self.replaceRequested.emit(self.tex_id))
        
        menu.addAction(export_act)
        menu.addAction(replace_act)
        menu.exec_(self.mapToGlobal(pos))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.tex_id)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.doubleClicked.emit(self.tex_id)
        super().mouseDoubleClickEvent(event)

class FileSidebar(QListWidget):
    fileSelected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(250)
        self.itemClicked.connect(self.on_item_clicked)

    def add_file(self, file_path):
        name = os.path.basename(os.path.dirname(file_path))
        item = QListWidgetItem(name)
        item.setData(Qt.UserRole, file_path)
        item.setToolTip(file_path)
        self.addItem(item)
        return item

    def on_item_clicked(self, item):
        path = item.data(Qt.UserRole)
        self.fileSelected.emit(path)
