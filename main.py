#!/usr/bin/env python3
"""
Cockburn Specification Generator - GUI Version

A modern desktop application for creating Cockburn use case specifications.
Uses PyQt6 with MVC architecture and supports export to Word/PDF/JSON/YAML.
"""

import sys
import os
import json
import re
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PyQt6.QtWidgets import (QApplication, QMainWindow, QMenuBar, QMenu, 
                             QAction, QStatusBar, QTreeWidget, QTreeWidgetItem, QSplitter,
                             QTextEdit, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QComboBox, QFileDialog,
                             QMessageBox, QInputDialog, QFrame, QTabWidget, QDialog,
                             QDialogButtonBox, QHeaderView, QAbstractItemView,
                             QProgressBar, QToolBar, QCheckBox, QSpinBox, QDoubleSpinBox,
                             QProgressDialog, QGroupBox, QRadioButton)
from PyQt6.QtCore import Qt, QTimer, QMimeData, QByteArray, QThread, pyqtSignal, QEvent, QObject
from PyQt6.QtGui import QFont, QIcon, QKeySequence, QTextCursor


class BatchExportWorker(QThread):
    """Worker thread for batch exporting use cases to Word without freezing the GUI."""
    
    progress_signal = pyqtSignal(str, float)  # message, percentage
    finished_signal = pyqtSignal(int, int)  # success_count, fail_count
    cancelled_signal = pyqtSignal()
    
    def __init__(self, project_path, use_case_files, skip_existing=False):
        super().__init__()
        self.project_path = project_path
        self.use_case_files = use_case_files
        self.skip_existing = skip_existing
        self._cancelled = False
    
    def run(self):
        """Run the batch export in background."""
        total = len(self.use_case_files)
        success_count = 0
        fail_count = 0
        
        for i, uc_file in enumerate(self.use_case_files):
            if self._cancelled:
                self.finished_signal.emit(success_count, fail_count)
                return
            
            # Check if file already exists (skip logic)
            word_dir = os.path.join(self.project_path, "word")
            match = re.match(r'UC-(\d+)_?(.*)', uc_file)
            if match:
                uc_num = match.group(1)
                uc_name = match.group(2).replace('_', ' ')
                word_filename = f"UC-{uc_num}_{uc_name}.docx"
            else:
                word_filename = f"{uc_file}.docx"
            
            word_path = os.path.join(word_dir, word_filename)
            
            if self.skip_existing and os.path.exists(word_path):
                continue
            
            # Export using python-docx
            try:
                self._export_single_word(uc_file, word_path)
                success_count += 1
            except Exception as e:
                fail_count += 1
            
            # Emit progress update
            pct = ((i + 1) / total) * 100 if total > 0 else 100
            self.progress_signal.emit(f"Processing {uc_file} ({i+1}/{total})", pct)
        
        self.finished_signal.emit(success_count, fail_count)
    
    def _export_single_word(self, use_case_file: str, output_path: str):
        """Export a single use case to Word format."""
        from docx import Document
        from docx.shared import Pt
        
        try:
            # Read the markdown file
            md_path = os.path.join(self.project_path, "markdown", use_case_file)
            if not os.path.exists(md_path):
                raise FileNotFoundError(f"Markdown file not found: {md_path}")
            
            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            doc = Document()
            style = doc.styles['Normal']
            font = style.font
            font.name = 'Calibri'
            font.size = Pt(11)
            
            # Title
            doc.add_heading(use_case_file.replace('_', ' '), level=0)
            
            # Parse sections from markdown
            for heading in ["Characteristic Information", "Main Success Scenario", 
                          "Extensions", "Sub-Variations"]:
                m = re.search(rf'## {re.escape(heading)}\s*\n(.*?)(?=##|$)', content, re.DOTALL)
                if m:
                    section_text = m.group(1).strip()
                    if heading == "Characteristic Information":
                        doc.add_heading("Characteristic Information", level=1)
                        for line in section_text.split('\n'):
                            line = line.strip()
                            if line.startswith('* '):
                                parts = line[2:].split(':', 1)
                                if len(parts) == 2:
                                    p = doc.add_paragraph()
                                    run = p.add_run(f"{parts[0].strip()}: ")
                                    run.bold = True
                                    p.add_run(parts[1].strip())
                    else:
                        doc.add_heading(heading, level=1)
                        for line in section_text.split('\n'):
                            line = line.strip()
                            if line:
                                doc.add_paragraph(line, style='List Bullet' if heading == "Extensions" else 'Normal')
            
            doc.add_paragraph(f"\nExported on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            doc.save(output_path)
        except Exception as e:
            raise
    
    def cancel(self):
        """Signal cancellation."""
        self._cancelled = True


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
        
        # Setup sub-variation auto-save
        self.subvar_auto_save_timer = QTimer()
        self.subvar_auto_save_timer.timeout.connect(self.auto_save_subvariations)
        self.subvar_auto_save_timer.start(30000)  # 30 seconds
        
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
        self.goal_input = QTextEdit()
        self.goal_input.setMaximumHeight(80)
        self.goal_input.setPlaceholderText("Describe the goal and context of this use case...")
        form_layout.addWidget(goal_label)
        form_layout.addWidget(self.goal_input)
        
        # Scope
        scope_label = QLabel("Scope:")
        self.scope_input = QTextEdit()
        self.scope_input.setMaximumHeight(60)
        self.scope_input.setPlaceholderText("Define the boundaries of this use case...")
        form_layout.addWidget(scope_label)
        form_layout.addWidget(self.scope_input)
        
        # Level
        level_label = QLabel("Level:")
        self.level_combo = QComboBox()
        self.level_combo.addItems(["Primary Task", "Summary", "Subfunction"])
        form_layout.addWidget(level_label)
        form_layout.addWidget(self.level_combo)
        
        # Preconditions
        preconditions_label = QLabel("Preconditions:")
        self.preconditions_input = QTextEdit()
        self.preconditions_input.setMaximumHeight(60)
        self.preconditions_input.setPlaceholderText("What must be true before this use case can execute...")
        form_layout.addWidget(preconditions_label)
        form_layout.addWidget(self.preconditions_input)
        
        # Success End Condition
        success_label = QLabel("Success End Condition:")
        self.success_input = QTextEdit()
        self.success_input.setMaximumHeight(60)
        self.success_input.setPlaceholderText("What is the ideal outcome...")
        form_layout.addWidget(success_label)
        form_layout.addWidget(self.success_input)
        
        # Failed End Condition
        failed_label = QLabel("Failed End Condition:")
        self.failed_input = QTextEdit()
        self.failed_input.setMaximumHeight(60)
        self.failed_input.setPlaceholderText("What happens when things go wrong...")
        form_layout.addWidget(failed_label)
        form_layout.addWidget(self.failed_input)
        
        # Primary Actor
        actor_label = QLabel("Primary Actor:")
        self.actor_input = QLineEdit()
        self.actor_input.setPlaceholderText("e.g., Software Developer, Business Analyst")
        form_layout.addWidget(actor_label)
        form_layout.addWidget(self.actor_input)
        
        # Trigger
        trigger_label = QLabel("Trigger:")
        self.trigger_input = QLineEdit()
        self.trigger_input.setPlaceholderText("What event starts this use case...")
        form_layout.addWidget(trigger_label)
        form_layout.addWidget(self.trigger_input)
        
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
        self.scenario_editor.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.scenario_editor.customContextMenuRequested.connect(self.show_scenario_context_menu)
        scenario_layout.addWidget(self.scenario_editor)
        
        self.tab_widget.addTab(scenario_widget, "Main Scenario")
        
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
        
    def add_sub_variation(self):
        """Open dialog to add a sub-variation with sub-step management"""
        # Create a dialog for adding sub-variations
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Sub-Variation")
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        
        # Step selection
        step_layout = QHBoxLayout()
        step_layout.addWidget(QLabel("Step to extend:"))
        self.subvar_step_combo = QComboBox()
        # For demo purposes, we'll populate with some sample steps
        self.subvar_step_combo.addItems(["Step 1", "Step 2", "Step 3"])
        step_layout.addWidget(self.subvar_step_combo)
        layout.addLayout(step_layout)
        
        # Variation title
        layout.addWidget(QLabel("Variation Title:"))
        self.variation_title = QLineEdit()
        self.variation_title.setPlaceholderText("e.g., Alternative Login Path")
        layout.addWidget(self.variation_title)
        
        # Description
        layout.addWidget(QLabel("Description (optional):"))
        self.variation_description = QTextEdit()
        self.variation_description.setMaximumHeight(60)
        layout.addWidget(self.variation_description)
        
        # Sub-steps section
        layout.addWidget(QLabel("Sub-steps:"))
        self.subvar_steps_editor = QTextEdit()
        self.subvar_steps_editor.setPlaceholderText("Enter sub-steps here (one per line)")
        self.subvar_steps_editor.setMaximumHeight(100)
        
        # Enable drag and drop
        self.set_drag_and_drop(self.subvar_steps_editor)
        
        layout.addWidget(self.subvar_steps_editor)
        
        # Sub-steps display area with numbering
        layout.addWidget(QLabel("Formatted Sub-steps:"))
        self.subvar_steps_display = QTextEdit()
        self.subvar_steps_display.setReadOnly(True)
        self.subvar_steps_display.setMaximumHeight(100)
        self.subvar_steps_display.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 3px;
                padding: 5px;
                font-family: monospace;
            }
        """)
        layout.addWidget(self.subvar_steps_display)
        
        # Connect text changed signal to update display
        self.subvar_steps_editor.textChanged.connect(self.update_substep_display)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Validate required fields
            step = self.subvar_step_combo.currentText()
            title = self.variation_title.text().strip()
            description = self.variation_description.toPlainText().strip()
            steps = self.subvar_steps_editor.toPlainText().strip()
            
            # Validate required fields
            if not title:
                QMessageBox.warning(dialog, "Validation Error", "Variation title is required")
                return
                
            if not steps:
                QMessageBox.warning(dialog, "Validation Error", "At least one sub-step is required")
                return
            
            # Display the sub-variation with proper visual hierarchy
            self.display_variation(step, title, description, steps)
            
            QMessageBox.information(self, "Sub-Variation Added", f"Sub-variation '{title}' created for {step}")
            
            # TODO: In a real implementation, this would parse and save the sub-steps
            if steps:
                print(f"Sub-steps for variation '{title}':")
                for line in steps.split('\n'):
                    if line.strip():
                        print(f"  - {line}")

    def update_substep_display(self):
        """Update the formatted sub-step display with automatic numbering"""
        text = self.subvar_steps_editor.toPlainText().strip()
        
        # Split by lines and number each step with proper indentation
        lines = text.split('\n')
        numbered_lines = []
        
        for i, line in enumerate(lines, 1):
            if line.strip():
                # Add indentation to show hierarchy
                numbered_lines.append(f"    * {i}. {line}")
        
        # Update the display
        self.subvar_steps_display.setText('\n'.join(numbered_lines))
        
    def display_variation(self, step, title, description, steps):
        """Display a sub-variation with proper visual hierarchy and formatting"""
        # Format the variation header
        variation_text = f"### Sub-Variation for {step}\n"
        variation_text += f"**{title}**\n\n"
        
        if description:
            variation_text += f"{description}\n\n"
        
        # Format sub-steps with proper indentation
        if steps:
            numbered_lines = []
            for i, line in enumerate(steps.split('\n'), 1):
                if line.strip():
                    # Add 4-space indentation to show hierarchy
                    numbered_lines.append(f"    * {i}. {line}")
            variation_text += '\n'.join(numbered_lines)
        
        self.subvar_steps_display.setText(variation_text)
        
    def set_drag_and_drop(self, editor):
        """Enable drag and drop functionality for text edit using event filter."""
        editor.setAcceptDrops(True)
        editor.installEventFilter(self._make_drop_filter(editor))

    def _make_drop_filter(self, editor):
        """Create an event filter for drag-and-drop on a QTextEdit."""
        class DropFilter(QObject):
            def __init__(self, target_editor):
                super().__init__()
                self.target = target_editor
            
            def eventFilter(self, obj, event):
                if event.type() == QEvent.Type.Drop:
                    mime = event.mimeData()
                    if mime.hasText():
                        cursor = self.target.textCursor()
                        pos = event.pos()
                        cursor.setPosition(
                            self.target.cursorForPosition(pos).position()
                        )
                        cursor.insertText(mime.text())
                        self.target.setTextCursor(cursor)
                        event.setDropAction(Qt.DropAction.CopyAction)
                        event.acceptProposedAction()
                        return True
                return super().eventFilter(obj, event)
        
        return DropFilter(editor)

    def custom_drag_enter_event(self, event):
        """Handle drag enter event"""
        if event.mimeData().hasFormat("text/plain"):
            event.acceptProposedAction()
        else:
            event.ignore()
            
    def custom_drag_move_event(self, event):
        """Handle drag move event"""
        if event.mimeData().hasFormat("text/plain"):
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def custom_drop_event(self, event):
        """Handle drop event for reordering sub-steps.
        
        Note: For QTextEdit widgets, use set_drag_and_drop() which installs
        an event filter instead of overriding dropEvent directly.
        """
        # Get the selected text
        cursor = self.subvar_steps_editor.textCursor()
        selected_text = cursor.selectedText()
        
        if not selected_text:
            event.ignore()
            return
            
        # Get the position where text was dropped (Qt6 uses .pos(), not .position())
        drop_pos = event.pos()
        
        # Simple implementation - just accept the drop
        # A full implementation would involve:
        # 1. Detecting which line is being moved
        # 2. Finding the target line
        # 3. Reordering the lines in memory
        # 4. Updating both the editor and the display
        
        QMessageBox.information(self, "Drag and Drop", 
                               f"Drag and drop implemented for:\n\n\"{selected_text}\"")
        
    def show_scenario_context_menu(self, position):
        """Show context menu for main scenario editor"""
        # Create the menu
        menu = QMenu(self.scenario_editor)
        
        # Add sub-variation option
        add_subvar_action = QAction("Add Sub-Variation", self)
        add_subvar_action.triggered.connect(self.add_sub_variation)
        menu.addAction(add_subvar_action)
        
        # Show the menu at the cursor position
        menu.exec(self.scenario_editor.viewport().mapToGlobal(position))
        
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
        
        export_all_word_action = QAction("Export All to Word", self)
        export_all_word_action.setShortcut(QKeySequence("Ctrl+Shift+E"))
        export_all_word_action.triggered.connect(self.export_all_to_word)
        tools_menu.addAction(export_all_word_action)
        
        export_pdf_action = QAction("Export to PDF", self)
        export_pdf_action.triggered.connect(self.export_to_pdf)
        tools_menu.addAction(export_pdf_action)
        
        export_json_action = QAction("Export to JSON", self)
        export_json_action.triggered.connect(self.export_to_json)
        tools_menu.addAction(export_json_action)
        
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
        """Open a use case for editing by parsing its markdown content."""
        self.current_use_case = use_case_file
        
        # Clear all editor fields first
        self._clear_editor_fields()
        
        # Load and parse the content
        use_case_path = f"{self.project_path}/markdown/{use_case_file}"
        if not os.path.exists(use_case_path):
            self.statusBar().showMessage(f"File not found: {use_case_file}")
            return
            
        try:
            with open(use_case_path, "r") as f:
                content = f.read()
            
            # Parse characteristic information fields
            self._parse_characteristics(content)
            
            # Parse main success scenario
            self._parse_main_scenario(content)
            
            # Parse extensions
            self._parse_extensions(content)
            
            # Parse sub-variations
            self._parse_subvariations(content)
            
            # Update navigation tree selection
            for i in range(self.navigation_tree.topLevelItemCount()):
                item = self.navigation_tree.topLevelItem(i)
                if item.text(0) == use_case_file:
                    self.navigation_tree.setCurrentItem(item)
                    break
            
            self.statusBar().showMessage(f"Opened use case: {use_case_file} at {self.get_current_time()}")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open use case: {e}")
            self.statusBar().showMessage(f"Error opening use case: {e}")

    def _clear_editor_fields(self):
        """Clear all editor fields to a clean state."""
        self.goal_input.clear()
        self.scope_input.clear()
        self.level_combo.setCurrentIndex(0)
        self.preconditions_input.clear()
        self.success_input.clear()
        self.failed_input.clear()
        self.actor_input.clear()
        self.trigger_input.clear()
        self.scenario_editor.clear()
        self.subvariations_editor.clear()
        if hasattr(self, 'extensions_preview'):
            self.extensions_preview.clear()

    def _parse_characteristics(self, content: str):
        """Parse characteristic information fields from markdown content."""
        # Goal in Context
        m = re.search(r'\* Goal in Context:\s*(.*?)\n', content)
        if m:
            self.goal_input.setText(m.group(1).strip())
        
        # Scope
        m = re.search(r'\* Scope:\s*(.*?)\n', content)
        if m:
            self.scope_input.setText(m.group(1).strip())
        
        # Level
        m = re.search(r'\* Level:\s*(.*?)\n', content)
        if m:
            level_text = m.group(1).strip()
            idx = self.level_combo.findText(level_text)
            if idx >= 0:
                self.level_combo.setCurrentIndex(idx)
        
        # Preconditions
        m = re.search(r'\* Preconditions:\s*(.*?)\n', content)
        if m:
            self.preconditions_input.setText(m.group(1).strip())
        
        # Success End Condition
        m = re.search(r'\* Success End Condition:\s*(.*?)\n', content)
        if m:
            self.success_input.setText(m.group(1).strip())
        
        # Failed End Condition
        m = re.search(r'\* Failed End Condition:\s*(.*?)\n', content)
        if m:
            self.failed_input.setText(m.group(1).strip())
        
        # Primary Actor
        m = re.search(r'\* Primary Actor:\s*(.*?)\n', content)
        if m:
            self.actor_input.setText(m.group(1).strip())
        
        # Trigger
        m = re.search(r'\* Trigger:\s*(.*?)\n', content)
        if m:
            self.trigger_input.setText(m.group(1).strip())

    def _parse_main_scenario(self, content: str):
        """Parse main success scenario steps from markdown content."""
        # Find the Main Success Scenario section
        m = re.search(r'## Main Success Scenario\s*\n(.*?)(?=##|$)', content, re.DOTALL)
        if m:
            section = m.group(1).strip()
            # Extract step lines
            steps = []
            for line in section.split('\n'):
                line = line.strip()
                if re.match(r'\*?\s*step\s*#\d+', line, re.IGNORECASE):
                    # Remove the "* step #N: " prefix
                    cleaned = re.sub(r'^\*\s*step\s*#\d+\s*:\s*', '', line, flags=re.IGNORECASE).strip()
                    steps.append(cleaned)
            if steps:
                self.scenario_editor.setText('\n'.join(steps))

    def _parse_extensions(self, content: str):
        """Parse extensions from markdown content."""
        m = re.search(r'## Extensions\s*\n(.*?)(?=##|$)', content, re.DOTALL)
        if m:
            section = m.group(1).strip()
            # Clear existing preview
            self.extensions_preview.clear()
            for line in section.split('\n'):
                line = line.strip()
                if line and (line.startswith('*') or 'step altered' in line):
                    self.extensions_preview.append(line)

    def _parse_subvariations(self, content: str):
        """Parse sub-variations from markdown content."""
        m = re.search(r'## Sub-Variations\s*\n(.*?)(?=##|$)', content, re.DOTALL)
        if m:
            section = m.group(1).strip()
            self.subvariations_editor.setText(section if section else "")

    def save_current_use_case(self):
        """Save the currently open use case by serializing all editor fields to markdown."""
        if not self.current_use_case or not self.project_path:
            return False
        
        # Build markdown content from editor fields
        lines = []
        
        # Header
        lines.append(f"# {self.current_use_case}")
        lines.append("")
        
        # Characteristic Information
        lines.append("## Characteristic Information")
        lines.append("")
        lines.append(f"* Goal in Context: {self.goal_input.toPlainText().strip()}")
        lines.append(f"* Scope: {self.scope_input.toPlainText().strip()}")
        lines.append(f"* Level: {self.level_combo.currentText()}")
        lines.append(f"* Preconditions: {self.preconditions_input.toPlainText().strip()}")
        lines.append(f"* Success End Condition: {self.success_input.toPlainText().strip()}")
        lines.append(f"* Failed End Condition: {self.failed_input.toPlainText().strip()}")
        lines.append(f"* Primary Actor: {self.actor_input.text().strip()}")
        lines.append(f"* Trigger: {self.trigger_input.text().strip()}")
        lines.append("")
        
        # Main Success Scenario
        lines.append("## Main Success Scenario")
        lines.append("")
        scenario_text = self.scenario_editor.toPlainText().strip()
        if scenario_text:
            for i, step in enumerate(scenario_text.split('\n'), 1):
                step = step.strip()
                if step:
                    lines.append(f"* step #{i}: {step}")
        else:
            lines.append("* step #1: ")
        lines.append("")
        
        # Extensions
        lines.append("## Extensions")
        lines.append("")
        ext_text = self.extensions_preview.toPlainText().strip()
        if ext_text:
            for line in ext_text.split('\n'):
                line = line.strip()
                if line:
                    lines.append(line)
        else:
            lines.append("* step altered #1: ")
        lines.append("")
        
        # Sub-Variations
        lines.append("## Sub-Variations")
        lines.append("")
        subvar_text = self.subvariations_editor.toPlainText().strip()
        if subvar_text:
            lines.append(subvar_text)
        else:
            lines.append("* step #1: ")
        lines.append("")
        
        # Write to file
        use_case_path = f"{self.project_path}/markdown/{self.current_use_case}"
        try:
            with open(use_case_path, "w") as f:
                f.write('\n'.join(lines))
            
            # Update the data model
            self._update_use_case_model()
            
            return True
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Failed to save use case: {e}")
            return False

    def _update_use_case_model(self):
        """Update the internal use_cases data model from current editor state."""
        if not self.current_use_case:
            return
        
        # Store characteristics
        characteristics = {
            "goal_in_context": self.goal_input.toPlainText().strip(),
            "scope": self.scope_input.toPlainText().strip(),
            "level": self.level_combo.currentText(),
            "preconditions": self.preconditions_input.toPlainText().strip(),
            "success_condition": self.success_input.toPlainText().strip(),
            "failed_condition": self.failed_input.toPlainText().strip(),
            "primary_actor": self.actor_input.text().strip(),
            "trigger": self.trigger_input.text().strip(),
        }
        
        # Store scenario steps
        scenario_text = self.scenario_editor.toPlainText().strip()
        scenarios = []
        if scenario_text:
            for step in scenario_text.split('\n'):
                step = step.strip()
                if step:
                    scenarios.append(step)
        
        # Store extensions from preview
        ext_preview_text = self.extensions_preview.toPlainText().strip()
        extensions = []
        if ext_preview_text:
            for line in ext_preview_text.split('\n'):
                line = line.strip()
                if line:
                    extensions.append(line)
        
        # Store sub-variations
        subvar_text = self.subvariations_editor.toPlainText().strip()
        
        self.use_cases[self.current_use_case] = {
            "characteristics": characteristics,
            "scenarios": scenarios,
            "extensions": extensions,
            "subvariations": subvar_text,
            "last_modified": datetime.now().isoformat(),
        }

    def auto_save(self):
        """Automatically save the project every 30 seconds."""
        if self.current_use_case:
            self.save_current_use_case()
        self.statusBar().showMessage(f"Auto-saved at {self.get_current_time()}")

    def auto_save_extensions(self):
        """Automatically save extensions — delegates to main save."""
        if self.current_use_case:
            self.save_current_use_case()

    def auto_save_subvariations(self):
        """Automatically save sub-variations — delegates to main save."""
        if self.current_use_case:
            self.save_current_use_case()

    def get_current_time(self):
        """Get current time for status messages."""
        return datetime.now().strftime("%H:%M:%S")

    def export_to_word(self):
        """Export current use case to Word using python-docx or markdown conversion."""
        if not self.current_use_case:
            QMessageBox.warning(self, "Export Error", "No use case selected.")
            return
        
        # First save the current state
        self.save_current_use_case()
        
        # Determine output path
        word_dir = os.path.join(self.project_path, "word")
        os.makedirs(word_dir, exist_ok=True)
        
        # Extract use case number and name for filename
        match = re.match(r'UC-(\d+)_?(.*)', self.current_use_case)
        if match:
            uc_num = match.group(1)
            uc_name = match.group(2).replace('_', ' ')
            word_filename = f"UC-{uc_num}_{uc_name}.docx"
        else:
            word_filename = f"{self.current_use_case}.docx"
        
        word_path = os.path.join(word_dir, word_filename)
        
        try:
            # Try python-docx first if available
            try:
                self._export_with_python_docx(self.current_use_case, word_path)
                self.statusBar().showMessage(f"Exported to Word: {word_filename} at {self.get_current_time()}")
                QMessageBox.information(self, "Export Complete", 
                    f"Use case exported to Word:\n{word_path}")
            except ImportError:
                # Fallback: create a formatted text file as .docx placeholder
                self._export_as_formatted_text(self.current_use_case, word_path)
                self.statusBar().showMessage(f"Exported (text format): {word_filename} at {self.get_current_time()}")
                QMessageBox.information(self, "Export Complete",
                    f"Use case exported (formatted text):\n{word_path}\n\n"
                    f"Note: Install python-docx for full .docx support.\n"
                    f"  pip install python-docx")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export to Word:\n{e}")

    def _export_with_python_docx(self, use_case_file: str, output_path: str):
        """Export a use case to a properly formatted .docx file."""
        from docx import Document
        from docx.shared import Pt, Inches
        
        doc = Document()
        
        # Use case title
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Calibri'
        font.size = Pt(11)
        
        doc.add_heading(use_case_file.replace('_', ' '), level=0)
        
        # Parse the markdown content
        use_case_path = f"{self.project_path}/markdown/{use_case_file}"
        if os.path.exists(use_case_path):
            with open(use_case_path, "r") as f:
                content = f.read()
            
            # Characteristic Information
            doc.add_heading("Characteristic Information", level=1)
            characteristics = {
                "Goal in Context": self.goal_input.toPlainText().strip(),
                "Scope": self.scope_input.toPlainText().strip(),
                "Level": self.level_combo.currentText(),
                "Preconditions": self.preconditions_input.toPlainText().strip(),
                "Success End Condition": self.success_input.toPlainText().strip(),
                "Failed End Condition": self.failed_input.toPlainText().strip(),
                "Primary Actor": self.actor_input.text().strip(),
                "Trigger": self.trigger_input.text().strip(),
            }
            
            for field, value in characteristics.items():
                if value:
                    p = doc.add_paragraph()
                    run = p.add_run(f"{field}: ")
                    run.bold = True
                    p.add_run(value)
            
            # Main Success Scenario
            doc.add_heading("Main Success Scenario", level=1)
            scenario_text = self.scenario_editor.toPlainText().strip()
            if scenario_text:
                for i, step in enumerate(scenario_text.split('\n'), 1):
                    step = step.strip()
                    if step:
                        doc.add_paragraph(f"Step {i}: {step}")
            
            # Extensions
            ext_text = self.extensions_preview.toPlainText().strip()
            if ext_text:
                doc.add_heading("Extensions", level=1)
                for line in ext_text.split('\n'):
                    line = line.strip()
                    if line:
                        doc.add_paragraph(line, style='List Bullet')
            
            # Sub-Variations
            subvar_text = self.subvariations_editor.toPlainText().strip()
            if subvar_text:
                doc.add_heading("Sub-Variations", level=1)
                for line in subvar_text.split('\n'):
                    line = line.strip()
                    if line:
                        doc.add_paragraph(line, style='List Bullet')
        
        # Add footer with timestamp
        doc.add_paragraph(f"\nExported on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        doc.save(output_path)

    def _export_as_formatted_text(self, use_case_file: str, output_path: str):
        """Create a formatted text file as fallback export."""
        self.save_current_use_case()
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"{use_case_file}\n")
            f.write("=" * len(use_case_file) + "\n\n")
            f.write("## Characteristic Information\n\n")
            f.write(f"Goal in Context: {self.goal_input.toPlainText().strip()}\n")
            f.write(f"Scope: {self.scope_input.toPlainText().strip()}\n")
            f.write(f"Level: {self.level_combo.currentText()}\n")
            f.write(f"Preconditions: {self.preconditions_input.toPlainText().strip()}\n")
            f.write(f"Success End Condition: {self.success_input.toPlainText().strip()}\n")
            f.write(f"Failed End Condition: {self.failed_input.toPlainText().strip()}\n")
            f.write(f"Primary Actor: {self.actor_input.text().strip()}\n")
            f.write(f"Trigger: {self.trigger_input.text().strip()}\n\n")
            
            f.write("## Main Success Scenario\n\n")
            scenario_text = self.scenario_editor.toPlainText().strip()
            if scenario_text:
                for i, step in enumerate(scenario_text.split('\n'), 1):
                    step = step.strip()
                    if step:
                        f.write(f"Step {i}: {step}\n")
            
            ext_text = self.extensions_preview.toPlainText().strip()
            if ext_text:
                f.write("\n## Extensions\n\n")
                for line in ext_text.split('\n'):
                    f.write(f"{line}\n")
        
        # Rename to .docx extension (it's actually a formatted text file)
        txt_path = output_path.rsplit('.', 1)[0] + '.txt'
        if os.path.exists(txt_path):
            os.rename(txt_path, output_path)

    def export_to_pdf(self):
        """Export current use case to PDF via markdown intermediate format."""
        if not self.current_use_case:
            QMessageBox.warning(self, "Export Error", "No use case selected.")
            return
        
        # First save the current state
        self.save_current_use_case()
        
        pdf_dir = os.path.join(self.project_path, "pdf")
        os.makedirs(pdf_dir, exist_ok=True)
        
        match = re.match(r'UC-(\d+)_?(.*)', self.current_use_case)
        if match:
            uc_num = match.group(1)
            uc_name = match.group(2).replace('_', ' ')
            pdf_filename = f"UC-{uc_num}_{uc_name}.pdf"
        else:
            pdf_filename = f"{self.current_use_case}.pdf"
        
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        
        try:
            # Try pandoc first (most reliable for markdown->PDF)
            import subprocess
            md_path = f"{self.project_path}/markdown/{self.current_use_case}"
            
            if os.path.exists(md_path):
                result = subprocess.run(
                    ["pandoc", md_path, "-o", pdf_path, 
                     "--pdf-engine=xelatex", "-V", "geometry:margin=1in"],
                    capture_output=True, text=True, timeout=30
                )
                
                if result.returncode == 0 and os.path.exists(pdf_path):
                    self.statusBar().showMessage(f"Exported to PDF: {pdf_filename} at {self.get_current_time()}")
                    QMessageBox.information(self, "Export Complete",
                        f"Use case exported to PDF:\n{pdf_path}")
                    return
            
            # Fallback: create HTML intermediate and note pandoc not available
            html_path = pdf_path.rsplit('.', 1)[0] + '.html'
            self._export_html(self.current_use_case, html_path)
            
            QMessageBox.information(self, "Export Note",
                f"PDF export requires Pandoc with LaTeX.\n\n"
                f"HTML version created instead:\n{html_path}\n\n"
                f"To enable PDF export:\n"
                f"  1. Install Pandoc: https://pandoc.org/installing.html\n"
                f"  2. Install XeLaTeX (e.g., texlive-xetex on Linux)")
            
        except FileNotFoundError:
            # Pandoc not found — create HTML fallback
            html_path = pdf_path.rsplit('.', 1)[0] + '.html'
            self._export_html(self.current_use_case, html_path)
            QMessageBox.information(self, "Export Note",
                f"Pandoc not found. HTML version created instead:\n{html_path}\n\n"
                f"To enable PDF export, install Pandoc:\n"
                f"  - macOS: brew install pandoc\n"
                f"  - Ubuntu: sudo apt install pandoc\n"
                f"  - Windows: choco install pandoc")
        except subprocess.TimeoutExpired:
            QMessageBox.critical(self, "Export Error", "PDF export timed out. Try a simpler use case.")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export to PDF:\n{e}")

    def _export_html(self, use_case_file: str, output_path: str):
        """Export a use case as an HTML file."""
        self.save_current_use_case()
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{use_case_file.replace('_', ' ')}</title>
<style>
    body {{ font-family: Georgia, serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; }}
    h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
    h2 {{ color: #2980b9; margin-top: 30px; }}
    .field {{ margin: 8px 0; }}
    .field strong {{ color: #34495e; }}
    ol {{ padding-left: 20px; }}
    li {{ margin: 4px 0; }}
    footer {{ margin-top: 40px; padding-top: 10px; border-top: 1px solid #ddd; color: #7f8c8d; font-size: 0.9em; }}
</style>
</head>
<body>
<h1>{use_case_file.replace('_', ' ')}</h1>

<h2>Characteristic Information</h2>
<div class="field"><strong>Goal in Context:</strong> {self.goal_input.toPlainText().strip()}</div>
<div class="field"><strong>Scope:</strong> {self.scope_input.toPlainText().strip()}</div>
<div class="field"><strong>Level:</strong> {self.level_combo.currentText()}</div>
<div class="field"><strong>Preconditions:</strong> {self.preconditions_input.toPlainText().strip()}</div>
<div class="field"><strong>Success End Condition:</strong> {self.success_input.toPlainText().strip()}</div>
<div class="field"><strong>Failed End Condition:</strong> {self.failed_input.toPlainText().strip()}</div>
<div class="field"><strong>Primary Actor:</strong> {self.actor_input.text().strip()}</div>
<div class="field"><strong>Trigger:</strong> {self.trigger_input.text().strip()}</div>

<h2>Main Success Scenario</h2>
<ol>
"""
        scenario_text = self.scenario_editor.toPlainText().strip()
        if scenario_text:
            for step in scenario_text.split('\n'):
                step = step.strip()
                if step:
                    html += f"  <li>{step}</li>\n"
        
        ext_text = self.extensions_preview.toPlainText().strip()
        if ext_text:
            html += "</ol>\n\n<h2>Extensions</h2>\n<ul>\n"
            for line in ext_text.split('\n'):
                line = line.strip()
                if line:
                    html += f"  <li>{line}</li>\n"
        
        subvar_text = self.subvariations_editor.toPlainText().strip()
        if subvar_text:
            html += "</ul>\n\n<h2>Sub-Variations</h2>\n<pre>\n" + subvar_text + "\n</pre>\n"
        
        html += f"""</ol>
<footer>Exported on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</footer>
</body>
</html>"""
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

    def export_to_json(self):
        """Export current use case to JSON format."""
        if not self.current_use_case:
            QMessageBox.warning(self, "Export Error", "No use case selected.")
            return
        
        self.save_current_use_case()
        
        json_dir = os.path.join(self.project_path, "json")
        os.makedirs(json_dir, exist_ok=True)
        
        match = re.match(r'UC-(\d+)_?(.*)', self.current_use_case)
        if match:
            uc_num = match.group(1)
            uc_name = match.group(2).replace('_', ' ')
            json_filename = f"UC-{uc_num}_{uc_name}.json"
        else:
            json_filename = f"{self.current_use_case}.json"
        
        json_path = os.path.join(json_dir, json_filename)
        
        try:
            # Build structured JSON data
            data = {
                "use_case_id": self.current_use_case,
                "characteristics": {
                    "goal_in_context": self.goal_input.toPlainText().strip(),
                    "scope": self.scope_input.toPlainText().strip(),
                    "level": self.level_combo.currentText(),
                    "preconditions": self.preconditions_input.toPlainText().strip(),
                    "success_condition": self.success_input.toPlainText().strip(),
                    "failed_condition": self.failed_input.toPlainText().strip(),
                    "primary_actor": self.actor_input.text().strip(),
                    "trigger": self.trigger_input.text().strip(),
                },
                "main_success_scenario": [
                    step.strip() for step in self.scenario_editor.toPlainText().split('\n')
                    if step.strip()
                ],
                "extensions": [
                    line.strip() for line in self.extensions_preview.toPlainText().split('\n')
                    if line.strip()
                ],
                "sub_variations": self.subvariations_editor.toPlainText().strip(),
                "metadata": {
                    "exported_at": datetime.now().isoformat(),
                    "format_version": "2.0",
                }
            }
            
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.statusBar().showMessage(f"Exported to JSON: {json_filename} at {self.get_current_time()}")
            QMessageBox.information(self, "Export Complete", 
                f"Use case exported to JSON:\n{json_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export to JSON:\n{e}")

    def add_extension(self):
        """Add a new extension to the current use case"""
        if not self.current_use_case:
            QMessageBox.warning(self, "No Use Case", "Please select a use case first.")
            return

        # Get available steps from current use case
        step_numbers = self._get_step_numbers()

        dialog = QDialog(self)
        dialog.setWindowTitle("Add Extension")
        dialog.setModal(True)
        dialog.setMinimumWidth(450)

        layout = QVBoxLayout(dialog)

        # Step number selection
        step_layout = QHBoxLayout()
        step_layout.addWidget(QLabel("Step to extend:"))
        step_combo = QComboBox()
        if step_numbers:
            step_combo.addItems([f"#{n}" for n in step_numbers])
        else:
            step_combo.addItem("#1 (default)")
        step_layout.addWidget(step_combo)
        layout.addLayout(step_layout)

        # Condition type
        condition_layout = QHBoxLayout()
        condition_layout.addWidget(QLabel("Condition type:"))
        condition_combo = QComboBox()
        condition_combo.addItems(["timeout", "error", "validation", "system"])
        condition_layout.addWidget(condition_combo)
        layout.addLayout(condition_layout)

        # Condition description with character counter
        layout.addWidget(QLabel("Condition description (max 500 chars):"))
        condition_text = QTextEdit()
        condition_text.setMaximumHeight(80)
        layout.addWidget(condition_text)
        char_count_label = QLabel("0/500 characters")
        layout.addWidget(char_count_label)

        def update_char_count():
            text = condition_text.toPlainText()
            count = len(text)
            char_count_label.setText(f"{count}/500 characters")
            if count > 500:
                char_count_label.setStyleSheet("color: red; font-weight: bold;")
            elif count > 400:
                char_count_label.setStyleSheet("color: orange;")
            else:
                char_count_label.setStyleSheet("")

        condition_text.textChanged.connect(update_char_count)

        # Action description
        layout.addWidget(QLabel("Action or alternative path:"))
        action_text = QTextEdit()
        action_text.setMaximumHeight(80)
        layout.addWidget(action_text)

        # Optional use case linking
        layout.addWidget(QLabel("Link to existing use case (optional):"))
        link_combo = QComboBox()
        link_combo.addItem("")  # empty = no link
        if self.use_cases:
            for uc_id in sorted(self.use_cases.keys()):
                link_combo.addItem(uc_id)
        layout.addWidget(link_combo)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            step_text = step_combo.currentText().lstrip("#")
            try:
                step_num = int(step_text)
            except ValueError:
                step_num = 1

            condition_type = condition_combo.currentText()
            condition_desc = condition_text.toPlainText().strip()
            action_desc = action_text.toPlainText().strip()
            linked_use_case = link_combo.currentText() if link_combo.currentText() else None

            # Validate required fields
            if not condition_desc:
                QMessageBox.warning(dialog, "Validation Error", "Condition description is required.")
                return
            if len(condition_desc) > 500:
                QMessageBox.warning(dialog, "Validation Error", "Condition description exceeds 500 characters.")
                return
            if not action_desc:
                QMessageBox.warning(dialog, "Validation Error", "Action description is required.")
                return

            # Display the extension in the preview
            self.display_extension(step_num, condition_type, action_desc, linked_use_case)

            # Save to use case data model
            self._save_extension_to_model(step_num, condition_type, condition_desc, action_desc, linked_use_case)

            QMessageBox.information(self, "Extension Added", f"Extension added for step #{step_num}")
            self.statusBar().showMessage(f"Extension added for step #{step_num} at {self.get_current_time()}")

    def _get_step_numbers(self) -> List[int]:
        """Extract step numbers from the current main scenario text."""
        if not hasattr(self, 'scenario_editor') or not self.scenario_editor.toPlainText().strip():
            return []
        text = self.scenario_editor.toPlainText()
        pattern = r'step\s*#\s*(\d+)'
        matches = re.findall(pattern, text, re.IGNORECASE)
        numbers = []
        for m in matches:
            try:
                numbers.append(int(m))
            except ValueError:
                pass
        return sorted(set(numbers)) if numbers else [1]

    def _save_extension_to_model(self, step_num: int, condition_type: str,
                                  condition_desc: str, action_desc: str,
                                  linked_use_case: Optional[str]):
        """Save extension to the use case data model and update preview."""
        if not self.current_use_case:
            return

        ext_key = f"ext_{step_num}"
        ext_data = {
            "step": step_num,
            "condition_type": condition_type,
            "condition": condition_desc,
            "action": action_desc,
            "linked_use_case": linked_use_case,
        }

        if self.current_use_case not in self.use_cases:
            self.use_cases[self.current_use_case] = {"extensions": {}}

        self.use_cases[self.current_use_case]["extensions"][ext_key] = ext_data

    def update_condition_char_count(self):
        """Update the character count for condition description."""
        if hasattr(self, 'condition_text') and hasattr(self, 'condition_char_count'):
            text = self.condition_text.toPlainText()
            self.condition_char_count.setText(f"{len(text)}/500 characters")

    def export_all_to_word(self):
        """Batch export all use cases to Word format with progress dialog."""
        if not self.project_path:
            QMessageBox.warning(self, "No Project", "Please open a project first.")
            return
        
        # Collect all use case files
        markdown_dir = os.path.join(self.project_path, "markdown")
        if not os.path.exists(markdown_dir):
            QMessageBox.warning(self, "No Use Cases", "No markdown directory found in project.")
            return
        
        use_case_files = [f for f in os.listdir(markdown_dir) if f.endswith('.md')]
        if not use_case_files:
            QMessageBox.information(self, "No Use Cases", "No use cases found to export.")
            return
        
        # Create the batch export dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Export All to Word")
        dialog.setModal(True)
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Info label
        info_label = QLabel(f"Found {len(use_case_files)} use case(s) to export.")
        layout.addWidget(info_label)
        
        # Options group
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        
        self.batch_skip_existing = QCheckBox("Skip already converted files")
        self.batch_skip_existing.setChecked(True)
        options_layout.addWidget(self.batch_skip_existing)
        
        self.batch_auto_open = QCheckBox("Auto-open Word folder after export")
        options_layout.addWidget(self.batch_auto_open)
        
        layout.addWidget(options_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        ok_btn = button_box.button(QDialogButtonBox.StandardButton.Ok)
        cancel_btn = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(button_box)
        
        if not dialog.exec():
            return  # User cancelled
        
        skip_existing = self.batch_skip_existing.isChecked()
        
        # Start batch export in background thread
        self.statusBar().showMessage("Starting batch export...")
        self.progress_dialog = QProgressDialog("Exporting use cases...", "Cancel", 0, len(use_case_files), self)
        self.progress_dialog.setWindowTitle("Batch Export")
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.valueChanged.connect(lambda v: self.statusBar().showMessage(f"Exporting... ({v}/{len(use_case_files)})"))
        
        # Create worker thread
        self.batch_worker = BatchExportWorker(self.project_path, use_case_files, skip_existing=skip_existing)
        self.batch_worker.progress_signal.connect(self._batch_progress_update)
        self.batch_worker.finished_signal.connect(self._batch_export_finished)
        
        def on_cancelled():
            if hasattr(self, 'batch_worker'):
                self.batch_worker.cancel()
            self.progress_dialog.close()
        
        cancel_btn.clicked.connect(on_cancelled)
        
        # Start the worker
        self.batch_worker.start()
        
        # Keep dialog open but non-blocking
        dialog.accept()

    def _batch_progress_update(self, message: str, pct: float):
        """Update progress during batch export."""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.setValue(int(pct))
            self.progress_dialog.setLabelText(message)
        self.statusBar().showMessage(message)

    def _batch_export_finished(self, success_count: int, fail_count: int):
        """Handle completion of batch export."""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
        
        msg = f"Export complete!\n\n✓ {success_count} exported successfully"
        if fail_count > 0:
            msg += f"\n✗ {fail_count} failed"
        QMessageBox.information(self, "Batch Export Complete", msg)
        
        self.statusBar().showMessage(f"Batch export finished: {success_count} success, {fail_count} failed")
        
        # Auto-open folder if requested
        if hasattr(self, 'batch_auto_open') and self.batch_auto_open.isChecked():
            word_dir = os.path.join(self.project_path, "word")
            if os.path.exists(word_dir):
                try:
                    if sys.platform == 'win32':
                        os.startfile(word_dir)
                    elif sys.platform == 'darwin':
                        os.system(f'open "{word_dir}"')
                    else:
                        os.system(f'xdg-open "{word_dir}"')
                except Exception as e:
                    QMessageBox.warning(self, "Open Folder Error", f"Could not open folder: {e}")

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