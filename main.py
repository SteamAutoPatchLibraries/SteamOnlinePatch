import os
import sys
import requests
import zipfile
import rarfile
import py7zr
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QComboBox, QLineEdit, QVBoxLayout, QWidget, QFileDialog, QMessageBox, QProgressBar
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QSize, QUrl
from PyQt6.QtGui import QFont, QIcon, QPixmap, QDesktopServices
REPO_URL = 'https://github.com/'
API_URL = 'https://api.github.com/repos/'
GITHUB_TOKEN = ''

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    return os.path.join(base_path, relative_path)
    except Exception:
        base_path = os.path.abspath('.')

class DownloadWorker(QThread):
    progress = pyqtSignal(str)

    def __init__(self, folder_path, save_dir):
        super().__init__()
        self.folder_path = folder_path
        self.save_dir = save_dir

    def run(self):
        try:
            headers = {'User-Agent': 'Mozilla/5.0', 'Authorization': f'token {GITHUB_TOKEN}'}
            self.download_folder(f'{API_URL}/{self.folder_path}', self.save_dir)

    def download_folder(self, folder_url, save_dir):
        headers = {'User-Agent': 'Mozilla/5.0', 'Authorization': f'token {GITHUB_TOKEN}'}
        response = requests.get(folder_url, headers=headers)
        response.raise_for_status()
        items = response.json()
        for item in items:
            item_name = item['name']
            item_type = item['type']
            item_path = os.path.join(save_dir, item_name)
            if item_type == 'file':
                self.download_file(item['download_url'], save_dir)
            else: 
                if item_type == 'dir':
                    pass
                else:
                    os.makedirs(item_path, exist_ok=True)
                    self.download_folder(item['url'], item_path)
        self.extract_rar_files(save_dir)

    def download_file(self, url, save_dir):
        try:
            headers = {'User-Agent': 'Mozilla/5.0', 'Authorization': f'token {GITHUB_TOKEN}'}
            self.progress.emit(f'⏳ Downloading file: {os.path.basename(url)}')
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()
            filename = os.path.basename(url)
            save_path = os.path.join(save_dir, filename)
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=16384):
                    if chunk:
                        pass
                    else:
                        file.write(chunk)
        except Exception as e:

    def extract_rar_files(self, directory):
        for root, _, files in os.walk(directory):
            rar_files = [f for f in files if f.lower().endswith('.rar')]
            for rar_file in rar_files:
                rar_path = os.path.join(root, rar_file)
                try:
                    with rarfile.RarFile(rar_path, 'r') as rar_ref:
                        rar_ref.extractall(root)
                            os.remove(rar_path)
                            folder_name = os.path.splitext(rar_file)[0]
                            folder_path = os.path.join(root, folder_name)
                            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                                for item in os.listdir(folder_path):
                                    src = os.path.join(folder_path, item)
                                    dst = os.path.join(root, item)
                                    if os.path.exists(dst):
                                        if os.path.isdir(dst):
                                            for sub_item in os.listdir(src):
                                                sub_src = os.path.join(src, sub_item)
                                                sub_dst = os.path.join(dst, sub_item)
                                                os.rename(sub_src, sub_dst)
                                        else:
                                            os.remove(dst)
                                            os.rename(src, dst)
                                    else:
                                        os.rename(src, dst)
                                os.rmdir(folder_path)

    def handle_subfolder_after_extraction(self, extract_to, parent_dir):
        try:
            items = os.listdir(extract_to)
            if len(items) == 1 and os.path.isdir(os.path.join(extract_to, items[0])):
                subfolder_path = os.path.join(extract_to, items[0])
                subfolder_items = os.listdir(subfolder_path)
                for item in subfolder_items:
                    src_path = os.path.join(subfolder_path, item)
                    dst_path = os.path.join(parent_dir, item)
                    os.rename(src_path, dst_path)
                os.rmdir(subfolder_path)
                return


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Steam Online Patch')
        self.setFixedSize(500, 750)
        self.setStyleSheet('\n        background-color: #2E2E2E;\n        color: white;\n        font-family: \'Segoe UI\', sans-serif;\n        ')
        app.setWindowIcon(QIcon(resource_path('icons_new/logo_2.0.png')))
        self.all_game_names = []
        self.init_ui()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label = QLabel(self)
        logo_pixmap = QPixmap(resource_path('icons_new/logo_2.0.png')).scaled(175, 175, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(logo_label)
        title_label = QLabel('Steam Online Patch', self)
        title_label.setFont(QFont('Segoe UI', 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet('color: #4CAF50; margin-bottom: 20px;')
        self.layout.addWidget(title_label)
        subtitle_note = QLabel('The game patch are not guaranteed to work. \nMost of the time it is updated to work with specific \ngame version or latest game version', self)
        subtitle_note.setFont(QFont('Segoe UI', 12))
        subtitle_note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_note.setStyleSheet('margin-bottom: 10px;')
        subtitle_label = QLabel('Select or Search for a Game to Patch:', self)
        subtitle_label.setFont(QFont('Segoe UI', 14))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet('margin-bottom: 10px; font-weight: bold;')
        self.layout.addWidget(subtitle_label)
        self.layout.addWidget(subtitle_note)
        self.search_bar = QLineEdit(self)
        self.search_bar.setFont(QFont('Segoe UI', 12))
        self.search_bar.setPlaceholderText('Search for a game...')
        self.search_bar.setStyleSheet('\n        QLineEdit {\n        background-color: #444;\n        color: white;\n        border: 1px solid #555;\n        border-radius: 5px;\n        padding: 5px;\n        }\n        ')
        self.search_bar.textChanged.connect(self.filter_games)
        self.layout.addWidget(self.search_bar)
        self.game_choice = QComboBox(self)
        self.game_choice.setFont(QFont('Segoe UI', 12))
        self.game_choice.setStyleSheet('\n        QComboBox {\n        background-color: #444;\n        color: white;\n        border: 1px solid #555;\n        border-radius: 5px;\n        padding: 5px;\n        }\n        QComboBox::drop-down {\n        border: none;\n        }\n        ')
        self.update_game_options()
        self.layout.addWidget(self.game_choice)
        directory_label = QLabel('Select Game Directory:', self)
        directory_label.setFont(QFont('Segoe UI', 12))
        directory_label.setStyleSheet('margin-top: 20px;')
        self.layout.addWidget(directory_label)
        self.directory_entry = QLineEdit(self)
        self.directory_entry.setFont(QFont('Segoe UI', 12))
        self.directory_entry.setReadOnly(True)
        self.directory_entry.setStyleSheet('\n        QLineEdit {\n        background-color: #444;\n        color: white;\n        border: 1px solid #555;\n        border-radius: 5px;\n        padding: 5px;\n        }\n        ')
        self.layout.addWidget(self.directory_entry)
        browse_button = QPushButton(' Browse ', self)
        browse_button.setFont(QFont('Segoe UI', 12))
        browse_button.setIcon(QIcon(resource_path('green download.png')))
        browse_button.setIconSize(QSize(32, 32))
        browse_button.setStyleSheet('\n        QPushButton {\n        background-color: #4CAF50;\n        color: white;\n        border: none;\n        border-radius: 5px;\n        padding: 10px;\n        }\n        QPushButton:hover {\n        background-color: #45A049;\n        }\n        ')
        browse_button.clicked.connect(self.browse_folder)
        self.layout.addWidget(browse_button)
        start_button = QPushButton('Start Patching', self)
        start_button.setFont(QFont('Segoe UI', 12))
        start_button.setStyleSheet('\n        QPushButton {\n        background-color: #FF9800;\n        color: white;\n        border: none;\n        border-radius: 5px;\n        padding: 10px;\n        }\n        QPushButton:hover {\n        background-color: #E68A00;\n        }\n        ')
        start_button.clicked.connect(self.start_download)
        self.layout.addWidget(start_button)
        self.status_label = QLabel('Select a game and directory to start.', self)
        self.status_label.setFont(QFont('Segoe UI', 12))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet('margin-top: 20px;')
        self.layout.addWidget(self.status_label)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet('\n        QProgressBar {\n        background-color: #444;\n        border: 1px solid #555;\n        border-radius: 5px;\n        height: 10px;\n        }\n        QProgressBar::chunk {\n        background-color: #4CAF50;\n        border-radius: 5px;\n        }\n        ')
        self.layout.addWidget(self.progress_bar)

    def update_game_options(self):
        try:
            headers = {'User-Agent': 'Mozilla/5.0', 'Authorization': f'token {GITHUB_TOKEN}'}
            response = requests.get(API_URL, headers=headers)
            response.raise_for_status()
            files = response.json()
            self.all_game_names = [file['name'] for file in files if file['type'] == 'dir']
                self.game_choice.addItems(self.all_game_names)

    def filter_games(self):
        search_text = self.search_bar.text().lower()
        filtered_games = [game for game in self.all_game_names if search_text in game.lower()]
        self.game_choice.clear()
        self.game_choice.addItems(filtered_games)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Directory')
        if folder:
            self.directory_entry.setText(folder)
        return None

    def start_download(self):
        selected_folder = self.game_choice.currentText()
        save_dir = self.directory_entry.text()
        if not save_dir or not os.path.isdir(save_dir):
            QMessageBox.warning(self, 'Error', 'Please select a valid directory on C: or D: drive.')
        return None

    def update_status(self, message):
        self.status_label.setText(message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('icons_new/icon.png'))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
