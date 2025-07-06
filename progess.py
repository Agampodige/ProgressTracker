import sys
import time
import math
import uuid
import json
import os
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QProgressBar,
    QMessageBox, QFrame, QListWidget, QListWidgetItem,
    QSpacerItem, QSizePolicy, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer, QPoint, QStandardPaths
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QDoubleValidator

# Define the name of the data file
DATA_FILE_NAME = "projects.json"

@dataclass
class Project:
    """Dataclass to hold all relevant information for a single project."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "New Project"
    total_units: float = 100.0
    current_units: float = 0.0
    start_time: Optional[float] = None  # Unix timestamp when timer started
    is_running: bool = False
    # Store elapsed time at pause to correctly resume timer
    elapsed_at_pause: float = 0.0
    description: str = "" # New field for project description

class ModernProgressBarApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Multi-Project Progress & ETC Estimator")
        self.setMinimumSize(850, 600) # Set a minimum size instead
        self.setWindowIcon(QIcon("app_icon.ico"))
        # --- Use standard window flags for OS-drawn frame and controls ---
        self.setWindowFlags(Qt.WindowType.Window) # This enables the default title bar and resizing

        self.projects: Dict[str, Project] = {}
        self.current_project_id: Optional[str] = None

        self.etc_timer = QTimer(self) # PyQt's timer
        self.etc_timer.setInterval(100) # Update every 100 milliseconds
        self.etc_timer.timeout.connect(self.update_all_etcs) # Connect timeout signal to update_etc

        self.init_ui()
        self.apply_styles() # Apply QSS for modern look

        # Load projects from file
        self.load_projects()

        # Add an initial project if none exist after loading
        if not self.projects:
            self.add_new_project()
        else:
            # Select the first project if projects were loaded
            if self.project_list_widget.count() > 0:
                self.project_list_widget.setCurrentRow(0)

        # Removed custom dragging logic as OS handles it now

    def get_data_file_path(self):
        """Returns the full path to the data file."""
        # Use QStandardPaths for cross-platform application data directory
        data_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        if not data_dir: # Fallback if AppDataLocation is not available (e.g., some Linux setups)
            data_dir = os.path.join(os.path.expanduser("~"), ".pyqt_progress_app")
        
        os.makedirs(data_dir, exist_ok=True) # Ensure the directory exists
        return os.path.join(data_dir, DATA_FILE_NAME)

    def load_projects(self):
        """Loads project data from the JSON file."""
        file_path = self.get_data_file_path()
        if not os.path.exists(file_path):
            print(f"No data file found at {file_path}. Starting with no projects.")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
                for project_data in raw_data:
                    # Convert dict back to Project dataclass instance
                    # Ensure all fields are present, provide defaults if necessary
                    project = Project(
                        id=project_data.get('id', str(uuid.uuid4())),
                        name=project_data.get('name', 'Unnamed Project'),
                        total_units=project_data.get('total_units', 100.0),
                        current_units=project_data.get('current_units', 0.0),
                        start_time=project_data.get('start_time'),
                        is_running=project_data.get('is_running', False),
                        elapsed_at_pause=project_data.get('elapsed_at_pause', 0.0),
                        description=project_data.get('description', '') # Load new description field
                    )
                    self.projects[project.id] = project
                    
                    item = QListWidgetItem(project.name)
                    item.setData(Qt.ItemDataRole.UserRole, project.id)
                    self.project_list_widget.addItem(item)
            print(f"Projects loaded from {file_path}")

        except json.JSONDecodeError:
            QMessageBox.warning(self, "Load Error", f"Could not decode project data from {DATA_FILE_NAME}. File might be corrupted.")
            print(f"Error decoding JSON from {file_path}")
            self.projects = {} # Clear existing projects to prevent bad data
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"An unexpected error occurred while loading projects: {e}")
            print(f"Unexpected error loading projects: {e}")
            self.projects = {}

    def save_projects(self):
        """Saves current project data to the JSON file."""
        file_path = self.get_data_file_path()
        
        # Convert Project objects to dictionaries for JSON serialization
        projects_to_save = [asdict(project) for project in self.projects.values()]

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(projects_to_save, f, indent=4) # Use indent for readability
            print(f"Projects saved to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"An error occurred while saving projects: {e}")
            print(f"Error saving projects to {file_path}: {e}")

    def closeEvent(self, event):
        """Overrides the close event to save projects before closing."""
        self.save_projects()
        event.accept() # Accept the close event

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(0, 0, 0, 0) # No margins for the main layout to allow Card to fill

        # Card-like frame for the main content
        card_frame = QFrame(self)
        card_frame.setObjectName("cardFrame") # Used for QSS styling
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(30, 30, 30, 30) # Padding inside the card
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Removed custom title bar layout and its buttons/label
        # The window's title and controls are now handled by the OS

        # --- Main Content Area: Project List (Left) and Details (Right) ---
        content_layout = QHBoxLayout()

        # Left Side: Project List and Management Buttons
        project_list_frame = QFrame(self)
        project_list_frame.setObjectName("projectListFrame")
        project_list_layout = QVBoxLayout(project_list_frame)
        project_list_layout.setContentsMargins(15, 15, 15, 15) # Increased padding

        project_list_layout.addWidget(QLabel("<b>Projects</b>"))
        project_list_layout.addSpacing(10) # Space below title

        self.project_list_widget = QListWidget(self)
        self.project_list_widget.setMinimumWidth(200)
        self.project_list_widget.setMaximumWidth(250)
        self.project_list_widget.currentItemChanged.connect(self.select_project_from_list)
        project_list_layout.addWidget(self.project_list_widget)
        project_list_layout.addSpacing(15) # Space before buttons

        project_buttons_layout = QHBoxLayout()
        self.add_project_button = QPushButton("Add Project")
        self.add_project_button.setIcon(QIcon.fromTheme("list-add"))
        self.add_project_button.clicked.connect(self.add_new_project)
        project_buttons_layout.addWidget(self.add_project_button)

        self.delete_project_button = QPushButton("Delete Project")
        self.delete_project_button.setIcon(QIcon.fromTheme("list-remove"))
        self.delete_project_button.clicked.connect(self.delete_selected_project)
        project_buttons_layout.addWidget(self.delete_project_button)
        project_list_layout.addLayout(project_buttons_layout)

        content_layout.addWidget(project_list_frame)
        content_layout.addSpacing(25) # Increased spacing between panels

        # Right Side: Project Details and Progress Display
        project_details_frame = QFrame(self)
        project_details_frame.setObjectName("projectDetailsFrame")
        self.project_details_layout = QVBoxLayout(project_details_frame)
        self.project_details_layout.setContentsMargins(20, 20, 20, 20) # Increased padding inside details frame

        self.project_details_layout.addWidget(QLabel("<b>Project Details</b>"))
        self.project_details_layout.addSpacing(15) # Increased spacing

        # Project Name
        name_layout = QHBoxLayout()
        name_label = QLabel("Project Name:")
        name_label.setFixedWidth(120) # Align labels
        name_layout.addWidget(name_label)
        self.project_name_input = QLineEdit()
        self.project_name_input.textChanged.connect(self._on_project_name_changed)
        name_layout.addWidget(self.project_name_input)
        self.project_details_layout.addLayout(name_layout)

        self.project_details_layout.addSpacing(10)

        # Project Description
        description_label = QLabel("Project Description:")
        description_label.setFixedWidth(120) # Align labels
        self.project_details_layout.addWidget(description_label) # Add label directly
        self.project_details_layout.addSpacing(5) # Small space between label and text edit

        self.project_description_input = QTextEdit()
        self.project_description_input.setPlaceholderText("Enter project description here...")
        self.project_description_input.setMinimumHeight(80) # Give it more space
        self.project_description_input.textChanged.connect(self._on_project_description_changed)
        self.project_details_layout.addWidget(self.project_description_input)

        self.project_details_layout.addSpacing(15)


        # Total Work Units
        total_layout = QHBoxLayout()
        total_label = QLabel("Total Work Units:")
        total_label.setFixedWidth(120) # Align labels
        total_layout.addWidget(total_label)
        self.total_value_input = QLineEdit("100.0")
        self.total_value_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.total_value_input.setFixedWidth(150)
        self.total_value_input.setValidator(QDoubleValidator(0.0, 1000000.0, 1))
        self.total_value_input.textChanged.connect(self._update_display_from_inputs)
        self.total_value_input.editingFinished.connect(lambda: self._finalize_input_editing(self.total_value_input, "total_units", "Total Work Units", is_total=True))
        total_layout.addWidget(self.total_value_input)
        self.project_details_layout.addLayout(total_layout)

        self.project_details_layout.addSpacing(10)

        # Current Work Units
        current_layout = QHBoxLayout()
        current_label = QLabel("Current Work Units:")
        current_label.setFixedWidth(120) # Align labels
        current_layout.addWidget(current_label)
        self.current_value_input = QLineEdit("0.0")
        self.current_value_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_value_input.setFixedWidth(150)
        self.current_value_input.setValidator(QDoubleValidator(0.0, 1000000.0, 1))
        self.current_value_input.textChanged.connect(self._update_display_from_inputs)
        self.current_value_input.editingFinished.connect(lambda: self._finalize_input_editing(self.current_value_input, "current_units", "Current Work Units", is_total=False))
        current_layout.addWidget(self.current_value_input)
        self.project_details_layout.addLayout(current_layout)

        self.project_details_layout.addSpacing(25) # Increased spacing before progress bar

        # Progress Display Section
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.project_details_layout.addWidget(self.progress_bar)

        self.project_details_layout.addSpacing(10)

        self.percentage_label = QLabel("0.0%")
        self.percentage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.percentage_label.setObjectName("percentageLabel")
        self.project_details_layout.addWidget(self.percentage_label)

        self.etc_label = QLabel("ETC: --:--:--" )
        self.etc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.etc_label.setObjectName("etcLabel")
        self.project_details_layout.addWidget(self.etc_label)

        self.project_details_layout.addSpacing(25) # Increased spacing before buttons

        # Buttons Section for selected project
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        
        self.start_timer_button = QPushButton("Start Timer")
        self.start_timer_button.setIcon(QIcon.fromTheme("media-playback-start"))
        self.start_timer_button.clicked.connect(self.toggle_timer)
        self.start_timer_button.setObjectName("startButton")
        button_layout.addWidget(self.start_timer_button)

        reset_button = QPushButton("Reset All")
        reset_button.setIcon(QIcon.fromTheme("view-refresh"))
        reset_button.clicked.connect(self.reset_selected_project)
        reset_button.setObjectName("resetButton")
        button_layout.addWidget(reset_button)
        
        button_layout.addStretch(1)

        self.project_details_layout.addLayout(button_layout)
        self.project_details_layout.addStretch(1) # Pushes content to the top within the details frame

        content_layout.addWidget(project_details_frame)
        card_layout.addLayout(content_layout) # Add the combined content layout to the card

        main_layout.addWidget(card_frame) # Add the styled card to the main layout

        self.etc_timer.start() # Start the global ETC update timer

    def apply_styles(self):
        # Using a QSS string for a modern, dark theme with subtle depth
        self.setStyleSheet("""
            QWidget {
                background-color: #2C2F33; /* Dark background */
                font-family: 'Segoe UI', 'Arial', sans-serif;
                color: #ABB2BF; /* Light grey text for general readability */
            }
            #cardFrame {
                background-color: #36393F; /* Slightly lighter dark grey for the card */
                border-radius: 12px;
                border: 1px solid #4A4D52; /* Darker border for definition */
            }
            /* Removed custom window control button styles */

            QLabel {
                background-color: transparent; /* Make label backgrounds transparent */
                font-size: 14px;
                color: #ABB2BF; /* Light grey for general labels */
            }
            QLabel#titleLabel { /* This label is no longer used in the UI, but keeping style for consistency if added back */
                font-size: 18px;
                font-weight: bold;
                color: #F8F8F2; /* Off-white for main title */
            }
            QLabel b { /* Bold labels within layouts (e.g., section titles) */
                font-size: 15px;
                color: #E0E0E0; /* Lighter grey for section titles */
            }
            #projectListFrame, #projectDetailsFrame {
                border: 1px solid #4A4D52; /* Darker border */
                border-radius: 10px;
                background-color: #3F4248; /* Slightly lighter dark grey for content frames */
            }
            QListWidget {
                border: 1px solid #5F6368; /* Medium dark grey border */
                border-radius: 8px;
                padding: 5px;
                background-color: #36393F; /* Same as card for seamless look */
                color: #E0E0E0; /* Light text for list items */
            }
            QListWidget::item {
                padding: 8px 10px;
                margin-bottom: 3px;
                border-radius: 5px;
            }
            QListWidget::item:selected {
                background-color: #4A5568; /* Muted blue-grey for selection */
                color: #FFFFFF; /* White text on selection */
                font-weight: bold;
            }
            QListWidget::item:hover {
                background-color: #42454A; /* Slightly lighter dark grey on hover */
            }
            QLineEdit, QTextEdit {
                border: 1px solid #5F6368; /* Darker border */
                border-radius: 8px;
                padding: 8px 10px;
                font-size: 14px;
                background-color: transparent; /* Make background transparent */
                color: #E0E0E0; /* Light text for inputs */
                selection-background-color: #4A5568; /* Match list selection */
                selection-color: #FFFFFF;
            }
            QLineEdit::placeholder-text, QTextEdit::placeholder-text {
                color: #A0A0A0; /* Slightly lighter grey for placeholder on transparent background */
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 2px solid #2196F3; /* Vibrant blue on focus */
                background-color: rgba(63, 66, 72, 0.5); /* Subtle translucent background on focus */
            }
            QProgressBar {
                border: 1px solid #4A4D52; /* Dark border */
                border-radius: 8px;
                background-color: #3F4248; /* Match frame background */
                text-align: center;
                height: 18px;
            }
            QProgressBar::chunk {
                background-color: #42A5F5; /* Vibrant blue */
                border-radius: 8px;
            }
            #percentageLabel {
                font-size: 42px;
                font-weight: bold;
                color: #42A5F5; /* Vibrant blue */
            }
            #etcLabel {
                font-size: 22px;
                font-style: italic;
                color: #B0BEC5; /* Light grey */
            }
            QPushButton {
                padding: 12px 20px;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                color: #FFFFFF;
                border: none;
                min-width: 120px; /* Increased min-width for text */
                border-bottom: 3px solid; /* Defined by specific button styles */
            }
            QPushButton:hover {
                /* Background and border-bottom will be overridden by specific button styles */
            }
            QPushButton:pressed {
                /* Subtle press effect: reduce border-bottom, slightly adjust padding-top */
                border-bottom-width: 1px; /* Make bottom border thinner */
                padding-top: 13px; /* Move text down by 1px to simulate press */
            }
            QPushButton#startButton {
                background-color: #2196F3; /* Blue 500 */
                border-bottom-color: #1976D2; /* Darker blue */
            }
            QPushButton#startButton:hover {
                background-color: #42A5F5; /* Light Blue 400 */
                border-bottom-color: #2196F3;
            }
            QPushButton#startButton:pressed {
                background-color: #1976D2; /* Darker blue on press */
                border-bottom-color: #1976D2;
            }
            QPushButton#startButton[running="true"] {
                background-color: #F44336; /* Red 500 */
                border-bottom-color: #D32F2F; /* Darker red */
            }
            QPushButton#startButton[running="true"]:hover {
                background-color: #EF5350; /* Red 400 */
                border-bottom-color: #F44336;
            }
            QPushButton#startButton[running="true"]:pressed {
                background-color: #D32F2F; /* Darker red on press */
                border-bottom-color: #D32F2F;
            }
            QPushButton#resetButton, QPushButton#deleteProjectButton {
                background-color: #4A4D52; /* Dark grey background for secondary buttons */
                color: #E0E0E0; /* Light grey text */
                border: 1px solid #5F6368; /* Light border */
                border-bottom-color: #3F4248; /* Darker grey bottom border */
            }
            QPushButton#resetButton:hover, QPushButton#deleteProjectButton:hover {
                background-color: #5F6368; /* Slightly darker grey on hover */
                border-bottom-color: #4A4D52;
            }
            QPushButton#resetButton:pressed, QPushButton#deleteProjectButton:pressed {
                background-color: #3F4248;
                border-bottom-color: #3F4248;
            }
            QPushButton#addProjectButton {
                background-color: #17A2B8; /* Info Blue */
                border-bottom-color: #138496;
            }
            QPushButton#addProjectButton:hover {
                background-color: #20C997; /* Teal */
                border-bottom-color: #17A2B8;
            }
            QPushButton#addProjectButton:pressed {
                background-color: #138496;
                border-bottom-color: #138496;
            }
        """)
        # Set a dynamic property for the start button to control its style with QSS
        self.start_timer_button.setProperty("running", "false")
        self.start_timer_button.style().polish(self.start_timer_button)

    def add_new_project(self):
        """Adds a new project to the list and selects it."""
        new_project = Project(name=f"New Project {len(self.projects) + 1}")
        self.projects[new_project.id] = new_project
        
        item = QListWidgetItem(new_project.name)
        item.setData(Qt.ItemDataRole.UserRole, new_project.id) # Store ID in item data
        self.project_list_widget.addItem(item)
        self.project_list_widget.setCurrentItem(item) # Select the new project
        # No need to call save_projects here, as closeEvent will handle it

    def delete_selected_project(self):
        """Deletes the currently selected project."""
        current_item = self.project_list_widget.currentItem()
        if not current_item:
            QMessageBox.information(self, "Delete Project", "No project selected to delete.")
            return

        project_id_to_delete = current_item.data(Qt.ItemDataRole.UserRole)
        project_name = current_item.text()

        reply = QMessageBox.question(self, "Delete Project",
                                     f"Are you sure you want to delete '{project_name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # Stop timer if it's running for the deleted project
            if self.projects[project_id_to_delete].is_running:
                self.projects[project_id_to_delete].is_running = False
                # No need to stop global timer, it continues for other projects

            del self.projects[project_id_to_delete]
            row = self.project_list_widget.row(current_item)
            self.project_list_widget.takeItem(row)
            
            self.current_project_id = None # Clear current selection

            if self.project_list_widget.count() > 0:
                self.project_list_widget.setCurrentRow(0) # Select the first project if available
            else:
                # If no projects left, clear details view
                self.project_name_input.setText("")
                self.project_description_input.setText("") # Clear description
                self.total_value_input.setText("0.0")
                self.current_value_input.setText("0.0")
                self.etc_label.setText("ETC: --:--:--")
                self.percentage_label.setText("0.0%")
                self.progress_bar.setValue(0)
                self.start_timer_button.setText("Start Timer")
                self.start_timer_button.setProperty("running", "false")
                self.start_timer_button.style().polish(self.start_timer_button)
            # No need to call save_projects here, as closeEvent will handle it


    def select_project_from_list(self, current_item: QListWidgetItem, previous_item: QListWidgetItem):
        """Loads the selected project's data into the UI."""
        if current_item is None:
            self.current_project_id = None
            # Clear UI if no project is selected
            self.project_name_input.setText("")
            self.project_description_input.setText("") # Clear description
            self.total_value_input.setText("0.0")
            self.current_value_input.setText("0.0")
            self.etc_label.setText("ETC: --:--:--")
            self.percentage_label.setText("0.0%")
            self.progress_bar.setValue(0)
            self.start_timer_button.setText("Start Timer")
            self.start_timer_button.setIcon(QIcon.fromTheme("media-playback-start"))
            self.start_timer_button.setProperty("running", "false")
            self.start_timer_button.style().polish(self.start_timer_button)
            return

        project_id = current_item.data(Qt.ItemDataRole.UserRole)
        if project_id == self.current_project_id:
            return # Already selected

        self.current_project_id = project_id
        project = self.projects[self.current_project_id]

        # Update UI elements with selected project's data
        self.project_name_input.setText(project.name)
        self.project_description_input.setText(project.description) # Set description
        self.total_value_input.setText(f"{project.total_units:.1f}")
        self.current_value_input.setText(f"{project.current_units:.1f}")

        # Update timer button state
        if project.is_running:
            self.start_timer_button.setText("Stop Timer")
            self.start_timer_button.setIcon(QIcon.fromTheme("media-playback-stop"))
            self.start_timer_button.setProperty("running", "true")
        else:
            self.start_timer_button.setText("Start Timer")
            self.start_timer_button.setIcon(QIcon.fromTheme("media-playback-start"))
            self.start_timer_button.setProperty("running", "false")
        self.start_timer_button.style().polish(self.start_timer_button)

        self._update_display_from_inputs() # Refresh progress and ETC for the new selection

    def _on_project_name_changed(self):
        """Updates the selected project's name in the data model and list widget."""
        if self.current_project_id:
            new_name = self.project_name_input.text()
            # Only update if the name is not empty or just whitespace
            if new_name.strip():
                self.projects[self.current_project_id].name = new_name
                current_item = self.project_list_widget.currentItem()
                if current_item:
                    current_item.setText(new_name)
            # No need to call save_projects here, as closeEvent will handle it

    def _on_project_description_changed(self):
        """Updates the selected project's description in the data model."""
        if self.current_project_id:
            self.projects[self.current_project_id].description = self.project_description_input.toPlainText()
        # No need to call save_projects here, as closeEvent will handle it

    def _get_safe_value(self, line_edit: QLineEdit, default_val: float) -> float:
        """Safely gets a float from a QLineEdit, handling empty strings or errors during real-time input."""
        try:
            val_str = line_edit.text()
            if not val_str.strip():
                return default_val
            return float(val_str)
        except ValueError:
            return default_val

    def _finalize_input_editing(self, line_edit: QLineEdit, project_attr: str, field_name: str, is_total: bool):
        """
        Performs final validation and reformatting when editing is finished.
        Updates the project data and shows QMessageBox for invalid inputs.
        """
        if not self.current_project_id:
            return

        project = self.projects[self.current_project_id]
        text = line_edit.text()
        try:
            value = float(text)
            
            # --- Enhanced Validation Logic ---
            if is_total:
                if value <= 0:
                    QMessageBox.warning(self, "Input Error", f"{field_name} must be a positive number.")
                    value = getattr(project, project_attr) # Revert to last valid value
                elif value < project.current_units: # Total cannot be less than current
                    QMessageBox.warning(self, "Input Error", f"{field_name} cannot be less than Current Work Units. Setting to Current Work Units.")
                    value = project.current_units # Cap total at current
            else: # is_current_units
                if value < 0:
                    QMessageBox.warning(self, "Input Error", f"{field_name} cannot be negative.")
                    value = getattr(project, project_attr) # Revert to last valid value
                elif value > project.total_units: # Current cannot exceed total
                    QMessageBox.information(self, "Input Info", f"{field_name} cannot exceed Total Work Units. Setting to Total Work Units.")
                    value = project.total_units # Cap current at total
                    if project.is_running: # If timer was running and now complete
                        self.toggle_timer(project.id) # Stop the timer

            setattr(project, project_attr, value) # Update project data
            line_edit.setText(f"{value:.1f}") # Reformat to 1 decimal place

        except ValueError:
            if text.strip() != "": # Only warn if something was typed that isn't a number
                QMessageBox.warning(self, "Input Error", f"Please enter a valid number for {field_name}.")
            line_edit.setText(f"{getattr(project, project_attr):.1f}") # Revert to last valid value
        
        self._update_display_from_inputs() # Update display after finalization
        # No need to call save_projects here, as closeEvent will handle it

    def _update_display_from_inputs(self):
        """Updates display elements based on current (potentially unfinalized) input values of the selected project."""
        if not self.current_project_id:
            return

        project = self.projects[self.current_project_id]
        
        # Read from input fields, not directly from project object, for real-time feedback during typing
        current = self._get_safe_value(self.current_value_input, default_val=project.current_units)
        total = self._get_safe_value(self.total_value_input, default_val=project.total_units)

        # Update project object with current input values (temporarily, finalized on editingFinished)
        # This is important for ETC calculation to use the latest typed values
        project.current_units = current
        project.total_units = total

        progress_percentage = 0.0
        if total > 0:
            progress_percentage = (current / total) * 100
        
        self.progress_bar.setValue(int(min(progress_percentage, 100.0)))

        self.percentage_label.setText(f"{min(progress_percentage, 100.0):.1f}%")
        self.update_etc_for_project(project) # Update ETC specifically for the displayed project

    def format_time(self, seconds: float) -> str:
        """Formats a time duration in seconds into HH:MM:SS."""
        if seconds is None or seconds < 0:
            return "--:--:--"
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def update_etc_for_project(self, project: Project):
        """Calculates and updates the Estimated Time to Completion (ETC) for a given project."""
        if not project.is_running:
            # If paused, display elapsed time
            if project.start_time is not None:
                elapsed_display = self.format_time(project.elapsed_at_pause)
                if project.id == self.current_project_id: # Only update if it's the currently displayed project
                    self.etc_label.setText(f"ETC: Paused ({elapsed_display} elapsed)")
            else:
                if project.id == self.current_project_id:
                    self.etc_label.setText("ETC: --:--:--")
            return

        try:
            # Calculate current elapsed time including any time before pause
            current_elapsed_time = project.elapsed_at_pause + (time.time() - project.start_time)

            if project.total_units <= 0:
                if project.id == self.current_project_id:
                    self.etc_label.setText("ETC: Total > 0 req.")
                return

            # If current units are 0 and timer just started, or elapsed time is effectively zero
            if math.isclose(project.current_units, 0.0) or math.isclose(current_elapsed_time, 0.0):
                if project.id == self.current_project_id:
                    self.etc_label.setText("ETC: Calculating...")
                return
            
            progress_ratio = project.current_units / project.total_units
            
            if progress_ratio >= 1.0:
                if project.id == self.current_project_id:
                    self.etc_label.setText("ETC: Complete!")
                if project.is_running:
                    # Automatically stop timer if project is complete
                    self.toggle_timer(project.id) 
                return
            elif progress_ratio > 0:
                rate = project.current_units / current_elapsed_time
                remaining_time = (project.total_units - project.current_units) / rate
                if project.id == self.current_project_id:
                    self.etc_label.setText(f"ETC: {self.format_time(remaining_time)}")
            else:
                if project.id == self.current_project_id:
                    self.etc_label.setText("ETC: Estimating...")
        except (ValueError, ZeroDivisionError):
            if project.id == self.current_project_id:
                self.etc_label.setText("ETC: Error")

    def update_all_etcs(self):
        """Called by the global QTimer to update ETC for all projects."""
        for project in self.projects.values():
            self.update_etc_for_project(project)

    def toggle_timer(self, project_id: Optional[str] = None):
        """Starts or stops the timer for the specified project ID, or current if none."""
        if project_id is None:
            project_id = self.current_project_id

        if not project_id or project_id not in self.projects:
            QMessageBox.information(self, "Timer Control", "No project selected or invalid project.")
            return

        project = self.projects[project_id]

        # Ensure latest values are validated and reflected before starting/stopping
        # Call finalize for both inputs to ensure they are properly validated and formatted
        # Only do this if the project being toggled is the currently displayed one
        if project_id == self.current_project_id:
            # Force finalization and update of project data from UI inputs
            self._finalize_input_editing(self.total_value_input, "total_units", "Total Work Units", is_total=True)
            self._finalize_input_editing(self.current_value_input, "current_units", "Current Work Units", is_total=False)
            # Re-fetch values from the project object after finalization, as they might have been capped
            project.total_units = self._get_safe_value(self.total_value_input, default_val=project.total_units)
            project.current_units = self._get_safe_value(self.current_value_input, default_val=project.current_units)


        if not project.is_running:
            # Pre-flight checks before starting
            if project.total_units <= 0:
                QMessageBox.warning(self, "Timer Error", "Total Work Units must be a positive number to start the timer.")
                return
            if project.current_units < 0:
                QMessageBox.warning(self, "Timer Error", "Current Work Units cannot be negative.")
                return
            if project.current_units >= project.total_units:
                QMessageBox.information(self, "Timer Info", "Current Work Units already meet or exceed Total. Project is complete. No need to start timer.")
                self.update_etc_for_project(project) # Ensure ETC says "Complete!"
                return

            project.start_time = time.time()
            project.is_running = True
            
            if project_id == self.current_project_id:
                self.start_timer_button.setText("Stop Timer")
                self.start_timer_button.setIcon(QIcon.fromTheme("media-playback-stop"))
                self.start_timer_button.setProperty("running", "true")
        else:
            # When stopping, update elapsed_at_pause
            if project.start_time is not None:
                project.elapsed_at_pause += (time.time() - project.start_time)
            project.is_running = False
            project.start_time = None # Clear start time when paused
            
            if project_id == self.current_project_id:
                self.start_timer_button.setText("Start Timer")
                self.start_timer_button.setIcon(QIcon.fromTheme("media-playback-start"))
                self.start_timer_button.setProperty("running", "false")

        # Re-polish the button style to apply QSS changes if it's the current project
        if project_id == self.current_project_id:
            self.start_timer_button.style().polish(self.start_timer_button)
            self.update_etc_for_project(project) # Update ETC display for paused state

    def reset_selected_project(self):
        """Resets all values for the currently selected project and stops its timer."""
        if not self.current_project_id:
            QMessageBox.information(self, "Reset Project", "No project selected to reset.")
            return

        project = self.projects[self.current_project_id]

        project.is_running = False
        project.start_time = None
        project.elapsed_at_pause = 0.0
        
        project.current_units = 0.0
        project.total_units = 100.0 # Reset total to default too
        project.description = "" # Reset description

        # Update UI fields for the current project
        self.current_value_input.setText(f"{project.current_units:.1f}")
        self.total_value_input.setText(f"{project.total_units:.1f}")
        self.project_description_input.setText(project.description) # Update description field
        
        self.start_timer_button.setText("Start Timer")
        self.start_timer_button.setIcon(QIcon.fromTheme("media-playback-start"))
        self.start_timer_button.setProperty("running", "false")
        self.start_timer_button.style().polish(self.start_timer_button) # Re-polish
        
        self._update_display_from_inputs() # Ensure everything is updated


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernProgressBarApp()
    window.show()
    sys.exit(app.exec())
