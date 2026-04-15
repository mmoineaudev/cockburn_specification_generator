#!/usr/bin/env python3
"""
Cockburn Specification Generator - GUI Version
"""

import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QMenuBar, QMenu, 
                             QAction, QStatusBar, QTreeWidget, QTreeWidgetItem, QSplitter,
                             QTextEdit, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QComboBox, QFileDialog,
                             QMessageBox, QInputDialog, QFrame, QTabWidget)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon, QKeySequence

class CockburnGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.project_path = None
        self.use_cases = {}
        self.current_use_case = None
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        self.load_project()
        
    def setup_ui(self):
        """Setup the main UI components"""
        self.setWindowTitle("Cockburn Specification Generator V2")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for left navigation and right editor
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left navigation panel
        self.create_navigation_panel(splitter)
        
        # Right editor panel
        self.create_editor_panel(splitter)
        
        # Setup auto-save
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(30000)  # 30 seconds
        
        # Setup extension auto-save
        self.extension_auto_save_timer = QTimer()
        self.extension_auto_save_timer.timeout.connect(self.auto_save_extensions)
        self.extension_auto_save_timer.start(30000)  # 30 seconds
        
    def create_navigation_panel(self, parent):
        """Create the left navigation panel"""
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        
        # Navigation title
        title_label = QLabel("Navigation")
        title_font = QFont()
        title_font.setBold(True)
        title_label.setFont(title_font)
        nav_layout.addWidget(title_label)
        
        # Navigation tree
        self.navigation_tree = QTreeWidget()
        self.navigation_tree.setHeaderLabels(["Use Cases"])
        self.navigation_tree.itemClicked.connect(self.on_use_case_selected)
        self.navigation_tree.itemDoubleClicked.connect(self.on_use_case_double_clicked)
        nav_layout.addWidget(self.navigation_tree)
        
        # Navigation buttons
        nav_buttons_layout = QHBoxLayout()
        
        new_button = QPushButton("New Use Case")
        new_button.clicked.connect(self.create_new_use_case)
        nav_buttons_layout.addWidget(new_button)
        
        open_button = QPushButton("Open Project")
        open_button.clicked.connect(self.open_project)
        nav_buttons_layout.addWidget(open_button)
        
        save_button = QPushButton("Save Project")
        save_button.clicked.connect(self.save_project)
        nav_buttons_layout.addWidget(save_button)
        
        nav_layout.addLayout(nav_buttons_layout)
        
        parent.addWidget(nav_widget)
        
    def create_editor_panel(self, parent):
        """Create the right editor panel"""
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        
        # Create tab widget for different sections
        self.tab_widget = QTabWidget()
        editor_layout.addWidget(self.tab_widget)
        
        # Characteristic Information Tab
        self.create_characteristic_tab()
        
        # Main Success Scenario Tab
        self.create_main_scenario_tab()
        
        # Extensions Tab
        self.create_extensions_tab()
        
        # Sub-Variations Tab
        self.create_subvariations_tab()
        
        # Extensions Tab - Add this after Sub-Variations Tab
        self.create_extensions_tab()
        
        parent.addWidget(editor_widget)
        
    def create_characteristic_tab(self):
        """Create the characteristic information tab"""
        char_widget = QWidget()
        char_layout = QVBoxLayout(char_widget)
        
        # Header
        char_header = QLabel("Characteristic Information")
        char_header_font = QFont()
        char_header_font.setBold(True)
        char_header.setFont(char_header_font)
        char_layout.addWidget(char_header)
        
        # Form fields
        form_layout = QVBoxLayout()
        
        # Goal in Context
        goal_label = QLabel("Goal in Context:")
        goal_input = QTextEdit()
        goal_input.setMaximumHeight(80)
        form_layout.addWidget(goal_label)
        form_layout.addWidget(goal_input)
        
        # Scope
        scope_label = QLabel("Scope:")
        scope_input = QTextEdit()
        scope_input.setMaximumHeight(60)
        form_layout.addWidget(scope_label)
        form_layout.addWidget(scope_input)
        
        # Level
        level_label = QLabel("Level:")
        level_combo = QComboBox()
        level_combo.addItems(["Primary Task", "Summary", "Subfunction"])
        form_layout.addWidget(level_label)
        form_layout.addWidget(level_combo)
        
        # Preconditions
        preconditions_label = QLabel("Preconditions:")
        preconditions_input = QTextEdit()
        preconditions_input.setMaximumHeight(60)
        form_layout.addWidget(preconditions_label)
        form_layout.addWidget(preconditions_input)
        
        # Success End Condition
        success_label = QLabel("Success End Condition:")
        success_input = QTextEdit()
        success_input.setMaximumHeight(60)
        form_layout.addWidget(success_label)
        form_layout.addWidget(success_input)
        
        # Failed End Condition
        failed_label = QLabel("Failed End Condition:")
        failed_input = QTextEdit()
        failed_input.setMaximumHeight(60)
        form_layout.addWidget(failed_label)
        form_layout.addWidget(failed_input)
        
        # Primary Actor
        actor_label = QLabel("Primary Actor:")
        actor_input = QLineEdit()
        form_layout.addWidget(actor_label)
        form_layout.addWidget(actor_input)
        
        # Trigger
        trigger_label = QLabel("Trigger:")
        trigger_input = QLineEdit()
        form_layout.addWidget(trigger_label)
        form_layout.addWidget(trigger_input)
        
        char_layout.addLayout(form_layout)
        self.tab_widget.addTab(char_widget, "Characteristic Info")
        
    def create_main_scenario_tab(self):
        """Create the main success scenario tab"""
        scenario_widget = QWidget()
        scenario_layout = QVBoxLayout(scenario_widget)
        
        # Header
        scenario_header = QLabel("Main Success Scenario")
        scenario_header_font = QFont()
        scenario_header_font.setBold(True)
        scenario_header.setFont(scenario_header_font)
        scenario_layout.addWidget(scenario_header)
        
        # Scenario editor
        self.scenario_editor = QTextEdit()
        self.scenario_editor.setPlaceholderText("Enter main success scenario steps here (one per line)")
        scenario_layout.addWidget(self.scenario_editor)
        
        self.tab_widget.addTab(scenario_widget, "Main Scenario")
        
    def create_extensions_tab(self):
        """Create the extensions tab"""
        extensions_widget = QWidget()
        extensions_layout = QVBoxLayout(extensions_widget)
        
        # Header
        extensions_header = QLabel("Extensions")
        extensions_header_font = QFont()
        extensions_header_font.setBold(True)
        extensions_header.setFont(extensions_header_font)
        extensions_layout.addWidget(extensions_header)
        
        # Extensions editor
        self.extensions_editor = QTextEdit()
        self.extensions_editor.setPlaceholderText("Enter extensions here (one per line)")
        extensions_layout.addWidget(self.extensions_editor)
        
        self.tab_widget.addTab(extensions_widget, "Extensions")
        
    def create_subvariations_tab(self):
        """Create the sub-variations tab"""
        subvariations_widget = QWidget()
        subvariations_layout = QVBoxLayout(subvariations_widget)
        
        # Header
        subvariations_header = QLabel("Sub-Variations")
        subvariations_header_font = QFont()
        subvariations_header_font.setBold(True)
        subvariations_header.setFont(subvariations_header_font)
        subvariations_layout.addWidget(subvariations_header)
        
        # Sub-variations editor
        self.subvariations_editor = QTextEdit()
        self.subvariations_editor.setPlaceholderText("Enter sub-variations here (one per line)")
        subvariations_layout.addWidget(self.subvariations_editor)
        
        self.tab_widget.addTab(subvariations_widget, "Sub-Variations")
        
    def create_extensions_tab(self):
        """Create the extensions tab"""
        extensions_widget = QWidget()
        extensions_layout = QVBoxLayout(extensions_widget)
        
        # Header
        extensions_header = QLabel("Extensions")
        extensions_header_font = QFont()
        extensions_header_font.setBold(True)
        extensions_header.setFont(extensions_header_font)
        extensions_layout.addWidget(extensions_header)
        
        # Add button for new extensions
        add_extension_button = QPushButton("Add Extension (+)")
        add_extension_button.clicked.connect(self.add_extension)
        extensions_layout.addWidget(add_extension_button)
        
        # Extensions list/preview area
        self.extensions_preview = QTextEdit()
        self.extensions_preview.setReadOnly(True)
        # Add styling for extensions
        self.extensions_preview.setStyleSheet("""
            QTextEdit {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        extensions_layout.addWidget(self.extensions_preview)
        
        self.tab_widget.addTab(extensions_widget, "Extensions")
        
    def display_extension(self, step, condition, action, linked_use_case=None):
        """Display an extension with proper formatting"""
        # Format the extension properly
        if linked_use_case:
            extension_text = f"* ***step altered #{step}*** > {condition} : {action} (linked to {linked_use_case})\n"
        else:
            extension_text = f"* ***step altered #{step}*** > {condition} : {action}\n"
            
        self.extensions_preview.append(extension_text)
        self.extensions_preview.moveCursor(self.extensions_preview.textCursor().End)
        
    def setup_menu(self):
        """Setup the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New Project", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open Project", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save Project", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save As", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_project_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        find_action = QAction("Find", self)
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        edit_menu.addAction(find_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        export_word_action = QAction("Export to Word", self)
        export_word_action.triggered.connect(self.export_to_word)
        tools_menu.addAction(export_word_action)
        
        export_pdf_action = QAction("Export to PDF", self)
        export_pdf_action.triggered.connect(self.export_to_pdf)
        tools_menu.addAction(export_pdf_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_status_bar(self):
        """Setup the status bar"""
        self.statusBar().showMessage("Ready")
        
    def load_project(self):
        """Load an existing project or create a new one"""
        # For now, just initialize an empty project
        self.project_path = "./projects/default_project"
        os.makedirs(self.project_path, exist_ok=True)
        os.makedirs(f"{self.project_path}/markdown", exist_ok=True)
        os.makedirs(f"{self.project_path}/word", exist_ok=True)
        self.update_navigation_tree()
        
    def new_project(self):
        """Create a new project"""
        project_name, ok = QInputDialog.getText(self, "New Project", "Enter project name:")
        if ok and project_name:
            self.project_path = f"./projects/{project_name}"
            os.makedirs(self.project_path, exist_ok=True)
            os.makedirs(f"{self.project_path}/markdown", exist_ok=True)
            os.makedirs(f"{self.project_path}/word", exist_ok=True)
            self.update_navigation_tree()
            self.statusBar().showMessage(f"Created project: {project_name}")
            
    def open_project(self):
        """Open an existing project"""
        project_dir = QFileDialog.getExistingDirectory(self, "Open Project", "./projects")
        if project_dir:
            self.project_path = project_dir
            self.update_navigation_tree()
            self.statusBar().showMessage(f"Opened project: {os.path.basename(project_dir)}")
            
    def save_project(self):
        """Save the current project"""
        if self.project_path:
            # Save current use case if exists
            if self.current_use_case:
                self.save_current_use_case()
            
            # Save project metadata
            metadata = {
                "project_name": os.path.basename(self.project_path),
                "last_modified": "2024-01-01T00:00:00Z"
            }
            
            with open(f"{self.project_path}/metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
                
            self.statusBar().showMessage("Project saved successfully")
            
    def save_project_as(self):
        """Save project with a new name"""
        new_path, ok = QInputDialog.getText(self, "Save Project As", "Enter new project path:")
        if ok and new_path:
            self.project_path = new_path
            self.save_project()
            
    def create_new_use_case(self):
        """Create a new use case"""
        # Get use case name from user
        use_case_name, ok = QInputDialog.getText(self, "New Use Case", "Enter use case name:")
        if not ok or not use_case_name:
            return
            
        # Auto-number the use case
        use_case_number = self.get_next_use_case_number()
        filename = f"UC-{use_case_number:03d}_{use_case_name.replace(' ', '_')}"
        
        # Create the use case file
        use_case_path = f"{self.project_path}/markdown/{filename}.md"
        with open(use_case_path, "w") as f:
            f.write(f"# {filename}\n\n")
            f.write("## Characteristic Information\n\n")
            f.write("* Goal in Context: \n")
            f.write("* Scope: \n")
            f.write("* Level: \n")
            f.write("* Preconditions: \n")
            f.write("* Success End Condition: \n")
            f.write("* Failed End Condition: \n")
            f.write("* Primary Actor: \n")
            f.write("* Trigger: \n\n")
            
            f.write("## Main Success Scenario\n\n")
            f.write("* step #1: \n\n")
            
            f.write("## Extensions\n\n")
            f.write("* step altered #1: \n\n")
            
            f.write("## Sub-Variations\n\n")
            f.write("* step #1: \n\n")
        
        # Update navigation tree
        self.update_navigation_tree()
        
        # Open the new use case
        self.open_use_case(filename)
        
        self.statusBar().showMessage(f"Created use case: {filename}")
        
    def get_next_use_case_number(self):
        """Get the next available use case number"""
        try:
            markdown_dir = f"{self.project_path}/markdown"
            use_case_files = [f for f in os.listdir(markdown_dir) if f.endswith('.md')]
            
            if not use_case_files:
                return 1
                
            # Extract numbers from existing use cases
            numbers = []
            for file in use_case_files:
                # Extract number from UC-001_file_name.md format
                if file.startswith('UC-'):
                    parts = file.split('_')
                    if len(parts) > 0:
                        number_part = parts[0]
                        if number_part.startswith('UC-'):
                            try:
                                num = int(number_part[3:6])
                                numbers.append(num)
                            except ValueError:
                                pass
            
            return max(numbers) + 1 if numbers else 1
            
        except Exception:
            return 1
            
    def update_navigation_tree(self):
        """Update the navigation tree with current use cases"""
        self.navigation_tree.clear()
        
        if self.project_path:
            try:
                markdown_dir = f"{self.project_path}/markdown"
                use_case_files = [f for f in os.listdir(markdown_dir) if f.endswith('.md')]
                
                for file in use_case_files:
                    item = QTreeWidgetItem([file])
                    self.navigation_tree.addTopLevelItem(item)
                    
            except Exception as e:
                print(f"Error updating navigation tree: {e}")
                
    def on_use_case_selected(self, item):
        """Handle use case selection"""
        use_case_file = item.text(0)
        self.open_use_case(use_case_file)
        
    def on_use_case_double_clicked(self, item):
        """Handle double-click on use case"""
        use_case_file = item.text(0)
        self.open_use_case(use_case_file)
        
    def open_use_case(self, use_case_file):
        """Open a use case for editing"""
        self.current_use_case = use_case_file
        self.statusBar().showMessage(f"Opened use case: {use_case_file}")
        
        # Load and display the content
        use_case_path = f"{self.project_path}/markdown/{use_case_file}"
        if os.path.exists(use_case_path):
            with open(use_case_path, "r") as f:
                content = f.read()
                # In a real implementation, we would parse the content
                # and populate the fields in the editor tabs
                pass
                
    def save_current_use_case(self):
        """Save the currently open use case"""
        if self.current_use_case:
            # In a real implementation, this would save the content
            # from the editor fields back to the file
            pass
            
    def auto_save(self):
        """Automatically save the project every 30 seconds"""
        self.save_project()
        self.statusBar().showMessage("Auto-saved at " + self.get_current_time())
        
    def auto_save_extensions(self):
        """Automatically save extensions every 30 seconds"""
        # In a real implementation, this would save the current extensions
        # to the use case file or a separate extensions file
        pass
        
    def get_current_time(self):
        """Get current time for status messages"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
        
    def export_to_word(self):
        """Export current use case to Word"""
        if self.current_use_case:
            QMessageBox.information(self, "Export to Word", 
                                  f"Exporting {self.current_use_case} to Word format")
        else:
            QMessageBox.warning(self, "Export Error", "No use case selected")
            
    def export_to_pdf(self):
        """Export current use case to PDF"""
        if self.current_use_case:
            QMessageBox.information(self, "Export to PDF", 
                                  f"Exporting {self.current_use_case} to PDF format")
        else:
            QMessageBox.warning(self, "Export Error", "No use case selected")
            
    def add_extension(self):
        """Add a new extension to the current use case"""
        # Create a dialog for adding extensions
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTextEdit, QPushButton, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Extension")
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        
        # Step number selection
        step_layout = QHBoxLayout()
        step_layout.addWidget(QLabel("Step to extend:"))
        self.step_combo = QComboBox()
        # For demo purposes, we'll populate with some sample steps
        self.step_combo.addItems(["Step 1", "Step 2", "Step 3"]) 
        step_layout.addWidget(self.step_combo)
        layout.addLayout(step_layout)
        
        # Condition type
        condition_layout = QHBoxLayout()
        condition_layout.addWidget(QLabel("Condition type:"))
        self.condition_combo = QComboBox()
        self.condition_combo.addItems(["timeout", "error", "validation", "system"])
        condition_layout.addWidget(self.condition_combo)
        layout.addLayout(condition_layout)
        
        # Condition description
        layout.addWidget(QLabel("Condition description:"))
        self.condition_text = QTextEdit()
        self.condition_text.setMaximumHeight(80)
        # Add character counter
        self.condition_char_count = QLabel("0/500 characters")
        layout.addWidget(self.condition_text)
        layout.addWidget(self.condition_char_count)
        
        # Connect text changed signal
        self.condition_text.textChanged.connect(self.update_condition_char_count)
        
    def update_condition_char_count(self):
        """Update the character count for condition description"""
        text = self.condition_text.toPlainText()
        self.condition_char_count.setText(f"{len(text)}/500 characters")
        
        # Action description
        layout.addWidget(QLabel("Action or alternative path:"))
        self.action_text = QTextEdit()
        self.action_text.setMaximumHeight(80)
        layout.addWidget(self.action_text)
        
        # Optional use case linking
        layout.addWidget(QLabel("Link to existing use case (optional):"))
        self.link_combo = QComboBox()
        # For demo purposes, we'll populate with sample use cases
        self.link_combo.addItems(["UC-001_Create New Use Case", "UC-002_Edit Characteristic Information", "UC-003_Edit Main Success Scenario"])  
        layout.addWidget(self.link_combo)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # In a real implementation, this would save the extension
            step = self.step_combo.currentText()
            condition = self.condition_combo.currentText()
            condition_desc = self.condition_text.toPlainText()
            action_desc = self.action_text.toPlainText()
            linked_use_case = self.link_combo.currentText() if self.link_combo.currentText() != "" else None
            
            # Display the extension in the preview
            self.display_extension(step, condition, action_desc, linked_use_case)
            
            QMessageBox.information(self, "Extension Added", f"Extension added for {step}")
        
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About Cockburn Specification Generator",
                         "Cockburn Specification Generator V2\n\n"
                         "A modern GUI application for creating Cockburn use case specifications.")

def main():
    app = QApplication(sys.argv)
    window = CockburnGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()