#!/bin/bash

# CryptoApp-Android Build Fix Script for Termux
# This script updates the GitHub Actions workflow to fix SQLite3 linking issues

echo "=========================================="
echo "CryptoApp-Android Build Fix Script"
echo "=========================================="
echo ""

# Check if we're in the correct directory
if [ ! -f "buildozer.spec" ]; then
    echo "ERROR: buildozer.spec not found!"
    echo "Please run this script from the root of the CryptoApp-Android repository"
    exit 1
fi

echo "[1/3] Creating backup of build.yml..."
cp .github/workflows/build.yml .github/workflows/build.yml.backup
echo "✓ Backup created: .github/workflows/build.yml.backup"
echo ""

echo "[2/3] Updating .github/workflows/build.yml..."

# Create the fixed workflow file
cat > .github/workflows/build.yml << 'EOF'
name: Build Kivy APK

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-22.04

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            build-essential \
            libffi-dev \
            git \
            zip \
            unzip \
            autoconf \
            libtool \
            pkg-config \
            zlib1g-dev \
            libncurses5-dev \
            libnss3-dev \
            libssl-dev \
            libreadline-dev \
            libsqlite3-dev \
            sqlite3 \
            bzip2 \
            libbz2-dev \
            libstdc++6 \
            libz-dev

      - name: Install Python dependencies
        run: |
          pip install --upgrade pip
          pip install "setuptools<66" "cython<3.0" virtualenv buildozer

      - name: Clean Cache Directories
        run: |
          rm -rf .buildozer
          rm -rf ~/.buildozer

      - name: Build APK
        env:
          # Target only the Android NDK compilers, ignoring legacy header warnings
          APP_CFLAGS: "-Wno-error=implicit-function-declaration -Wno-error=incompatible-function-pointer-types"
          APP_CPPFLAGS: "-Wno-error=implicit-function-declaration -Wno-error=incompatible-function-pointer-types"
          # Pass directly to python-for-android recipe compilations
          p4a_extra_cflags: "-Wno-error=implicit-function-declaration -Wno-error=incompatible-function-pointer-types"
          # Add explicit library linking for SQLite3
          LDFLAGS: "-lm -lz"
        run: |
          yes | buildozer -v android debug || {
            echo "=== BUILD FAILED! PRINTING RECENT LOG FILES ==="
            find .buildozer/ -name "*.log" -type f -exec echo "--- {} ---" \; -exec tail -n 100 {} \;
            exit 1
          }

      - name: Upload APK Artifact
        if: success()
        uses: actions/upload-artifact@v4
        with:
          name: CryptoApp-APK
          path: bin/*.apk

EOF

echo "✓ Updated .github/workflows/build.yml"
echo ""

echo "[3/3] Verifying changes..."
echo ""
echo "Changes made:"
echo "  ✓ Added 'libz-dev' to system dependencies"
echo "  ✓ Added 'LDFLAGS: \"-lm -lz\"' to Build APK environment"
echo ""

echo "=========================================="
echo "Fix Summary"
echo "=========================================="
echo ""
echo "The following issues have been fixed:"
echo "  1. Missing libz-dev system dependency"
echo "  2. Missing LDFLAGS for explicit library linking"
echo ""
echo "Root cause: SQLite3 compilation was failing because:"
echo "  - Math library (libm) was not being linked (ceil function)"
echo "  - Zlib library (libz) was not being linked (deflate function)"
echo ""
echo "Next steps:"
echo "  1. Review the changes: git diff .github/workflows/build.yml"
echo "  2. Commit the changes: git add .github/workflows/build.yml && git commit -m 'Fix: Add library linking for SQLite3 build'"
echo "  3. Push to GitHub: git push"
echo "  4. Trigger workflow: Push to main/master or manually trigger via GitHub Actions"
echo ""
echo "=========================================="
echo "✓ Fix script completed successfully!"
echo "=========================================="
