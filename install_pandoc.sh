#!/bin/bash
######################################
# Pandoc Installer Script
# This script checks for pandoc and installs it if missing
######################################

set -e

print_status() {
    echo -e "${PROMPT_STYLE}$(date +%H:%M:%S) $1${RAZ_STYLE}"
}

print_success() {
    echo -e "${GREEN_STYLE}✓ $1${RAZ_STYLE}"
}

print_error() {
    echo -e "${RED_STYLE}✗ $1${RAZ_STYLE}" >&2
}

print_warning() {
    echo -e "${ORANGE_STYLE}⚠ $1${RAZ_STYLE}"
}

# Check if pandoc is already installed
check_pandoc() {
    print_status "Checking for pandoc..."
    
    if command -v pandoc &> /dev/null; then
        print_success "Pandoc is already installed: $(pandoc --version | head -n1)"
        return 0
    else
        print_warning "Pandoc is not installed"
        return 1
    fi
}

# Install from .deb package
install_from_deb() {
    local deb_file="pandoc-3.9.0.2-1-amd64.deb"
    local download_url="https://github.com/jgm/pandoc/releases/download/3.9.0.2/${deb_file}"
    local output_file="./${deb_file}"
    
    print_status "Downloading pandoc from GitHub..."
    
    # Download the package
    if curl -fL "${download_url}" -o "${output_file}"; then
        print_success "Downloaded: ${output_file}"
    else
        print_error "Failed to download pandoc"
        echo ""
        echo "Please download manually from:"
        echo "  ${download_url}"
        return 1
    fi
    
    # Install the package
    print_status "Installing pandoc..."
    
    if dpkg -i "${output_file}"; then
        print_success "Pandoc installed successfully"
    else
        print_error "dpkg installation failed, trying apt-get..."
        
        # Fix dependencies and install
        sudo apt-get update -qq
        sudo apt-get install -f -qq
        sudo dpkg -i "${output_file}"
        
        if [ $? -eq 0 ]; then
            print_success "Pandoc installed successfully"
        else
            print_error "Installation failed"
            return 1
        fi
    fi
    
    # Clean up download
    rm -f "${output_file}"
    print_status "Cleaned up downloaded package"
}

# Install using apt (alternative method)
install_from_apt() {
    print_status "Installing pandoc via apt..."
    
    if command -v apt-get &> /dev/null; then
        sudo apt-get update -qq
        sudo apt-get install -y pandoc
        
        if [ $? -eq 0 ]; then
            print_success "Pandoc installed via apt"
        else
            print_error "apt installation failed"
            return 1
        fi
    elif command -v yum &> /dev/null; then
        sudo yum install -y pandoc
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y pandoc
    else
        print_error "Unsupported package manager"
        return 1
    fi
}

# Main execution
main() {
    echo ""
    echo "####################################"
    echo "# Pandoc Installer for Cockburn Specification Generator #"
    echo "####################################"
    echo ""
    
    # Check if pandoc is already installed
    check_pandoc || true
    
    if [ $? -eq 0 ]; then
        print_status "Pandoc is ready to use!"
        echo ""
        echo "Usage: pandoc -o output.docx input.md"
        echo ""
        exit 0
    fi
    
    # Determine installation method
    if command -v curl &> /dev/null; then
        print_status "Installing pandoc from GitHub release..."
        install_from_deb
    elif command -v apt-get &> /dev/null || command -v yum &> /dev/null || command -v dnf &> /dev/null; then
        print_status "Installing pandoc via system package manager..."
        install_from_apt
    else
        print_error "No suitable package manager found"
        echo ""
        echo "Please install pandoc manually:"
        echo "  curl -L https://github.com/jgm/pandoc/releases/download/3.9.0.2/pandoc-3.9.0.2-1-amd64.deb -o pandoc.deb"
        echo "  sudo dpkg -i pandoc.deb"
        echo ""
        exit 1
    fi
    
    # Verify installation
    echo ""
    print_status "Verifying pandoc installation..."
    
    if command -v pandoc &> /dev/null; then
        local version=$(pandoc --version | head -n1)
        print_success "Pandoc is ready!"
        echo "  ${version}"
        echo ""
        echo "You can now use the specification generator."
        echo "Run: ./main.sh"
    else
        print_error "Pandoc verification failed"
        exit 1
    fi
    
    echo ""
}

# Run main function
main "$@"
