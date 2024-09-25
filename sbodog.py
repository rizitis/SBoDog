import sys
import subprocess
import os
import pexpect
import getpass
from PyQt5.QtWidgets import (
    QApplication, QMessageBox, QLabel, QVBoxLayout, QWidget, QSplitter, QPushButton,
    QMainWindow, QDialog, QTextEdit, QLineEdit, QGridLayout,
    QFileDialog, QSystemTrayIcon, QMenu, QAction
)
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal
def load_env_vars(filepath):
    with open(filepath) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value


# Load environment variables from the .env
load_env_vars('/etc/sbodog/sbodog.env') # Comment SLAKCBUILDS_REPO=SBo/15.0 to switch to ponce repo for current

class CommandThread(QThread):
    output_ready = pyqtSignal(str)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        process = subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        output = stdout.decode() + stderr.decode()
        self.output_ready.emit(output)

class OutputDialog(QDialog):
    def __init__(self, output):
        super().__init__()
        self.setWindowTitle("Command Output")
        self.setGeometry(200, 200, 600, 400)

        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlainText(output)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

class ImagePanel(QWidget):
    def __init__(self, image_path, directory, label_text):
        super().__init__()
        self.directory = directory
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.image_label = QLabel(self)
        self.load_image(image_path)

        self.name_label = QLabel(label_text, self)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("color: #A06DCC; font-size: 14px; padding: 5px;")
        self.name_label.setFont(QFont("Arial", 12, QFont.Bold))

        open_button = QPushButton("Open as Root")
        open_button.clicked.connect(self.on_click)

        layout.addWidget(self.image_label)
        layout.addWidget(self.name_label)
        layout.addWidget(open_button)  # Add the button to the layout
        self.setLayout(layout)

    def load_image(self, image_path):
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            print(f"Warning: Unable to load image at {image_path}")
            pixmap = QPixmap(80, 80)
            pixmap.fill(Qt.black)
        self.image_label.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio))
        self.image_label.setAlignment(Qt.AlignCenter)

    def on_click(self):
        command = f"xdg-open '{self.directory}'"
        try:
            subprocess.Popen(command, shell=True)
        except Exception as e:
            print(f"An error occurred: {e}")

    def load_image(self, image_path):
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            print(f"Warning: Unable to load image at {image_path}")
            pixmap = QPixmap(80, 80)
            pixmap.fill(Qt.black)
        self.image_label.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio))
        self.image_label.setAlignment(Qt.AlignCenter)

    def on_click(self):
        command = f"pkexec xdg-open '{self.directory}'"
        try:
            subprocess.Popen(command, shell=True)
        except Exception as e:
            print(f"An error occurred: {e}")  # Handle any errors

    def load_image(self, image_path):
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            print(f"Warning: Unable to load image at {image_path}")
            pixmap = QPixmap(80, 80)
            pixmap.fill(Qt.black)
        self.image_label.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio))
        self.image_label.setAlignment(Qt.AlignCenter)

    def on_click(self, event):
        subprocess.Popen(f"xdg-open {self.directory}", shell=True)

# I know ... but just leave it there. If it works dont touch it :D
import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QDialog, QTextEdit

class OutputDialog(QDialog):
    def __init__(self, output):
        super().__init__()
        self.setWindowTitle("Folder Contents")
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlainText(output)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

class CommandPanel(QWidget):
    def __init__(self, commands):
        super().__init__()

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Input field for the folder name at the top
        self.folder_name_entry = QLineEdit()
        self.folder_name_entry.setPlaceholderText("Type SlackBuild name to search...")
        layout.addWidget(self.folder_name_entry)

        # Button to search for the SlackBuild folder locally. TBH sbopkg -g <name> is better, but hey! terminal is always better than gui... :D
        search_button = QPushButton("Search Folder")
        search_button.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: #A06DCC;
                border: none;
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005f87;
            }
        """)
        search_button.clicked.connect(self.search_folder)
        layout.addWidget(search_button)

        # Input field for filtering commands
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("Type package name")
        self.setup_entry_style()
        layout.addWidget(self.entry)

        self.commands = commands
        self.button_layout = QVBoxLayout()
        self.button_layout.setSpacing(0)
        self.button_layout.setContentsMargins(0, 0, 0, 0)

        for label, command, show_popup in self.commands:
            self.create_command_button(label, command, show_popup)

        layout.addLayout(self.button_layout)
        self.setLayout(layout)
    # Set default SBo-git but real default is in .env This way we can easy updated 15.0 to 15.1 etc...current is always SBo-git ;)
    def search_folder(self):
        folder_name = self.folder_name_entry.text().strip()
        repo_name = os.getenv('SLAKCBUILDS_REPO', 'SBo-git')
        if repo_name != 'SBo-git':
            search_path = f"/var/lib/sbopkg/{repo_name}"
        else:
            search_path = "/var/lib/sbopkg/SBo-git"

        if not folder_name:
            print("No folder name entered.")
            return

        found = False
        try:
            # Recursively search for the SlackBuild folder
            for root, dirs, files in os.walk(search_path):
                if folder_name in dirs:
                    found = True
                    folder_path = os.path.join(root, folder_name)  # Full path to the found folder
                    contents = os.listdir(folder_path)  # List contents of the folder
                    parent_folder = os.path.relpath(root, search_path)  # Get the relative path of the parent
                    self.show_folder_contents(contents, parent_folder)  # Show contents in a popup
                    break

            if not found:
                print("Folder not found.")
                self.show_folder_contents([], "")  # Show empty if not found
        except Exception as e:
            print(f"An error occurred: {e}")

    def show_folder_contents(self, contents, parent_folder):
        if contents:
            content_output = f"Contents of '{parent_folder}/{self.folder_name_entry.text()}':\n" + "\n".join(contents)
        else:
            content_output = f"No contents found in '{parent_folder}/{self.folder_name_entry.text()}'."

        dialog = OutputDialog(content_output)
        dialog.exec_()

    def setup_entry_style(self):
        self.entry.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 14px;
                border: 2px solid #5A5A5A;
                border-radius: 5px;
                background-color: #2D2D2D;
                color: #E0E0E0;
            }
            QLineEdit:focus {
                border: 2px solid #A06DCC;
                background-color: #1E1E1E;
            }
        """)

    def create_command_button(self, label, command, show_popup):
        button = QPushButton(label)
        button.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: #A06DCC;
                border: none;
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005f87;
            }
        """)
        button.clicked.connect(lambda: self.run_command(command, show_popup))
        self.button_layout.addWidget(button)

    def run_command(self, command, show_popup):
        user_input = self.entry.text()
        command_with_input = command.format(input=user_input)

        terminal_command = f"konsole -e bash -c '{command_with_input}; exec bash'"  # Keep terminal open

        self.thread = CommandThread(terminal_command)
        self.thread.output_ready.connect(lambda output: self.show_output(output) if show_popup else self.show_message(output))
        self.thread.start()

    def show_output(self, output):
        dialog = OutputDialog(output)
        dialog.exec_()

    def show_message(self, output):
        print(output)

class NewSection(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        # Button to open the slpkg.toml file
        slpkg_button = QPushButton("Edit sbodog.env")
        slpkg_button.setStyleSheet("background-color: #333333; color: #A06DCC; padding: 10px;")
        slpkg_button.clicked.connect(lambda: self.open_file("/etc/sbodog/sbodog.env"))
        self.layout.addWidget(slpkg_button)

        # Button to open the repositories.toml file
        repos_button = QPushButton("Edit sbopkg.conf")
        repos_button.setStyleSheet("background-color: #333333; color: #A06DCC; padding: 10px;")
        repos_button.clicked.connect(lambda: self.open_file("/etc/sbopkg/sbopkg.conf"))
        self.layout.addWidget(repos_button)

        # button to open the /tmp/slpkg/build folder
        build_folder_button = QPushButton("Open /tmp/SBo")
        build_folder_button.setStyleSheet("background-color: #333333; color: #A06DCC; padding: 10px;")
        build_folder_button.clicked.connect(lambda: self.open_folder("/tmp/SBo"))
        self.layout.addWidget(build_folder_button)

        # Example image for visual consistency but keep it with this name, thanks GPT ;)
        example_image = QLabel()
        example_pixmap = QPixmap("/usr/share/pixmaps/sbodog/icons/sbodog.png")
        example_image.setPixmap(example_pixmap.scaled(100, 100, Qt.KeepAspectRatio))
        example_image.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(example_image)

        self.setLayout(self.layout)

    def open_file(self, file_path):
        try:
            subprocess.run(["xdg-open", file_path])  # This will open the file in the default editor
        except Exception as e:
            print(f"An error occurred: {e}")

    def open_folder(self, folder_path):
        try:
            subprocess.run(["xdg-open", folder_path])  # This will open the folder in the default file manager
        except Exception as e:
            print(f"An error occurred: {e}")


class AdditionalSection(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Define command templates
        self.commands = [
            ("Update SBo (sbopkg -r)", "sbopkg -r"),  # Command for Update
            ("SBo Queue Generator (sqg -a)", "sqg -a")   # Command for create queue for all SlackBuilds...
        ]

        # Create buttons based on command definitions
        for label, command_template in self.commands:
            button = QPushButton(label)
            button.setStyleSheet("background-color: #333333; color: #A06DCC; padding: 10px;")
            # Capture command_template correctly
            button.clicked.connect(lambda _, cmd=command_template: self.execute_command(cmd))
            layout.addWidget(button)

        # ICONS FROM https://www.freepik.com TODO:MENTION to README
        example_image = QLabel()
        example_pixmap = QPixmap("/usr/share/pixmaps/sbodog/icons/sbodog-1.png")
        example_image.setPixmap(example_pixmap.scaled(100, 100, Qt.KeepAspectRatio))
        example_image.setAlignment(Qt.AlignCenter)
        layout.addWidget(example_image)

        self.setLayout(layout)

    def execute_command(self, command):
        try:
            # Use konsole to run the command, change it with xfce4-terminal or xterm or whatever...
            subprocess.Popen(['konsole', '-e', 'bash', '-c', command])
        except Exception as e:
            print(f"An error occurred: {e}")  # Handle any errors

class MainWindow(QMainWindow):
    def __init__(self, images):
        super().__init__()

        # Setup window properties
        self.setGeometry(100, 100, 800, 800)
        self.setMinimumSize(400, 300)
        self.setWindowTitle("SBo Dog")

        # Setup the system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        tray_icon_path = '/usr/share/icons/hicolor/48x48/apps/sbodog.png'
        self.tray_icon.setIcon(QIcon(tray_icon_path))

        # Add a context menu for the tray icon
        tray_menu = QMenu()

        # Add a "Show" action
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)

        # Add a "Quit" action to exit the app from the tray
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)

        # Assign the menu to the tray icon and show it
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # code for the main window .
        splitter = QSplitter(Qt.Horizontal)

        # Left panel with images of sbo categories
        left_panel = QSplitter(Qt.Vertical)
        image_panel = QWidget()
        image_layout = QGridLayout()  # Change to QGridLayout
        num_columns = 4

        for idx, (image_path, directory, title) in enumerate(images):
            panel = ImagePanel(image_path, directory, title)
            row = idx // num_columns  # Determine the row
            column = idx % num_columns  # Determine the column
            image_layout.addWidget(panel, row, column)  # Add to grid layout

        image_panel.setLayout(image_layout)
        left_panel.addWidget(image_panel)

        additional_section = AdditionalSection()
        left_panel.addWidget(additional_section)

        right_panel = QSplitter(Qt.Vertical)

        commands = [
            ("Install", "sbopkg -i {input}", False),
            ("READ,Skip-Installed,Install", "sbopkg -Rki {input}", False),
            ("Read and Build (no install)", "sbopkg -Rb {input}", False),
            ("Read and Download (no build))", "sbopkg -Rd {input}", False),
            ("Read and Install", "sbopkg -Ri {input}", False),
            ("Creates package queuefile", "sqg -p {input}", False),
            ("List installed", "sbopkg -c", False),
            ("View SBo ChangeLog", "sbopkg -l", False),
            ("sbopkg help", "sbopkg -h", False),
        ]

        command_panel = CommandPanel(commands)
        right_panel.addWidget(command_panel)

        new_section = NewSection()
        right_panel.addWidget(new_section)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        self.setCentralWidget(splitter)
        self.setStyleSheet("background-color: #444444;")


def main():
    app = QApplication(sys.argv)

     # Set the global application icon
    app.setWindowIcon(QIcon('/usr/share/icons/hicolor/48x48/apps/sbodog.png'))


    # Get the environment variable
    repo_name = os.getenv('SLAKCBUILDS_REPO', 'SBo-git')

    # Define the base path for images
    base_path = f'/var/lib/sbopkg/{repo_name}'

    images = [
        (f'/usr/share/pixmaps/sbodog/icons/academic.png', f'{base_path}/academic', 'Academic'),
        (f'/usr/share/pixmaps/sbodog/icons/accessibility.png', f'{base_path}/accessibility', 'Accessibility'),
        (f'/usr/share/pixmaps/sbodog/icons/audio.png', f'{base_path}/audio', 'Audio'),
        (f'/usr/share/pixmaps/sbodog/icons/business.png', f'{base_path}/business', 'Business'),
        (f'/usr/share/pixmaps/sbodog/icons/desktop.png', f'{base_path}/desktop', 'Desktop'),
        (f'/usr/share/pixmaps/sbodog/icons/development.png', f'{base_path}/development', 'Development'),
        (f'/usr/share/pixmaps/sbodog/icons/games.png', f'{base_path}/games', 'Games'),
        (f'/usr/share/pixmaps/sbodog/icons/gis.png', f'{base_path}/gis', 'GIS'),
        (f'/usr/share/pixmaps/sbodog/icons/graphics.png', f'{base_path}/graphics', 'Graphics'),
        (f'/usr/share/pixmaps/sbodog/icons/ham.png', f'{base_path}/ham', 'Ham'),
        (f'/usr/share/pixmaps/sbodog/icons/haskell.png', f'{base_path}/haskell', 'Haskell'),
        (f'/usr/share/pixmaps/sbodog/icons/libraries.png', f'{base_path}/libraries', 'Libraries'),
        (f'/usr/share/pixmaps/sbodog/icons/misc.png', f'{base_path}/misc', 'Misc'),
        (f'/usr/share/pixmaps/sbodog/icons/mutlimedia.png', f'{base_path}/multimedia', 'Multimedia'),
        (f'/usr/share/pixmaps/sbodog/icons/network.png', f'{base_path}/network', 'Network'),
        (f'/usr/share/pixmaps/sbodog/icons/office.png', f'{base_path}/office', 'Office'),
        (f'/usr/share/pixmaps/sbodog/icons/perl.png', f'{base_path}/perl', 'Perl'),
        (f'/usr/share/pixmaps/sbodog/icons/python.png', f'{base_path}/python', 'Python'),
        (f'/usr/share/pixmaps/sbodog/icons/ruby.png', f'{base_path}/ruby', 'Ruby'),
        (f'/usr/share/pixmaps/sbodog/icons/system.png', f'{base_path}/system', 'System'),
    ]

    window = MainWindow(images)  # Create the main window
    window.show()  # Show the window
    sys.exit(app.exec_())  # Start the application loop

if __name__ == "__main__":
    main()
