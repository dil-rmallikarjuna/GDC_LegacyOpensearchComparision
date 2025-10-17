# K6 Installation Guide

## Manual Installation (Recommended)

Since the automated installation is having issues, please install K6 manually:

### Option 1: Using Homebrew (Recommended)

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install K6
brew install k6

# Verify installation
k6 version
```

### Option 2: Direct Download

1. Visit: https://k6.io/docs/getting-started/installation/
2. Download the appropriate version for macOS ARM64
3. Extract the archive
4. Move the `k6` binary to `/usr/local/bin/`:
   ```bash
   sudo mv k6 /usr/local/bin/
   sudo chmod +x /usr/local/bin/k6
   ```

### Option 3: Using npm (Alternative)

```bash
# Install K6 via npm
npm install -g k6

# Add to PATH if needed
export PATH="/usr/local/lib/node_modules/k6/bin:$PATH"
```

## Verify Installation

After installation, verify K6 is working:

```bash
k6 version
```

You should see output like:
```
k6 v0.47.0 (go1.21.0, darwin/arm64)
```

## Test the Framework

Once K6 is installed, you can test the framework:

```bash
# Navigate to the k6-tests directory
cd k6-tests

# Run a quick smoke test
./run-tests.sh smoke

# Or run the demo
./demo.sh
```

## Troubleshooting

### K6 command not found

If you get "command not found" error:

1. Check if K6 is in your PATH:
   ```bash
   which k6
   ```

2. If not found, add it to your PATH:
   ```bash
   export PATH="/usr/local/bin:$PATH"
   ```

3. Or create a symlink:
   ```bash
   sudo ln -s /path/to/k6 /usr/local/bin/k6
   ```

### Permission denied

If you get permission errors:

```bash
sudo chmod +x /usr/local/bin/k6
```

### Architecture issues

Make sure you download the correct version for your system:
- macOS ARM64 (Apple Silicon): `k6-v0.47.0-macos-arm64.tar.gz`
- macOS Intel: `k6-v0.47.0-macos-amd64.tar.gz`

## Next Steps

Once K6 is installed:

1. **Run the demo**: `./demo.sh`
2. **Test the framework**: `./run-tests.sh smoke`
3. **Read the documentation**: `README.md`
4. **Customize configuration**: Edit `config/k6-config.js`

## Support

If you continue to have issues:

1. Check the official K6 documentation: https://k6.io/docs/
2. Visit the K6 GitHub repository: https://github.com/grafana/k6
3. Check the K6 community forum: https://community.k6.io/
