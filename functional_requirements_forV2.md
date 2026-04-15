# Cockburn Specification Generator - V2: Functional Requirements Document

## Document Overview

**Version:** 1.0  
**Date:** 2026-04-15  
**Target Audience:** Product Owner, Development Team, QA Team  
**Status:** Draft  

---

## 1. Introduction

### 1.1 Purpose
This document outlines the functional requirements for a modern, Python-based graphical user interface (GUI) version of the Cockburn Specification Generator. The goal is to transform the current command-line bash script into an intuitive desktop application with enhanced features, better UX, and expanded capabilities.

### 1.2 Scope
This document covers all functional requirements for V2 of the Cockburn Specification Generator, including:
- GUI interface design and interaction patterns
- Core use case generation workflow
- File management (import, export, save)
- Collaboration and version control integration
- Reporting and analysis tools

### 1.3 Target Users
- Software development teams
- Business analysts
- Product managers
- Technical writers

---

## 2. User Interface Requirements

### 2.1 Platform Support
- **Desktop Applications:**
  - Windows 10/11 (x64)
  - macOS 12+ (Intel and Apple Silicon)
  - Linux (Ubuntu 20.04+, Debian, Fedora, Arch)

- **GUI Framework Selection:** PyQt6 or PySide6 (preferred for modern look and professional feel)

### 2.2 Main Window Layout

#### 2.2.1 Menu Bar
```
File              Edit              View              Tools             Help
|                 |                 |                 |
New Use Case      Add Section       Toggle Sidebar    Import Templates  About
Open Project      Save Project      Zoom In/Out       Export All to PDF  Keyboard Shortcuts
Save As...        Copy              Reset View        Convert to Word   Keyboard Shortcuts
Close             Paste             Toggle Fullscreen Generate Batch Reports Exit
Exit              Clear All                          Check for Updates
```

#### 2.2.2 Toolbar
- [ ] New Use Case Button (plus icon)
- [ ] Open Project Button (folder icon)
- [ ] Save Project Button (floppy icon)
- [ ] Import Templates Button (file icon)
- [ ] Export to Word Button
- [ ] Export to PDF Button
- [ ] Preview Toggle Button (eye icon)
- [ ] Zoom Controls (+, -, 100%)
- [ ] Fullscreen Toggle

#### 2.2.3 Main Content Area - Three-Pane Layout

**Left Pane - Use Case Navigator:**
- Tree view of all use cases organized by project
- Sortable columns: Name, Number, Date Created, Last Modified
- Search and filter functionality
- Quick actions: Add, Rename, Delete, Export individual use case
- Context menu with actions based on selection

**Center Pane - Editor:**
- Rich text editor for specification content
- Collapsible sections for: Characteristic Information, Main Success Scenario, Extensions, Sub-variations
- Auto-save indicator
- Real-time validation warnings (red highlight, tooltip)
- Undo/Redo support (Ctrl+Z / Ctrl+Y)
- Line numbers display
- Tab size configuration

**Right Pane - Properties & Preview:**
- **Properties Panel:**
  - Edit characteristic information fields
  - Set use case metadata (priority, performance targets, frequency)
  - Add related use cases and secondary actors
  - Link to sub-use cases
  
- **Preview Panel:**
  - Live preview of Markdown rendering
  - Print/Export view
  - PDF generation preview
  - Copy to clipboard button

#### 2.2.4 Status Bar
- Current use case name and number
- Auto-save status indicator
- Validation warnings count
- Keyboard shortcut hints (e.g., "Ctrl+S to save")
- User account/status

### 2.3 Dialog Windows

#### 2.3.1 New Use Case Dialog
**Fields:**
- Use Case Name (text input, required)
- Auto-numbering checkbox (default: checked)
- Category/Project tag selector
- Template selection dropdown
- Create button
- Cancel button

#### 2.3.2 Save Project Dialog
**Options:**
- Project name input
- Project location browser
- Include metadata checkbox
- Compress project option
- Save and Close button

#### 2.3.3 Settings/Preferences Dialog
**Tabs:**
- **General:**
  - Language preference (English, French)
  - Auto-save interval (5 min, 10 min, 15 min, disabled)
  - Default export format
  - Theme selection (Light, Dark, System)

- **Editor:**
  - Font family and size
  - Tab size (2, 4, 8 spaces)
  - Line numbers toggle
  - Word wrap toggle
  - Syntax highlighting colors

- **Templates:**
  - Custom template management
  - Default template selector
  - Edit template button
  - Import template from file

- **Export:**
  - Default Word template path
  - PDF settings (page size, margins)
  - Auto-conversion on save option

---

## 3. Core Functional Requirements

### 3.1 Use Case Creation Workflow

#### CR-001: Create New Use Case
**Priority:** High  
**Type:** Feature  

**Description:** User creates a new use case specification using the GUI.

**Functionality:**
1. User clicks "New Use Case" button or presses Ctrl+N
2. Application displays New Use Case dialog
3. User enters use case name and optionally selects template
4. User reviews suggested filename with auto-numbering
5. User confirms creation
6. Editor pane opens with empty characteristic information form
7. Cursor focuses on first field for quick entry

**Acceptance Criteria:**
- [ ] New use case appears in the left navigation tree
- [ ] Filename format: `UC-{number}_{name}` (e.g., UC-01_PayInvoice)
- [ ] Creation timestamp is automatically set
- [ ] Use case number increments based on existing files
- [ ] Empty project creates first use case as UC-001
- [ ] Project already has 100 use cases, next is UC-101

**Data Validation:**
- Use case name cannot be empty
- Use case name must not contain special characters (except underscores, spaces, hyphens)
- Name maximum length: 100 characters

---

#### CR-002: Edit Characteristic Information
**Priority:** High  
**Type:** Feature  

**Description:** User can view and edit all characteristic information fields.

**Functionality:**
1. Left navigation tree allows selection of any use case
2. Center editor shows Characteristic Information section as form with 8 required fields:
   - Goal in Context (text area, multiline)
   - Scope (text input)
   - Level (dropdown: Summary, Primary Task, Subfunction)
   - Preconditions (text area)
   - Success End Condition (text area)
   - Failed End Condition (text area)
   - Primary Actor (text input)
   - Trigger (text input)

3. Each field has:
   - Help tooltip with definition
   - Validation error messages
   - Suggested values based on context

4. User can click on any field to edit inline or via dialog

**Acceptance Criteria:**
- [ ] All fields are visible and editable
- [ ] Field order matches Cockburn standard
- [ ] Changes auto-save after 2 seconds of inactivity
- [ ] Validation prevents saving invalid data
- [ ] Help tooltips accessible on hover
- [ ] Required fields marked with asterisk (*)

**Data Constraints:**
- Level must be one of the three predefined values
- All fields have maximum character limits (Goal in Context: 1000, others: 500)
- Primary Actor accepts multiple roles separated by commas

---

#### CR-003: Main Success Scenario Editing
**Priority:** High  
**Type:** Feature  

**Description:** User creates and edits step-by-step main success scenario.

**Functionality:**
1. Editor displays "Main Success Scenario" section
2. Each step is displayed as:
   ```
   * step #1: [step text]
   ```
3. User can:
   - Add new steps (type step text, press Enter or click "+")
   - Delete steps (right-click → Remove)
   - Reorder steps (drag and drop or move buttons)
   - Edit existing steps (double-click or F2)
   - Insert blank line between steps for readability
   - Set step numbering style (#1, 1., 1)

4. Step validation:
   - Each step must be descriptive and testable
   - Empty steps are not allowed
   - Step numbers must be sequential without gaps

5. Auto-creation of numbered steps when adding new content

**Acceptance Criteria:**
- [ ] New step appends with next sequential number
- [ ] Step text wraps at 80 characters in editor
- [ ] Steps maintain relative order during reordering
- [ ] Cannot delete last remaining step (minimum 1 required)
- [ ] Changes to steps auto-save after 3 seconds
- [ ] Undo/Redo works for step edits

**User Experience:**
- Visual indicator showing current step position in scenario flow
- Step validation icon (green checkmark for valid, yellow warning)
- "Show/hide step numbers" toggle in toolbar

---

#### CR-004: Extensions Management
**Priority:** High  
**Type:** Feature  

**Description:** User can define alternative paths and error conditions that extend main success scenario steps.

**Functionality:**
1. Extension section displayed as list:
   ```
   * ***step altered #3*** > PaymentGatewayTimeout : Retry or offer alternative
   ```

2. User can:
   - Add extensions to existing steps
   - Define extension names/descriptions
   - Link extensions to sub-use cases
   - Edit existing extensions
   - Delete extensions
   - Import/export extension lists

3. Extension dialog fields:
   - Step number (dropdown or input, auto-completes from scenario)
   - Condition type (dropdown: timeout, error, validation, system)
   - Condition description (text area)
   - Action/Alternative path (text area)
   - Link to existing use case (dropdown, optional)

4. Visual indicators:
   - Color-coded condition types
   - Step numbers highlighted in extensions
   - Link icon for sub-use cases

**Acceptance Criteria:**
- [ ] Extension must reference an existing valid step number
- [ ] Cannot create extension without referencing a step
- [ ] Duplicate step references are prevented
- [ ] Auto-save after completing extension entry
- [ ] Extensions visible in preview pane
- [ ] Export all extensions to separate file (UC-{name}_extensions.json)

**Data Constraints:**
- Extension descriptions limited to 500 characters
- Each step can have multiple extensions
- Extensions must follow "step altered #X" format

---

#### CR-005: Sub-variations Management
**Priority:** Medium  
**Type:** Feature  

**Description:** User defines alternative branches and edge cases that bifurcate the main success scenario.

**Functionality:**
1. Sub-variations section displayed with step hierarchy:
   ```
   * ***step#2 [SOUS-VARIATION]***
      * step #1: Credit Card (via Stripe)
      * step #2: Bank Transfer
   ```

2. User can:
   - Create sub-variations for specific steps
   - Add multiple sub-steps per variation
   - Nest variations within variations (optional)
   - Delete individual sub-steps
   - Reorder variations

3. Sub-variation creation dialog:
   - Step number to modify (dropdown)
   - Variation title (text input)
   - Add sub-step button
   - Delete variation button

4. Visual representation:
   - Indentation indicates hierarchy
   - Variation header highlighted
   - Numbered sub-steps with prefix "step #" and sequential numbering

**Acceptance Criteria:**
- [ ] Must select existing step to create sub-variation for
- [ ] Each variation must have at least one sub-step
- [ ] Cannot delete last remaining sub-step of a variation
- [ ] Auto-save after completing all sub-steps
- [ ] Sub-variations show in preview pane
- [ ] Preview highlights which steps are variations

**User Experience:**
- "Show/hide sub-variations" toggle
- "Expand all / Collapse all" buttons for step sections
- Visual connection lines in preview (optional)

---

#### CR-006: Related Information Fields
**Priority:** Low  
**Type:** Feature  

**Description:** User can add and edit optional related information fields.

**Fields:**
- Priority (dropdown: Critical, High, Medium, Low)
- Performance Target (text input with time unit)
- Frequency (text input)
- Superordinate Use Case (text input with autocomplete from project use cases)
- Subordinate Use Cases (text input, multiple entries)
- Channel to Primary Actor (dropdown/ text)
- Secondary Actors (text input, multiple entries)
- Channel to Secondary Actors (dropdown/ text)

**Functionality:**
1. Related Information section displayed in editor
2. All fields collapsible or expandable in properties panel
3. Validation rules:
   - Priority must be one of four values
   - Performance Target accepts formats like "30s", "5 min", "1 hour"
   - Superordinate Use Case auto-completes from existing use cases

**Acceptance Criteria:**
- [ ] All fields are optional
- [ ] Auto-save after field modification
- [ ] Dropdowns with autocomplete suggestions
- [ ] Multiple values supported for some fields
- [ ] Fields saved to project metadata file

---

### 3.2 File Management Functions

#### CR-007: Open Existing Project
**Priority:** High  
**Type:** Feature  

**Description:** User opens a previously saved project.

**Functionality:**
1. Click "Open Project" or Ctrl+O
2. File dialog shows .cpz (Cockburn Project ZIP) files
3. Application loads all use cases from project file
4. Project metadata restored (last modified dates, statistics)
5. Left navigation tree populates with use case hierarchy

**Acceptance Criteria:**
- [ ] Opens project directory structure or ZIP file
- [ ] All Markdown files loaded from project
- [ ] Project metadata file (metadata.json) parsed successfully
- [ ] Last opened position and cursor location restored
- [ ] Undo/Redo stack preserved if possible

**Project Structure:**
```
project.cpz/
├── metadata.json
├── markdown/
│   ├── UC-001_PayInvoice.md
│   ├── UC-002_CreateInvoice.md
│   └── ...
└── word/
    ├── UC-001_PayInvoice.docx
    └── ...
```

**Metadata JSON Format:**
```json
{
  "project_name": "Customer Portal System",
  "created_date": "2026-04-15",
  "last_modified": "2026-04-15T12:30:00",
  "use_case_count": 3,
  "version": "2.0"
}
```

---

#### CR-008: Save Project
**Priority:** High  
**Type:** Feature  

**Description:** User saves the current project state.

**Functionality:**
1. Automatic save on user idle after 30 seconds
2. Manual save via File → Save or Ctrl+S
3. Projects saved as .cpz (ZIP archive with embedded metadata)
4. Version control integration (optional)

**Acceptance Criteria:**
- [ ] All Markdown files saved to project directory
- [ ] Project metadata JSON updated with current date/time
- [ ] Last use case file shows "Saved" indicator in status bar
- [ ] File size remains reasonable (<50MB for typical projects)
- [ ] Save progress shown if project is large

**User Experience:**
- Auto-save indicator in status bar (blinking or subtle)
- Toast notification on manual save
- "Auto-saved at: 12:30 PM" message
- Conflict resolution dialog if file has been modified externally

---

#### CR-009: Export to Word (.docx)
**Priority:** High  
**Type:** Feature  

**Description:** User exports a single use case specification to Word format.

**Functionality:**
1. Select use case in navigation tree
2. Right-click → "Export to Word" or toolbar button
3. Application uses Pandoc or python-docx to convert Markdown to .docx
4. Applied document styling from template
5. Automatic file generation in ./word/ directory

**Acceptance Criteria:**
- [ ] Converts Markdown to properly formatted Word document
- [ ] Applies default Word styling (headings, lists)
- [ ] Document includes metadata (creation date, use case name)
- [ ] Supports Unicode characters correctly
- [ ] File named as `UC-{number}_{name}.docx`
- [ ] Conversion progress shown if document is complex

**Styling Template:**
```css
/* Word document styles generated from template */
h1 { font-size: 24pt; font-weight: bold; color: #333; margin-bottom: 12pt; }
h2 { font-size: 18pt; font-weight: bold; color: #555; margin-top: 16pt; }
h3 { font-size: 14pt; font-weight: bold; color: #777; margin-top: 12pt; }
p { font-size: 11pt; line-height: 1.6; margin-bottom: 8pt; }
ul { list-style-type: disc; margin-left: 24pt; padding-left: 8pt; }
strong { font-weight: bold; color: #333; }
```

---

#### CR-010: Export All to Word
**Priority:** Medium  
**Type:** Feature  

**Description:** User exports all use cases in a project to Word format in batch.

**Functionality:**
1. Menu option "Tools → Export All to Word"
2. Progress dialog shows conversion status
3. Batch conversion of all Markdown files to .docx
4. Word files saved in ./word/ directory
5. Conversion log generated

**Acceptance Criteria:**
- [ ] Converts all use cases sequentially
- [ ] Shows progress bar (e.g., "Converting UC-001... (10%)")
- [ ] Cancels on user action
- [ ] Skips already converted files unless force reconvert selected
- [ ] Summary dialog shows success/failure count

**User Experience:**
- Background processing (does not freeze GUI)
- Option to open generated Word folder automatically
- Conversion speed indicator (e.g., "3 use cases per second")

---

#### CR-011: Export to PDF
**Priority:** Medium  
**Type:** Feature  

**Description:** User exports a single use case specification to PDF format.

**Functionality:**
1. Select use case → Export to PDF
2. Uses Pandoc or pdfkit for conversion
3. Applies PDF styling and formatting
4. Generated file in project directory

**Acceptance Criteria:**
- [ ] Produces readable, printable PDF document
- [ ] Page size configured (A4 or Letter)
- [ ] Margins applied (1-inch standard)
- [ ] Document includes metadata header
- [ ] Hyperlinks preserved if any
- [ ] Font embedding for special characters

**PDF Styling:**
- A4 page size
- 1-inch margins on all sides
- Page numbering (top-right corner)
- Document properties saved in PDF metadata

---

#### CR-012: Import Template
**Priority:** Low  
**Type:** Feature  

**Description:** User can import custom templates for use case generation.

**Functionality:**
1. File → Import Template menu option
2. Opens template file (.md or .json)
3. Validates template structure
4. Adds to local template list
5. Available in "New Use Case" dialog

**Acceptance Criteria:**
- [ ] Validates Markdown template structure
- [ ] Supports both simple and advanced templates
- [ ] Shows preview of template before import
- [ ] Can override default template
- [ ] Imports template metadata if present

**Template Structure:**
```markdown
Use Case: {{use_case_name}}

CHARACTERISTIC INFORMATION

Goal in Context: {{goal_in_context}}
Scope: {{scope}}
...
MAIN SUCCESS SCENARIO

* step #1: {{step_1}}
* step #2: {{step_2}}
...
```

---

### 3.3 Collaboration and Version Control

#### CR-013: Git Integration
**Priority:** Low  
**Type:** Feature  

**Description:** Integrated version control using Git.

**Functionality:**
1. Automatic Git initialization on project creation
2. Stage all use case files for commit
3. Commit message auto-generated (optional user override)
4. Git status indicator in toolbar
5. Branch creation and switching support

**Acceptance Criteria:**
- [ ] Creates .gitignore file automatically
- [ ] Initializes repository with default README
- [ ] Commits on auto-save intervals
- [ ] Shows commit count in project name
- [ ] Allows manual commit/commit all via menu

**User Experience:**
- Git icon indicator (green check = clean, yellow dot = modified)
- "Commit All Changes" button in toolbar
- "View Git Log" dialog showing commit history
- Branch selector dropdown

---

#### CR-014: Export to JSON/YAML
**Priority:** Low  
**Type:** Feature  

**Description:** User can export use case specifications as structured data.

**Functionality:**
1. Export current use case or all use cases as JSON/YAML
2. Useful for integration with other tools
3. Supports full Cockburn specification structure

**Acceptance Criteria:**
- [ ] Produces valid JSON/YAML file
- [ ] Includes all sections (Characteristics, Scenario, Extensions, Variations)
- [ ] Handles Unicode characters correctly
- [ ] File size optimized (no unnecessary whitespace)

**JSON Output Example:**
```json
{
  "use_case_name": "Pay Invoice",
  "creation_date": "2026-04-15",
  "characteristic_information": {
    "goal_in_context": "Allow customers to pay outstanding invoices...",
    "scope": "Customer portal and payment processing system",
    "level": "Primary task",
    ...
  },
  "main_success_scenario": [
    { "step": 1, "description": "System displays invoice summary" },
    { "step": 2, "description": "Customer selects payment method" },
    ...
  ],
  "extensions": [
    {
      "step": 3,
      "condition": "PaymentGatewayTimeout",
      "action": "Retry or offer alternative"
    }
  ]
}
```

---

### 3.4 Search and Navigation

#### CR-015: Global Search
**Priority:** Medium  
**Type:** Feature  

**Description:** User can search across all use cases in the project.

**Functionality:**
1. Ctrl+F opens search dialog
2. Search across:
   - Use case names
   - Characteristic information
   - Main success scenario steps
   - Extensions and conditions
   - Sub-variations
3. Results displayed in separate results window with context
4. Navigate between results with Next/Previous buttons

**Acceptance Criteria:**
- [ ] Performs full-text search across all fields
- [ ] Case-insensitive search by default
- [ ] Highlights matching text in editor
- [ ] Shows result count (e.g., "3 matches in 2 use cases")
- [ ] Esc closes search dialog without selecting first result
- [ ] Regex support optional

**User Experience:**
- Search results window floating above editor
- Clicking result opens corresponding use case and scrolls to match
- Search history saved for current session
- Filter options (search in all fields vs. specific field)

---

#### CR-016: Use Case Navigation Tree
**Priority:** High  
**Type:** Feature  

**Description:** Hierarchical navigation of use cases in the project.

**Functionality:**
1. Left pane displays tree view of all use cases
2. Tree supports:
   - Sorting by name, number, date
   - Grouping by category
   - Filtering by search text
3. Context menu per use case:
   - Edit
   - Rename
   - Duplicate (copy existing use case)
   - Export to Word
   - Export to PDF
   - Delete
4. Expand/Collapse all branches

**Acceptance Criteria:**
- [ ] Tree updates in real-time when use cases are created/modified
- [ ] Sorting persists across project sessions
- [ ] Filtering is case-insensitive
- [ ] Can navigate via keyboard (Up/Down arrows, Enter)
- [ ] Current selection highlighted visually

**Visual Indicators:**
- Modified flag (asterisk or dot) if unsaved changes
- Last modified date timestamp (small font)
- Use case number displayed inline

---

#### CR-017: Bookmark/Favorite Use Cases
**Priority:** Low  
**Type:** Feature  

**Description:** User can mark important use cases as favorites for quick access.

**Functionality:**
1. Add favorite via right-click → "Add to Favorites"
2. Favorites stored separately in project metadata
3. Quick access panel or dedicated favorites section
4. Remove favorite option

**Acceptance Criteria:**
- [ ] Favorites persist across project sessions
- [ ] Can pin favorites at top of navigation tree
- [ ] Unsaved changes still show on favorite items
- [ ] Bulk actions available (export favorites only)

---

### 3.5 Preview and Validation

#### CR-018: Live Markdown Preview
**Priority:** Medium  
**Type:** Feature  

**Description:** Real-time preview of rendered Markdown in the right pane.

**Functionality:**
1. Right pane displays rendered Markdown
2. Updates automatically as user types
3. Supports:
   - Headings, bold, italic
   - Lists (ordered and unordered)
   - Code blocks
   - Tables
   - Links

**Acceptance Criteria:**
- [ ] Preview updates within 300ms of edit
- [ ] Shows formatting indicators (e.g., `#` for heading size)
- [ ] Can switch preview/edit modes with toggle button
- [ ] Supports dark/light theme preview
- [ ] Print view available

**User Experience:**
- Split pane layout shows both editor and preview
- "Sync scrolling" option (vertical scroll matches in both panes)
- Zoom controls for preview (50%, 100%, 150%, 200%)
- Export preview as PDF or HTML

---

#### CR-019: Validation Engine
**Priority:** High  
**Type:** Feature  

**Description:** Validates use case specifications for completeness and quality.

**Validation Rules:**
1. **Required Fields:**
   - Use case name must not be empty
   - Goal in Context, Precondition, Success End Condition required
   - Primary Actor required

2. **Structure Validation:**
   - Main success scenario must have at least 1 step
   - No empty steps allowed
   - Step numbers must be sequential (no gaps)
   - Extensions must reference valid steps
   - Sub-variations must reference valid steps

3. **Content Quality:**
   - Step descriptions should be more than 10 characters
   - Avoid "TODO" placeholders for critical fields
   - Limit field lengths to maximum allowed

**Functionality:**
1. Auto-validation on every edit
2. Visual indicators:
   - Green checkmark for valid
   - Red X for critical errors
   - Yellow warning triangle for warnings
3. Validation summary in status bar or properties panel
4. "Fix All" button attempts to resolve common errors automatically

**Acceptance Criteria:**
- [ ] Real-time validation (no manual trigger required)
- [ ] Error messages provide actionable guidance
- [ ] Validation prioritizes critical errors over warnings
- [ ] Summary dialog shows total errors/warnings count
- [ ] Can disable specific validation rules in preferences

**Error Examples:**
```
❌ Error: Use case name cannot be empty
⚠ Warning: Main success scenario missing
⚠ Warning: Step #3 has no description
✓ Validation passed (no errors)
```

---

### 3.6 Settings and Configuration

#### CR-020: Global Preferences
**Priority:** High  
**Type:** Feature  

**Description:** User can configure global application settings.

**Preferences Tabs:**
1. **General:**
   - Language: English, French, Spanish (default: System locale)
   - Auto-save interval: 5 min, 10 min, 15 min, Disabled
   - Start at last position on open project
   - Show tooltips by default

2. **Editor:**
   - Font family: Inter, Roboto, Arial, Monospace
   - Font size: 12, 14, 16, 18 (default: 14)
   - Tab size: 2, 4, 8 spaces
   - Line numbers toggle
   - Word wrap toggle
   - Syntax highlighting colors (theme selector)

3. **Templates:**
   - Default template selection
   - Custom template path
   - Auto-create from template checkbox

4. **Export:**
   - Default export format: Word, PDF
   - Word template path (.docx)
   - PDF page size: A4, Letter
   - PDF margins: 0.5 inch, 1 inch, 1.5 inch

5. **Interface:**
   - Theme: Light, Dark, System (default: System)
   - UI scale: 100%, 125%, 150%
   - Show status bar: On/Off
   - Show toolbar: On/Off

**Acceptance Criteria:**
- [ ] Changes apply immediately without restart
- [ ] Reset to defaults button available
- [ ] Preferences exportable/importable (backup configuration)
- [ ] Default preferences set on first run

---

#### CR-021: Keyboard Shortcuts
**Priority:** Medium  
**Type:** Feature  

**Description:** User can customize and use keyboard shortcuts.

**Default Shortcuts:**
| Action | Shortcut |
|--------|----------|
| New Use Case | Ctrl+N |
| Open Project | Ctrl+O |
| Save Project | Ctrl+S |
| Save As... | Ctrl+Shift+S |
| Close Project | Ctrl+W |
| Find | Ctrl+F |
| Replace | Ctrl+H |
| Undo | Ctrl+Z |
| Redo | Ctrl+Y |
| Copy | Ctrl+C |
| Paste | Ctrl+V |
| Cut | Ctrl+X |
| Print | Ctrl+P |
| Export to Word | Ctrl+E |
| Export to PDF | Ctrl+Shift+E |
| Toggle Preview | Alt+P |
| Fullscreen | F11 |

**Functionality:**
1. Edit keyboard shortcuts via Preferences → Keyboard
2. Conflict detection for duplicate shortcuts
3. Show all shortcuts in Help → Keyboard Shortcuts menu
4. Shortcut suggestion as user types

**Acceptance Criteria:**
- [ ] All standard shortcuts work consistently
- [ ] Customizable shortcuts with conflict warnings
- [ ] Keyboard shortcut dialog shows current binding
- [ ] Remappable to any key combination
- [ ] Reset to defaults option available

---

### 3.7 Help and Support

#### CR-022: User Guide / Help System
**Priority:** Medium  
**Type:** Feature  

**Description:** Integrated help documentation accessible from within the application.

**Functionality:**
1. Help → User Guide opens browser or built-in documentation viewer
2. Content includes:
   - Getting Started guide
   - Feature descriptions with screenshots
   - Tutorial walkthroughs
   - Best practices for Cockburn specifications
3. Searchable help system
4. Context-sensitive help (F1 on dialog)

**Acceptance Criteria:**
- [ ] Built-in help viewer (HTML/Markdown)
- [ ] Search across entire help system
- [ ] F1 opens context-specific help for selected element
- [ ] Links to external documentation if needed
- [ ] Localizable help content

---

#### CR-023: Keyboard Shortcuts Reference
**Priority:** Low  
**Type:** Feature  

**Description:** Display all keyboard shortcuts in a dedicated dialog.

**Functionality:**
1. Help → Keyboard Shortcuts opens dialog with all shortcuts
2. Categorized by action (File, Edit, View, Tools)
3. Filter search box available
4. Copy shortcuts to clipboard button

**Acceptance Criteria:**
- [ ] All default shortcuts listed
- [ ] Shows custom shortcuts user has configured
- [ ] Filter functionality working
- [ ] Clear UI layout

---

## 4. Non-Functional Requirements

### 4.1 Performance Requirements

#### NFR-001: Startup Time
**Requirement:** Application should start within 3 seconds on a modern computer (8GB RAM, SSD).

**Acceptance Criteria:**
- [ ] Splash screen displayed during startup
- [ ] Main window fully rendered within 3 seconds
- [ ] Project loading from disk < 2 seconds for typical projects (<100 use cases)

#### NFR-002: Response Time
**Requirement:** UI should respond to user input within 200ms (excluding background tasks).

**Acceptance Criteria:**
- [ ] Menu item click response < 150ms
- [ ] Dialog open/close < 200ms
- [ ] Auto-save interval configured by user does not freeze UI

#### NFR-003: Concurrency
**Requirement:** Support concurrent use case files with minimal memory overhead.

**Acceptance Criteria:**
- [ ] Can have 50+ use cases in project with <500MB RAM usage
- [ ] Switching between use cases is instantaneous (<100ms)
- [ ] Large projects (>200 use cases) still responsive

#### NFR-004: Export Performance
**Requirement:** Export to Word should complete within 10 seconds for a single use case on a modern computer.

**Acceptance Criteria:**
- [ ] Conversion progress shown during export
- [ ] Can cancel long-running exports
- [ ] PDF generation completes within 15 seconds per use case

### 4.2 Usability Requirements

#### NFR-005: Learnability
**Requirement:** New users should be able to generate their first use case specification in less than 10 minutes.

**Acceptance Criteria:**
- [ ] Welcome dialog on first launch with tutorial link
- [ ] Clear step-by-step guidance for new use case creation
- [ ] Inline help tooltips accessible for all fields
- [ ] Short tutorial video or GIF available

#### NFR-006: Error Prevention
**Requirement:** Interface should guide users away from making common mistakes.

**Acceptance Criteria:**
- [ ] Validation errors displayed immediately on invalid input
- [ ] Clear error messages with actionable suggestions
- [ ] Prevents actions that would result in data loss (e.g., closing without saving)

#### NFR-007: Accessibility
**Requirement:** Application should be usable by users with disabilities.

**Acceptance Criteria:**
- [ ] Support for screen readers (JAWS, NVDA)
- [ ] High contrast mode available (WCAG AA compliant)
- [ ] Keyboard navigation fully supported (Tab, Alt, Ctrl combinations)
- [ ] Font size at least 12px minimum
- [ ] Colorblind-friendly color schemes

### 4.3 Security Requirements

#### NFR-008: Data Protection
**Requirement:** User data and project files should be protected.

**Acceptance Criteria:**
- [ ] File paths encrypted when stored in memory (optional)
- [ ] Project password protection (encryption of .cpz file)
- [ ] No insecure storage of credentials
- [ ] Automatic lock after idle period (15 minutes)

#### NFR-009: Backup and Recovery
**Requirement:** System should have mechanisms to prevent data loss.

**Acceptance Criteria:**
- [ ] Auto-save every 30 seconds (configurable)
- [ ] Backup file created before major operations (e.g., delete use case)
- [ ] Undo/Redo for last 50 actions
- [ ] Project version history (Git integration)

### 4.4 Compatibility Requirements

#### NFR-010: Platform Compatibility
**Requirement:** Application should run on supported platforms with minimal configuration.

**Acceptance Criteria:**
- [ ] Installation packages for Windows (.exe), macOS (.dmg), Linux (.AppImage)
- [ ] Cross-platform UI consistency (QT framework ensures this)
- [ ] No native platform dependencies beyond QT
- [ ] Works with standard office software (Office, LibreOffice)

#### NFR-011: External Dependencies
**Requirement:** Minimal and well-managed external dependencies.

**Acceptance Criteria:**
- [ ] Pandoc required for Word/PDF export (checked at startup)
- [ ] No runtime dependencies on proprietary software
- [ ] QT framework for GUI (open source, permissive license)
- [ ] Optional: python-docx if preferred over Pandoc

### 4.5 Maintainability Requirements

#### NFR-012: Code Quality
**Requirement:** Code should follow best practices for maintainability.

**Acceptance Criteria:**
- [ ] Follow PEP 8 style guide (Python code)
- [ ] Modular architecture with clear separation of concerns
- [ ] Comprehensive test coverage (>80%)
- [ ] Logging system for debugging
- [ ] Error handling throughout the application

#### NFR-013: Documentation
**Requirement:** Well-documented codebase for future maintenance.

**Acceptance Criteria:**
- [ ] Inline comments for complex logic
- [ ] Module-level docstrings
- [ ] API documentation generated (Sphinx)
- [ ] README with installation and usage instructions

### 4.6 Localization Requirements

#### NFR-014: Internationalization Support
**Requirement:** Application should support multiple languages.

**Acceptance Criteria:**
- [ ] English default UI
- [ ] French translation available
- [ ] String extraction for localization (gettext)
- [ ] Date and time formatting adapted to locale
- [ ] Text direction support (LTR/RTL)

---

## 5. User Stories

### US-001: New User Creates First Use Case

**As a** first-time user  
**I want** to create a new use case specification in under 10 minutes  
**So that** I can start documenting requirements for my project  

**Acceptance Criteria:**
1. Launch application and see welcome dialog
2. Click "New Use Case" and follow guided steps
3. Enter minimal required information (name, primary actor)
4. See validation warnings if something is missing
5. Generate first specification successfully
6. Export to Word and verify format is correct

**Priority:** High  
**Estimate:** 8 story points  

---

### US-002: Project Manager Reviews Multiple Use Cases

**As a** project manager reviewing requirements  
**I want** to quickly navigate and compare use case specifications  
**So that** I can provide feedback efficiently  

**Acceptance Criteria:**
1. Open project with multiple use cases
2. Use navigation tree to jump between use cases
3. See last modified dates and save status
4. Search for specific terms across all documents
5. Export all use cases to Word simultaneously
6. Compare two use cases side by side

**Priority:** Medium  
**Estimate:** 5 story points  

---

### US-003: Developer Imports Specification into Codebase

**As a** developer working on implementation  
**I want** to import use case specifications as JSON/YAML  
**So that** I can automate documentation generation in CI/CD  

**Acceptance Criteria:**
1. Export use case as JSON with complete structure
2. Validate JSON structure matches expected schema
3. Use exported data to generate test cases automatically
4. Update use case and re-export without data loss
5. Import existing JSON back into project

**Priority:** Low  
**Estimate:** 3 story points  

---

### US-004: Advanced User Customizes Templates

**As an** experienced user familiar with Cockburn methodology  
**I want** to customize templates for different projects  
**So that** I can ensure consistent documentation style across teams  

**Acceptance Criteria:**
1. Import custom Markdown template
2. Preview template before applying
3. Define custom fields in template
4. Use new template when creating use cases
5. Share custom template with team members

**Priority:** Low  
**Estimate:** 5 story points  

---

### US-005: User Fixes Validation Errors Automatically

**As a** user unfamiliar with Cockburn standards  
**I want** the system to suggest fixes for validation errors  
**So that** I don't have to guess how to correct my specifications  

**Acceptance Criteria:**
1. Create use case with missing critical field
2. Validation error appears immediately
3. Error message suggests possible value
4. "Fix" button attempts to resolve common errors
5. Manual override still possible after auto-fix

**Priority:** Medium  
**Estimate:** 5 story points  

---

## 6. Technical Considerations

### 6.1 Technology Stack

#### Recommended Frameworks:
- **GUI Framework:** PyQt6 or PySide6 (modern, cross-platform, professional look)
- **Text Editor Component:** QSyntaxHighlighter + QTextEdit/ QTextDocument
- **Markdown Rendering:** QtMarkdown (built-in) or Misaka (Python markdown library)
- **ZIP/Packaging:** Python zipfile module for .cpz format
- **Pandoc Integration:** Subprocess calls or python-pandoc wrapper

#### Alternative Options:
- **Tkinter:** Simpler, less modern UI, faster to develop but less professional
- **PyWebView:** Electron-like web interface using system browsers (limited control)
- **Flet:** Flutter-based framework for Python, very modern but newer ecosystem

### 6.2 Architecture Patterns

#### Model-View-Controller (MVC) or Model-View-Presenter:
```
Model: UseCase, CharacteristicInformation, ScenarioStep classes
View: PyQt forms, widgets, layouts
Controller: EditorController handles user input and updates model
```

#### Modular Design:
```
cockburn_spec_generator_v2/
├── main.py                 # Application entry point
├── ui/                     # GUI components
│   ├── main_window.py
│   ├── editor.py
│   ├── navigation_tree.py
│   └── dialogs/
├── core/                   # Business logic
│   ├── usecase.py
│   ├── validator.py
│   └── exporter.py
├── models/                 # Data models
│   ├── characteristic.py
│   ├── scenario.py
│   └── metadata.py
├── templates/              # Template files
│   └── default.md
├── utils/                  # Helper functions
├── resources/              # UI assets (icons, styles)
└── tests/
```

### 6.3 Data Structure Design

#### UseCase Data Model:
```python
class UseCase:
    def __init__(self):
        self.name: str = ""
        self.number: int = 0
        self.created_date: datetime = None
        self.characteristic_information: dict = {}
        self.main_success_scenario: List[ScenarioStep] = []
        self.extensions: List[Extension] = []
        self.sub_variations: List[SubVariation] = []
        self.related_information: dict = {}

class ScenarioStep:
    def __init__(self, step_number: int, description: str):
        self.step_number: int = step_number
        self.description: str = description

class Extension:
    def __init__(self, step_number: int, condition: str, action: str):
        self.step_number: int = step_number
        self.condition: str = condition
        self.action: str = action

class SubVariation:
    def __init__(self, step_number: int, sub_steps: List[str]):
        self.step_number: int = step_number
        self.sub_steps: List[str] = sub_steps
```

#### Project Metadata:
```json
{
  "project_name": "Customer Portal System",
  "created_date": "2026-04-15",
  "last_modified": "2026-04-15T12:30:00",
  "version": "2.0.0",
  "use_case_count": 25,
  "preferences": {
    "theme": "dark",
    "font_size": 14,
    "auto_save_interval": 600
  }
}
```

### 6.4 Markdown Conversion Strategy

#### Option 1: Pandoc (Recommended for Word/PDF):
- Pros: Industry standard, robust conversion, good styling support
- Cons: Requires external tool installation
- Implementation: subprocess.Popen or python-pandoc wrapper

```python
import subprocess

def convert_to_word(markdown_path: str, output_path: str):
    command = [
        "pandoc",
        "-f", "markdown",
        "-t", "docx",
        "-o", output_path,
        "--reference-doc", "templates/default.docx"
    ]
    subprocess.run(command, check=True)
```

#### Option 2: python-docx (Python-native):
- Pros: Pure Python, no external dependencies
- Cons: Limited styling control, more manual HTML-to-docx conversion

```python
from docx import Document
from docx.shared import Pt
import markdown

def convert_to_word(markdown_path: str, output_path: str):
    md_content = read_file(markdown_path)
    html = markdown.markdown(md_content)
    # Convert HTML to python-docx elements manually
```

### 6.5 Validation Engine Design

#### Validation Rules Implementation:
```python
class ValidationEngine:
    @staticmethod
    def validate_use_case(use_case: UseCase) -> List[ValidationError]:
        errors = []
        
        # Required fields check
        if not use_case.name:
            errors.append(ValidationError("use_case_name", "Empty"))
        
        if not use_case.characteristic_information.get("goal_in_context"):
            errors.append(ValidationError("goal_in_context", "Missing"))
            
        # Structure check
        if not use_case.main_success_scenario:
            errors.append(ValidationError("main_success_scenario", "Empty"))
        
        # Sequential steps check
        for i, step in enumerate(use_case.main_success_scenario):
            expected_number = i + 1
            if step.step_number != expected_number:
                errors.append(ValidationError(
                    f"step_{expected_number}",
                    f"Expected {expected_number}, got {step.step_number}"
                ))
        
        return errors

class ValidationError:
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
```

### 6.6 Project File Format (.cpz)

#### ZIP Structure:
```
project.cpz (ZIP archive)
├── metadata.json           # Project metadata
├── templates/              # Optional custom templates
│   └── default.md
└── use_cases/
    ├── UC-001_PayInvoice.md
    ├── UC-002_CreateInvoice.md
    └── ...
```

#### Compression Strategy:
- Use ZIP with deflate compression (balance between speed and size)
- Exclude .docx files from main project archive (optional separate export)
- Include Git metadata if available (.git folder, optional)

### 6.7 Auto-Save Mechanism

```python
import time
from threading import Timer

class AutoSaveManager:
    def __init__(self, on_save_callback, interval_seconds=30):
        self.on_save_callback = on_save_callback
        self.interval = interval_seconds
        self.timer = None
    
    def start(self):
        if self.timer:
            self.timer.cancel()
        self.timer = Timer(self.interval, self._save)
        self.timer.start()
    
    def _save(self):
        self.on_save_callback()
        self.start()  # Restart timer for next cycle
    
    def stop(self):
        if self.timer:
            self.timer.cancel()
```

### 6.8 Theme System

#### Qt Stylesheet-based Theming:
```css
/* Light Theme */
QMainWindow {
    background-color: #f5f5f5;
}

QTextEdit {
    font-family: 'Inter', sans-serif;
    font-size: 14pt;
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
}

QPushButton {
    background-color: #0078d7;
    color: white;
    padding: 6px 12px;
    border-radius: 4px;
}

/* Dark Theme */
QMainWindow {
    background-color: #2d2d30;
}

QTextEdit {
    background-color: #1e1e1e;
    color: #d4d4d4;
}
```

### 6.9 Testing Strategy

#### Unit Tests (pytest):
- Test validation rules for edge cases
- Test Markdown parsing/conversion
- Test data model serialization/deserialization
- Mock external dependencies (Pandoc)

#### Integration Tests:
- Test complete workflow from project creation to export
- Test concurrent file operations
- Test performance with large projects

#### UI Tests (pytest-qt):
- Test dialog opening/closing
- Test button interactions
- Test keyboard shortcuts
- Test validation feedback

```python
# Example unit test
def test_use_case_validation():
    use_case = UseCase()
    errors = ValidationEngine.validate_use_case(use_case)
    
    # Should have at least one error for empty name
    assert len(errors) > 0
    assert any(e.field == "use_case_name" for e in errors)
```

---

## 7. Implementation Phases

### Phase 1: Core Functionality (MVP)
**Duration:** 4-6 weeks

**Features:**
- Basic GUI framework with PyQt6
- New use case creation wizard
- Editor with form-based characteristic information
- Main success scenario step editor
- Export to Word functionality
- Auto-save mechanism
- Validation engine

**Deliverables:**
- Working prototype that replicates CLI functionality in GUI
- First release candidate (v0.9)

---

### Phase 2: Enhanced Features
**Duration:** 4-6 weeks

**Features:**
- Extensions and sub-variations management
- Preview pane with live Markdown rendering
- Search and navigation improvements
- Template system
- Keyboard shortcuts
- Settings/preferences dialog

**Deliverables:**
- Feature-complete v1.0 release candidate

---

### Phase 3: Collaboration and Polish
**Duration:** 2-3 weeks

**Features:**
- Batch export (all to Word/PDF)
- Git integration
- Export to JSON/YAML
- Help system
- Accessibility improvements
- Performance optimization
- Bug fixes and refinement

**Deliverables:**
- Production-ready v1.0 release

---

### Phase 4: Future Enhancements (Out of Scope for V2)
**Potential future features:**
- Auto-detection of use cases from existing documentation
- Collaborative editing (multi-user, real-time)
- Use case dependency graph visualization
- Integration with project management tools (Jira, Trello)
- AI-assisted use case generation
- Plugin system for custom exporters

---

## 8. Dependencies

### Minimum Required:
1. **Python:** 3.10 or higher
2. **Pandoc:** 2.14+ (for Word/PDF export)
   - Install: `brew install pandoc` (macOS), `sudo apt install pandoc` (Ubuntu)

### Recommended Optional:
1. **QDarkStyle:** Dark theme for Qt applications
2. **Misaka:** Python markdown library (alternative to Pandoc for rendering)
3. **python-docx:** For Word export without Pandoc

### Package Dependencies (requirements.txt):
```
PyQt6==6.5.0
Markdown==3.5.1
python-dateutil==2.8.2
zipfile-deflate64  # Optional, faster compression
```

---

## 9. Glossary

- **Cockburn Methodology:** A set of guidelines for writing use case specifications, developed by Alistair Cockburn
- **Use Case:** A description of how a system is used by an actor to accomplish a goal
- **Characteristic Information:** The descriptive fields that provide context about the use case
- **Main Success Scenario:** The primary "happy path" flow where everything goes according to plan
- **Extensions:** Alternative paths and error conditions that deviate from the main scenario
- **Sub-variations:** Nested branches within a step that create forks in the scenario flow
- **Markdown:** A lightweight markup language for formatting text
- **Pandoc:** Universal document converter supporting multiple formats
- **MVP (Minimum Viable Product):** The most basic version of the product that still delivers core value

---

## 10. Conclusion

This document provides a comprehensive roadmap for developing a modern GUI version of the Cockburn Specification Generator. By following these functional requirements, the development team can build an intuitive, powerful application that enhances the existing CLI tool with better user experience and expanded capabilities.

The V2 application should:
- Maintain full backward compatibility with existing use case specifications
- Improve usability for teams new to the Cockburn methodology
- Enable seamless integration with modern development workflows
- Provide a professional tool for software requirements documentation

**Next Steps:**
1. Review and approve this document with stakeholders
2. Prioritize features based on business value
3. Begin Phase 1 implementation planning
4. Set up development environment and CI/CD pipeline

---

## 11. Approval

| Role | Name | Date |
|------|------|------|
| Product Owner | | |
| Technical Lead | | |
| QA Lead | | |

**Version History:**
- v1.0 (2026-04-15): Initial draft