#!/bin/bash
# Trinity Command Center - One-Click Installation

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║      TRINITY COMMAND CENTER - INSTALLATION WIZARD              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "This will install:"
echo "  🐍 Python dependencies (Streamlit, trimesh, psutil)"
echo "  🔧 OpenSCAD (CAD engine)"
echo "  📦 Additional libraries"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 1
fi

cd "$(dirname "$0")"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Installing Python Dependencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

pip3 install -r requirements_command_center.txt

echo ""
echo "✅ Python dependencies installed"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Installing OpenSCAD"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if command -v openscad &> /dev/null; then
    echo "✅ OpenSCAD already installed: $(which openscad)"
else
    echo "Installing OpenSCAD via Homebrew..."
    brew install --cask openscad
    echo "✅ OpenSCAD installed"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Creating Output Directories"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

mkdir -p cad_output/previews
mkdir -p email_drafts

echo "✅ Directories created"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4: Making Scripts Executable"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

chmod +x launch_command_center.sh
chmod +x install_command_center.sh

echo "✅ Scripts are executable"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 5: Testing Installation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Testing Streamlit..."
python3 -c "import streamlit; print(f'  ✅ Streamlit {streamlit.__version__}')"

echo "Testing OpenSCAD..."
openscad --version 2>&1 | head -1 | sed 's/^/  ✅ /'

echo "Testing trimesh..."
python3 -c "import trimesh; print('  ✅ trimesh ' + trimesh.__version__)"

echo "Testing psutil..."
python3 -c "import psutil; print('  ✅ psutil ' + psutil.__version__)"

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                   INSTALLATION COMPLETE! ✅                    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 Quick Start:"
echo ""
echo "  Launch Command Center:"
echo "    ./launch_command_center.sh"
echo ""
echo "  Access Points:"
echo "    Desktop:  http://localhost:8502"
echo "    Mobile:   http://$(tailscale ip -4 2>/dev/null || echo 'TAILSCALE-IP'):8502"
echo "    VR:       http://$(tailscale ip -4 2>/dev/null || echo 'TAILSCALE-IP'):8502?vr=true"
echo ""
echo "📖 Full documentation: COMMAND_CENTER_SETUP.md"
echo ""
echo "Ready to launch Trinity Command Center!"
echo ""
