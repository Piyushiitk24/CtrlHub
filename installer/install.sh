#!/bin/bash

# CtrlHub Control Systems - Local Agent Installer
# Cross-platform installer for the Python local agent

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
AGENT_DIR="$HOME/.ctrlhub"
PYTHON_MIN_VERSION="3.8"
VENV_NAME="ctrlhub-env"

# Platform detection
PLATFORM=""
case "$(uname -s)" in
    Darwin*)    PLATFORM="macos";;
    Linux*)     PLATFORM="linux";;
    MINGW*|CYGWIN*|MSYS*) PLATFORM="windows";;
    *)          PLATFORM="unknown";;
esac

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              CtrlHub Control Systems - Local Agent          ║${NC}">
echo -e "${BLUE}║                                                              ║${NC}"
echo -e "${BLUE}║  This installer will set up the local Python agent that    ║${NC}"
echo -e "${BLUE}║  enables hardware communication for CtrlHub.               ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Utility functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Version comparison function
version_ge() {
    [ "$(printf '%s\n' "$1" "$2" | sort -V | head -n1)" = "$2" ]
}

# Check Python installation
check_python() {
    log_info "Checking Python installation..."
    
    PYTHON_CMD=""
    
    # Try different Python commands
    for cmd in python3 python; do
        if command_exists "$cmd"; then
            PYTHON_VERSION=$($cmd --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
            if [ -n "$PYTHON_VERSION" ]; then
                if version_ge "$PYTHON_VERSION" "$PYTHON_MIN_VERSION"; then
                    PYTHON_CMD="$cmd"
                    log_success "Found Python $PYTHON_VERSION at $(which $cmd)"
                    break
                else
                    log_warning "Python $PYTHON_VERSION found but minimum $PYTHON_MIN_VERSION required"
                fi
            fi
        fi
    done
    
    if [ -z "$PYTHON_CMD" ]; then
        log_error "Python $PYTHON_MIN_VERSION or higher is required but not found."
        echo ""
        echo "Please install Python from https://python.org/downloads/"
        echo "Make sure to:"
        echo "  1. Install Python $PYTHON_MIN_VERSION or higher"
        echo "  2. Add Python to your PATH"
        echo "  3. Run this installer again"
        exit 1
    fi
    
    export PYTHON_CMD
}

# Check pip
check_pip() {
    log_info "Checking pip installation..."
    
    if ! $PYTHON_CMD -m pip --version >/dev/null 2>&1; then
        log_error "pip is not available"
        echo ""
        echo "Please ensure pip is installed:"
        echo "  curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py"
        echo "  $PYTHON_CMD get-pip.py"
        exit 1
    fi
    
    log_success "pip is available"
}

# Create installation directory
create_install_dir() {
    log_info "Creating installation directory..."
    
    if [ -d "$AGENT_DIR" ]; then
        log_warning "Installation directory already exists: $AGENT_DIR"
        read -p "Do you want to overwrite the existing installation? [y/N]: " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Installation cancelled by user"
            exit 0
        fi
        rm -rf "$AGENT_DIR"
    fi
    
    mkdir -p "$AGENT_DIR"
    log_success "Created installation directory: $AGENT_DIR"
}

# Create virtual environment
create_virtual_env() {
    log_info "Creating Python virtual environment..."
    
    cd "$AGENT_DIR"
    $PYTHON_CMD -m venv "$VENV_NAME"
    
    # Activate virtual environment
    if [ "$PLATFORM" = "windows" ]; then
        source "$VENV_NAME/Scripts/activate"
    else
        source "$VENV_NAME/bin/activate"
    fi
    
    # Upgrade pip in virtual environment
    pip install --upgrade pip
    
    log_success "Virtual environment created: $AGENT_DIR/$VENV_NAME"
}

# Download and install agent files
install_agent_files() {
    log_info "Installing CtrlHub Desktop Agent..."
    
    # Create directory structure
    mkdir -p local_agent/{models,controllers,simulations,hardware,utils}
    
    # Copy or download agent files
    # In a real deployment, this would download from a release or copy from installation media
    log_info "Copying agent files..."
    
    # For now, we'll create a minimal version indicator
    cat > local_agent/__init__.py << 'EOF'
"""
CtrlHub Desktop Agent
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "CtrlHub Team"
EOF

    # Install Python dependencies
    log_info "Installing Python dependencies..."
    
    cat > requirements.txt << 'EOF'
# Core dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
PyQt5==5.15.10
pyserial==3.5
websockets==12.0

# Scientific computing
numpy==1.24.3
scipy==1.11.4
matplotlib==3.8.2
control==0.10.0

# Data handling
pandas==2.1.4
pydantic==2.5.2

# Development tools
python-multipart==0.0.6
jinja2==3.1.2
EOF

    pip install -r requirements.txt
    
    log_success "Python dependencies installed"
}

# Create launcher scripts
create_launchers() {
    log_info "Creating launcher scripts..."
    
    # Platform-specific launcher
    if [ "$PLATFORM" = "windows" ]; then
        # Windows batch file
        cat > ctrlhub-agent.bat << EOF
@echo off
cd /d "$AGENT_DIR"
call "$VENV_NAME\\Scripts\\activate.bat"
python local_agent/main.py %*
EOF
        chmod +x ctrlhub-agent.bat
        log_success "Created Windows launcher: $AGENT_DIR/ctrlhub-agent.bat"
        
    else
        # Unix shell script
        cat > ctrlhub-agent.sh << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source "./ctrlhub-env/Scripts/activate"
else
    source "./ctrlhub-env/bin/activate"
fi

# Run the agent
python local_agent/main.py "$@"
EOF
        chmod +x ctrlhub-agent.sh
        log_success "Created launcher script: $AGENT_DIR/ctrlhub-agent.sh"
    fi
}

# Create desktop shortcut (platform-specific)
create_desktop_shortcut() {
    log_info "Creating desktop shortcut..."
    
    case "$PLATFORM" in
        "macos")
            # macOS .app bundle or Alias
            osascript -e "tell application \"Finder\" to make alias file to POSIX file \"$AGENT_DIR/ctrlhub-agent.sh\" at desktop"
            log_success "Created desktop alias"
            ;;
        "linux")
            # Linux .desktop file
            DESKTOP_FILE="$HOME/Desktop/CtrlHub-Agent.desktop"
            cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=CtrlHub Desktop Agent
Comment=Local hardware interface for CtrlHub
Icon=$AGENT_DIR/icon.png
Exec=$AGENT_DIR/ctrlhub-agent.sh
Terminal=false
Categories=Education;Science;
EOF
            chmod +x "$DESKTOP_FILE"
            log_success "Created desktop shortcut: $DESKTOP_FILE"
            ;;
        "windows")
            # Windows shortcut (simplified)
            log_warning "Windows shortcut creation requires manual setup"
            echo "Please create a shortcut to: $AGENT_DIR\\ctrlhub-agent.bat"
            ;;
    esac
}

# Add to system PATH (optional)
add_to_path() {
    log_info "Adding CtrlHub to system PATH..."
    
    case "$PLATFORM" in
        "macos")
            # Add to .zshrc or .bash_profile
            SHELL_RC="$HOME/.zshrc"
            if [ ! -f "$SHELL_RC" ]; then
                SHELL_RC="$HOME/.bash_profile"
            fi
            
            if ! grep -q "ctrlhub-agent" "$SHELL_RC" 2>/dev/null; then
                echo "" >> "$SHELL_RC"
                echo "# CtrlHub Desktop Agent" >> "$SHELL_RC"
                echo "alias ctrlhub-agent='$AGENT_DIR/ctrlhub-agent.sh'" >> "$SHELL_RC"
                log_success "Added alias to $SHELL_RC"
                log_info "Run 'source $SHELL_RC' or restart terminal to use 'ctrlhub-agent' command"
            fi
            ;;
        "linux")
            # Add to .bashrc
            BASHRC="$HOME/.bashrc"
            if ! grep -q "ctrlhub-agent" "$BASHRC" 2>/dev/null; then
                echo "" >> "$BASHRC"
                echo "# CtrlHub Desktop Agent" >> "$BASHRC"
                echo "alias ctrlhub-agent='$AGENT_DIR/ctrlhub-agent.sh'" >> "$BASHRC"
                log_success "Added alias to $BASHRC"
                log_info "Run 'source ~/.bashrc' or restart terminal to use 'ctrlhub-agent' command"
            fi
            ;;
        "windows")
            log_warning "PATH modification on Windows requires manual setup"
            echo "To use 'ctrlhub-agent' command globally:"
            echo "  1. Add $AGENT_DIR to your System PATH"
            echo "  2. Restart Command Prompt"
            ;;
    esac
}

# Test installation
test_installation() {
    log_info "Testing installation..."
    
    cd "$AGENT_DIR"
    
    # Activate virtual environment
    if [ "$PLATFORM" = "windows" ]; then
        source "$VENV_NAME/Scripts/activate"
    else
        source "$VENV_NAME/bin/activate"
    fi
    
    # Test Python imports
    if python -c "import fastapi, PyQt5, serial, numpy, scipy, control" 2>/dev/null; then
        log_success "All dependencies are working correctly"
    else
        log_error "Some dependencies failed to import"
        log_info "You may need to install additional system packages"
    fi
    
    # Test agent startup (dry run)
    if [ -f "local_agent/main.py" ]; then
        # This would test the actual agent if we had the full code
        log_success "Agent files are present"
    fi
}

# Print final instructions
print_final_instructions() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    Installation Complete!                   ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Installation Location:${NC} $AGENT_DIR"
    echo ""
    echo -e "${BLUE}To start the CtrlHub Desktop Agent:${NC}"
    
    case "$PLATFORM" in
        "windows")
            echo "  Double-click: $AGENT_DIR\\ctrlhub-agent.bat"
            echo "  Or from Command Prompt: cd \"$AGENT_DIR\" && ctrlhub-agent.bat"
            ;;
        *)
            echo "  Run: $AGENT_DIR/ctrlhub-agent.sh"
            echo "  Or use the desktop shortcut"
            if grep -q "ctrlhub-agent" "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.bash_profile" 2>/dev/null; then
                echo "  Or simply: ctrlhub-agent (after restarting terminal)"
            fi
            ;;
    esac
    
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo "  1. Connect your Arduino board via USB"
    echo "  2. Start the CtrlHub Desktop Agent"
    echo "  3. Open CtrlHub in your web browser"
    echo "  4. The web interface will automatically detect the local agent"
    echo ""
    echo -e "${BLUE}Troubleshooting:${NC}"
    echo "  - Ensure your Arduino has the CtrlHub firmware uploaded"
    echo "  - Check that no other programs are using the Arduino's serial port"
    echo "  - Make sure the agent is running before opening CtrlHub web interface"
    echo ""
    echo -e "${BLUE}For support and documentation:${NC}"
    echo "  Visit: https://ctrlhub.edu/docs"
    echo ""
}

# Cleanup function
cleanup() {
    if [ $? -ne 0 ]; then
        log_error "Installation failed!"
        echo ""
        echo "If you continue to have issues:"
        echo "  1. Check that Python $PYTHON_MIN_VERSION+ is installed and in PATH"
        echo "  2. Ensure you have internet connection for downloading dependencies"
        echo "  3. Try running the installer with administrator/sudo privileges"
        echo "  4. Check the installation log above for specific error messages"
        echo ""
    fi
}

# Set trap for cleanup
trap cleanup EXIT

# Main installation flow
main() {
    echo "Platform detected: $PLATFORM"
    echo ""
    
    # Pre-installation checks
    check_python
    check_pip
    
    # Installation steps
    create_install_dir
    create_virtual_env
    install_agent_files
    create_launchers
    create_desktop_shortcut
    add_to_path
    test_installation
    
    # Success!
    print_final_instructions
    
    # Remove error trap since we succeeded
    trap - EXIT
}

# Ask for confirmation before starting
echo -e "${YELLOW}This installer will:${NC}"
echo "  1. Create installation directory: $AGENT_DIR"
echo "  2. Set up Python virtual environment"
echo "  3. Install required Python packages"
echo "  4. Create launcher scripts"
echo "  5. Add desktop shortcuts"
echo ""
read -p "Continue with installation? [Y/n]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    log_info "Installation cancelled by user"
    exit 0
fi

# Start installation
main