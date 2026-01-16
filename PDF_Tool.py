import sys
import os
import io
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLineEdit, QListWidget, QFileDialog, QLabel, 
                             QListWidgetItem, QFrame, QSplitter, QStatusBar)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage, QColor, QTransform
import fitz  # PyMuPDF
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image

# ==========================================
# THEME DEFINITIONS
# ==========================================
LIGHT_THEME = {
    "bg": "#f4f7f6",
    "panel": "#ffffff",
    "text": "#2c3e50",
    "input_bg": "#ffffff",
    "input_text": "#000000",
    "border": "#ced4da",
    "accent": "#3498db",
    "accent_hover": "#2980b9",
    "accent_pressed": "#1c638e",
    "success": "#27ae60",
    "success_hover": "#219150",
    "success_pressed": "#1a6f3e",
    "danger": "#e74c3c",
    "danger_hover": "#c0392b",
    "danger_pressed": "#962d22",
    "action": "#2c3e50",
    "action_hover": "#1a252f",
    "action_pressed": "#0d1318"
}

DARK_THEME = {
    "bg": "#121212",
    "panel": "#1e1e1e",
    "text": "#e0e0e0",
    "input_bg": "#2c2c2c",
    "input_text": "#ffffff",
    "border": "#333333",
    "accent": "#bb86fc",
    "accent_hover": "#9965f4",
    "accent_pressed": "#7c4dff",
    "success": "#03dac6",
    "success_hover": "#01b0a1",
    "success_pressed": "#008b7d",
    "danger": "#cf6679",
    "danger_hover": "#b04a5a",
    "danger_pressed": "#8c3846",
    "action": "#3d3d3d",
    "action_hover": "#505050",
    "action_pressed": "#252525"
}

class PDFTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Tool Pro")
        self.setMinimumSize(1200, 800)
        
        self.current_theme = LIGHT_THEME
        self.is_dark = False
        
        self.current_pdf_doc = None
        self.current_pdf_path = ""
        self.current_page_idx = 0
        self.current_rotation = 0 
        self.supported_imgs = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff")

        self.init_ui()
        self.update_styles()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 5, 10, 5)
        main_layout.setSpacing(5)

        # --- Top Bar ---
        top_bar = QFrame()
        top_bar.setMaximumHeight(60)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(5, 5, 5, 5)
        
        self.help_label = QLabel("i")
        self.help_label.setFixedSize(28, 28)
        self.help_label.setAlignment(Qt.AlignCenter)
        self.help_label.setToolTip("Drag & Drop Files | Rotate to fix orientation | Status bar shows progress")
        
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Root Folder Path...")
        self.path_input.setObjectName("InputBar")
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_folder)
        
        self.theme_btn = QPushButton("Dark Mode")
        self.theme_btn.clicked.connect(self.toggle_theme)
        
        top_layout.addWidget(self.help_label)
        top_layout.addWidget(self.path_input)
        top_layout.addWidget(browse_btn)
        top_layout.addWidget(self.theme_btn)
        main_layout.addWidget(top_bar)

        splitter = QSplitter(Qt.Horizontal)

        # 1. Source Panel
        left_widget = QFrame()
        left_vbox = QVBoxLayout(left_widget)
        self.pdf_list_widget = QListWidget()
        self.pdf_list_widget.itemClicked.connect(self.load_preview)
        left_vbox.addWidget(QLabel("SOURCE FILES"))
        left_vbox.addWidget(self.pdf_list_widget)
        splitter.addWidget(left_widget)

        # 2. Preview Panel
        mid_widget = QFrame()
        mid_vbox = QVBoxLayout(mid_widget)
        mid_vbox.setSpacing(8)
        
        self.preview_label = QLabel("Preview Area")
        self.preview_label.setAlignment(Qt.AlignCenter)
        
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("<")
        self.page_label = QLabel("Page 0/0")
        self.next_btn = QPushButton(">")
        rotate_btn = QPushButton("Rotate")
        
        self.prev_btn.clicked.connect(lambda: self.change_page(-1))
        self.next_btn.clicked.connect(lambda: self.change_page(1))
        rotate_btn.clicked.connect(self.rotate_preview)
        
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.page_label)
        nav_layout.addWidget(self.next_btn)
        nav_layout.addWidget(rotate_btn)

        self.page_range_input = QLineEdit()
        self.page_range_input.setPlaceholderText("Page Range (1, 3-5)")
        self.page_range_input.setObjectName("InputBar")
        
        add_btn = QPushButton("ADD TO BUILD")
        add_btn.setObjectName("ActionBtn")
        add_btn.clicked.connect(self.add_to_build)

        mid_vbox.addWidget(self.preview_label, 5)
        mid_vbox.addLayout(nav_layout)
        mid_vbox.addWidget(self.page_range_input)
        mid_vbox.addWidget(add_btn)
        splitter.addWidget(mid_widget)

        # 3. Build Panel
        right_widget = QFrame()
        right_vbox = QVBoxLayout(right_widget)
        self.build_list_widget = QListWidget()
        
        reorder_layout = QHBoxLayout()
        up_btn = QPushButton("Move Up")
        down_btn = QPushButton("Move Down")
        up_btn.clicked.connect(lambda: self.move_item(-1))
        down_btn.clicked.connect(lambda: self.move_item(1))
        reorder_layout.addWidget(up_btn)
        reorder_layout.addWidget(down_btn)

        build_ctrl = QHBoxLayout()
        remove_btn = QPushButton("Remove")
        clear_btn = QPushButton("Clear All")
        remove_btn.setObjectName("RemoveBtn")
        remove_btn.clicked.connect(self.remove_item)
        clear_btn.clicked.connect(self.clear_build)
        build_ctrl.addWidget(remove_btn)
        build_ctrl.addWidget(clear_btn)

        self.file_name_input = QLineEdit("Final_Project.pdf")
        self.file_name_input.setObjectName("InputBar")
        
        export_btn = QPushButton("EXPORT PDF")
        export_btn.setObjectName("ExportBtn")
        export_btn.clicked.connect(self.export_pdf)

        right_vbox.addWidget(QLabel("BUILD ORDER"))
        right_vbox.addWidget(self.build_list_widget)
        right_vbox.addLayout(reorder_layout)
        right_vbox.addLayout(build_ctrl)
        right_vbox.addWidget(self.file_name_input)
        right_vbox.addWidget(export_btn)
        splitter.addWidget(right_widget)

        main_layout.addWidget(splitter)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        self.setAcceptDrops(True)

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.current_theme = DARK_THEME if self.is_dark else LIGHT_THEME
        self.theme_btn.setText("Light Mode" if self.is_dark else "Dark Mode")
        self.update_styles()

    def update_styles(self):
        t = self.current_theme
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {t['bg']}; }}
            QFrame {{ border: 1px solid {t['border']}; border-radius: 4px; background: {t['panel']}; padding: 5px; }}
            QLabel {{ border: none; font-weight: 700; color: {t['text']}; letter-spacing: 0.5px; }}
            
            /* Standard Buttons */
            QPushButton {{ 
                background: {t['accent']}; 
                color: #ffffff; 
                padding: 8px; 
                border-radius: 4px; 
                font-weight: bold; 
                border: none; 
            }}
            QPushButton:hover {{ background: {t['accent_hover']}; }}
            QPushButton:pressed {{ background: {t['accent_pressed']}; }}
            
            /* Add to Build Button */
            QPushButton#ActionBtn {{ background: {t['action']}; color: {t['panel']}; }}
            QPushButton#ActionBtn:hover {{ background: {t['action_hover']}; }}
            QPushButton#ActionBtn:pressed {{ background: {t['action_pressed']}; }}

            /* Export Button */
            QPushButton#ExportBtn {{ background: {t['success']}; color: #ffffff; }}
            QPushButton#ExportBtn:hover {{ background: {t['success_hover']}; }}
            QPushButton#ExportBtn:pressed {{ background: {t['success_pressed']}; }}
            
            /* Remove Button */
            QPushButton#RemoveBtn {{ background: {t['danger']}; color: #ffffff; }}
            QPushButton#RemoveBtn:hover {{ background: {t['danger_hover']}; }}
            QPushButton#RemoveBtn:pressed {{ background: {t['danger_pressed']}; }}
            
            QLineEdit#InputBar {{ 
                padding: 8px; 
                border: 1px solid {t['border']}; 
                border-radius: 4px; 
                background-color: {t['input_bg']}; 
                color: {t['input_text']}; 
            }}
            
            QListWidget {{ 
                border: 1px solid {t['border']}; 
                background: {t['panel']}; 
                color: {t['text']}; 
                outline: none;
            }}
            QListWidget::item {{ padding: 6px; border-bottom: 1px solid {t['border']}; }}
            QListWidget::item:selected {{ background: {t['accent']}; color: #ffffff; }}
            
            QStatusBar {{ color: {t['text']}; background: {t['bg']}; border-top: 1px solid {t['border']}; }}
        """)
        self.help_label.setStyleSheet(f"background: {t['accent']}; color: #ffffff; border-radius: 14px; font-weight: bold;")

    def rotate_preview(self):
        self.current_rotation = (self.current_rotation + 90) % 360
        if self.current_pdf_doc: self.show_page(self.current_page_idx)
        elif self.current_pdf_path.lower().endswith(self.supported_imgs): self.load_preview_image(self.current_pdf_path)

    def move_item(self, direction):
        curr_row = self.build_list_widget.currentRow()
        if curr_row == -1: return
        new_row = curr_row + direction
        if 0 <= new_row < self.build_list_widget.count():
            item = self.build_list_widget.takeItem(curr_row)
            self.build_list_widget.insertItem(new_row, item)
            self.build_list_widget.setCurrentRow(new_row)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.path_input.setText(folder)
            self.pdf_list_widget.clear()
            for f in os.listdir(folder):
                if f.lower().endswith((".pdf",) + self.supported_imgs):
                    path = os.path.join(folder, f)
                    it = QListWidgetItem(f"FILE: {f}")
                    it.setData(Qt.UserRole, path)
                    self.pdf_list_widget.addItem(it)

    def load_preview(self, item):
        path = item.data(Qt.UserRole)
        self.current_pdf_path, self.current_rotation = path, 0 
        if path.lower().endswith(self.supported_imgs):
            self.load_preview_image(path)
            self.current_pdf_doc = None 
        else:
            self.current_pdf_doc = fitz.open(path)
            self.current_page_idx = 0
            self.show_page(0)

    def load_preview_image(self, path):
        pixmap = QPixmap(path)
        if self.current_rotation != 0:
            pixmap = pixmap.transformed(QTransform().rotate(self.current_rotation))
        self.preview_label.setPixmap(pixmap.scaled(self.preview_label.width()-20, self.preview_label.height()-20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.page_label.setText("Image 1/1")

    def show_page(self, idx):
        if not self.current_pdf_doc: return
        page = self.current_pdf_doc.load_page(idx)
        pix = page.get_pixmap(matrix=fitz.Matrix(self.current_rotation))
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
        self.preview_label.setPixmap(QPixmap.fromImage(img).scaled(self.preview_label.width()-20, self.preview_label.height()-20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.page_label.setText(f"Page {idx + 1}/{self.current_pdf_doc.page_count}")

    def change_page(self, d):
        if not self.current_pdf_doc: return
        new = self.current_page_idx + d
        if 0 <= new < self.current_pdf_doc.page_count:
            self.current_page_idx = new
            self.show_page(new)

    def add_to_build(self):
        if not self.current_pdf_path: return
        r = self.page_range_input.text().replace(" ", "") or "All"
        item = QListWidgetItem(f"{os.path.basename(self.current_pdf_path)} | Pgs: {r} | Rot: {self.current_rotation}")
        item.setData(Qt.UserRole, (self.current_pdf_path, r, self.current_rotation))
        self.build_list_widget.addItem(item)
        self.status_bar.showMessage("Added to queue", 2000)

    def remove_item(self):
        for it in self.build_list_widget.selectedItems(): self.build_list_widget.takeItem(self.build_list_widget.row(it))

    def clear_build(self): self.build_list_widget.clear()

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls(): e.accept()
        else: e.ignore()

    def dropEvent(self, e):
        for url in e.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith((".pdf",) + self.supported_imgs):
                it = QListWidgetItem(f"FILE: {os.path.basename(path)}")
                it.setData(Qt.UserRole, path)
                self.pdf_list_widget.addItem(it)

    def export_pdf(self):
        if self.build_list_widget.count() == 0: return
        save_path, _ = QFileDialog.getSaveFileName(self, "Export PDF", self.file_name_input.text(), "*.pdf")
        if not save_path: return
        self.status_bar.showMessage("Building PDF...")
        QApplication.processEvents()
        writer = PdfWriter()
        try:
            for i in range(self.build_list_widget.count()):
                path, rng, rot = self.build_list_widget.item(i).data(Qt.UserRole)
                if path.lower().endswith(self.supported_imgs):
                    img = Image.open(path).convert("RGB")
                    if rot != 0: img = img.rotate(-rot, expand=True)
                    buf = io.BytesIO()
                    img.save(buf, format="PDF")
                    buf.seek(0)
                    writer.add_page(PdfReader(buf).pages[0])
                else:
                    reader = PdfReader(path)
                    pgs = reader.pages if rng == "All" else []
                    if rng != "All":
                        for part in rng.split(','):
                            if '-' in part:
                                s, e = map(int, part.split('-'))
                                for n in range(s-1, e): pgs.append(reader.pages[n])
                            else: pgs.append(reader.pages[int(part)-1])
                    for p in pgs:
                        if rot != 0: p.rotate(rot)
                        writer.add_page(p)
            with open(save_path, "wb") as f: writer.write(f)
            self.status_bar.showMessage("Export complete", 5000)
        except Exception as e: self.status_bar.showMessage(f"Error: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFTool()
    window.show()
    sys.exit(app.exec_())