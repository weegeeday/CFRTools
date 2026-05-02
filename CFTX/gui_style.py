
STYLE_SHEET = """
QMainWindow {
    background-color: #121212;
}

QWidget {
    color: #e0e0e0;
    font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    font-size: 14px;
}

QScrollBar:vertical {
    border: none;
    background: #1e1e1e;
    width: 10px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: #3a3a3a;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Sidebar */
QListWidget {
    background-color: #1e1e1e;
    border: none;
    border-right: 1px solid #333333;
    outline: none;
}
QListWidget::item {
    padding: 15px;
    border-bottom: 1px solid #2a2a2a;
}
QListWidget::item:selected {
    background-color: #3d3d3d;
    color: #ffffff;
    border-left: 4px solid #ff9800;
}
QListWidget::item:hover {
    background-color: #2a2a2a;
    color: #ffffff;
}

/* Button Group for Viewer */
#buttonGroupFrame {
    background-color: #2a2a2a;
    border-radius: 8px;
    padding: 2px;
}
#viewButton {
    background-color: transparent;
    border: none;
    padding: 8px 12px;
    font-size: 13px;
    border-radius: 6px;
}
#viewButton:checked {
    background-color: #3d3d3d;
    color: #ff9800;
}

/* Scroll Area */
QScrollArea {
    background-color: #121212;
    border: none;
}
#scrollContent {
    background-color: #121212;
}

/* Texture Tile */
#textureTile {
    background-color: #1e1e1e;
    border-radius: 8px;
    border: 1px solid #333333;
}
#textureTile:hover {
    border: 1px solid #ff9800;
}
#tileLabel {
    color: #aaaaaa;
    font-size: 12px;
}

/* Buttons */
QPushButton {
    background-color: #333333;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #444444;
}
QPushButton#primaryButton {
    background-color: #ff9800;
    color: #000000;
}
QPushButton#primaryButton:hover {
    background-color: #ffa726;
}

/* Dialogs */
QDialog {
    background-color: #1e1e1e;
}
QLineEdit, QComboBox {
    background-color: #2a2a2a;
    border: 1px solid #444444;
    padding: 5px;
    border-radius: 4px;
    color: white;
}
"""
