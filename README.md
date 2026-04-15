# Cockburn Specification Generator

A command-line tool for generating **use case specifications** based on Alistair Cockburn's User Story and Use Case methodology. This tool helps software teams document system requirements in a structured, consistent format that aligns with agile development practices.

---

## Overview

This generator creates detailed use case documentation following the Cockburn framework, which includes:

- **Characteristic Information** - Context, scope, preconditions, success/failure conditions
- **Main Success Scenario** - The primary happy path flow
- **Extensions** - Alternative paths and error handling
- **Sub-variations** - Branching scenarios and edge cases

The output is saved as Markdown files that can be converted to Microsoft Word documents using Pandoc.

---

## Features

### Core Functionality

1. **Interactive Generation** - Step-by-step interactive prompts guide users through creating complete use case specifications
2. **Template Support** - Built-in Cockburn-compliant template ensures consistent documentation structure
3. **Batch Processing** - Convert all generated specifications to Word format with a single command
4. **Modular Architecture** - Clean separation of concerns with library modules for extensibility

### Output Format

- **Markdown (.md)** - Human-readable, version-controlled documentation
- **Word (.docx)** - Professional formatting for stakeholder review (requires Pandoc)

---

## Architecture

```
cockburn_specification_generator/
├── main.sh                    # Entry point - interactive menu system
├── lib/                       # Library modules
│   ├── create_specification.sh  # Core specification creation logic
│   ├── convert_specifications.sh # Batch conversion utilities
│   └── style.sh                # UI styling and output formatting
├── resources/
│   └── template.md            # Output template structure
├── markdown/                  # Generated use case files
└── word/                      # Converted Word documents
```

### Key Components

| Component | Purpose |
|-----------|---------|
| `main.sh` | Orchestrates the interactive workflow with menu-driven navigation |
| `create_specification.sh` | Handles user input collection and file generation |
| `convert_specifications.sh` | Batch converts Markdown to Word using Pandoc |
| `style.sh` | Provides colored output, prompts, and UI formatting |

---

## Installation & Usage

### Prerequisites

- **Bash** - Shell environment
- **Pandoc** - Markdown to Word converter (optional, for .docx export)

### Install Pandoc

```bash
./install_pandoc.sh
```

### Run the Generator

```bash
./main.sh
```

The tool will present an interactive menu:

1. **Choose a use case name** - Defines the output filename
2. **Enter characteristic information** - Context, scope, actors, etc.
3. **Define main success scenario** - Happy path steps
4. **Add extensions** - Alternative paths and error conditions
5. **Add sub-variations** - Branching scenarios

### Generate Word Documents

```bash
# Convert all specifications at once
convert_all

# Or convert a single file manually
pandoc -o ./word/<filename>.docx -f markdown -t docx ./markdown/<filename>.md
```

---

## Generated Specification Structure

Each use case specification includes:

- **Header** - Use case name and creation date
- **Characteristic Information** - 8 standard fields covering context, scope, actors, triggers
- **Main Success Scenario** - Numbered step-by-step flow
- **Extensions** - Alternative paths with step references
- **Sub-variations** - Branching scenarios with nested steps
- **Related Information** - Priority, performance targets, dependencies
- **Open Issues & Schedule** - Tracking fields

---

## Example Output

A generated use case file (`UC-01_PayInvoice.md`) might contain:

```markdown
# Pay Invoice

> Date de création : 2026-04-15

## CHARACTERISTIC INFORMATION

Goal in Context: Allow customers to pay outstanding invoices...
Scope: Customer portal and payment processing system
Level: Primary task
Preconditions: User has an account with unpaid invoices
Success End Condition: Invoice marked as paid, receipt generated
Failed End Condition: Payment declined or timeout
Primary Actor: Customer
Trigger: Customer initiates payment from invoice list

## MAIN SUCCESS SCENARIO

* step #1: System displays invoice summary
* step #2: Customer selects payment method
* step #3: Payment gateway processes transaction
* step #4: Receipt is emailed to customer

## EXTENSIONS

step altered #3 > PaymentGatewayTimeout : Retry or offer alternative
step altered #2 > NoPaymentMethods : Display available options

## SUB-VARIATIONS

step: 2
* Credit Card (via Stripe)
* Bank Transfer
* PayPal
```

---

## Best Practices

1. **Use descriptive names** - Avoid special characters in use case names
2. **Be specific with steps** - Each step should be atomic and testable
3. **Document extensions thoroughly** - These capture edge cases and error handling
4. **Link related use cases** - Use the "Related Information" section for dependencies

---

## Limitations

- Requires manual input of all content (no auto-generation)
- Word conversion requires Pandoc installed on the system
- No built-in validation or review workflow
- Single-user design (not concurrent multi-user)

---

## Future Enhancements

Potential improvements:

- **Auto-detection** - Extract use cases from existing documentation
- **Validation** - Check for missing required fields
- **Export formats** - Add JSON, YAML for CI/CD integration
- **Review workflow** - Collaborative review and approval process
- **Version control hooks** - Pre-commit checks for specification quality

---

## License

This tool is provided as-is. Please credit Alistair Cockburn's methodology in any derived work.

---

## Contact & Support

For questions or contributions, please reach out to the original project owner.
