#!/bin/bash

echo "=================================================="
echo "   POV UGC Video Generator - Setup Script"
echo "=================================================="
echo ""

# Check if running on Mac
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "This setup script is for Mac only."
    echo "For Windows, please follow the manual instructions in README.md"
    exit 1
fi

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew is not installed. Installing Homebrew..."
    echo "(You may be asked for your password)"
    echo ""
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Add Homebrew to PATH for Apple Silicon Macs
    if [[ -f "/opt/homebrew/bin/brew" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
else
    echo "[OK] Homebrew is already installed"
fi

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo ""
    echo "Installing FFmpeg (this may take a few minutes)..."
    brew install ffmpeg
else
    echo "[OK] FFmpeg is already installed"
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo ""
    echo "Installing Python 3..."
    brew install python3
else
    echo "[OK] Python 3 is already installed"
fi

# Create folder structure
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo ""
echo "Creating folder structure..."

mkdir -p "$SCRIPT_DIR/input/intro"
mkdir -p "$SCRIPT_DIR/input/memes"
mkdir -p "$SCRIPT_DIR/input/outro"
mkdir -p "$SCRIPT_DIR/output"

echo "[OK] Created input/intro folder"
echo "[OK] Created input/memes folder"
echo "[OK] Created input/outro folder"
echo "[OK] Created output folder"

# Make the main script executable
chmod +x "$SCRIPT_DIR/generate_videos.py"

echo ""
echo "=================================================="
echo "   Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Add your videos to the folders:"
echo "   - input/intro/  -> Your wake-up clip (1 video)"
echo "   - input/memes/  -> All your meme clips (as many as you want)"
echo "   - input/outro/  -> Your screen-time-block clip (1 video)"
echo ""
echo "2. Run the generator:"
echo "   python3 generate_videos.py"
echo ""
echo "3. Find your videos in the 'output' folder!"
echo ""
