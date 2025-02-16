# OSINT Framework Installation Guide

This guide will walk you through the process of installing and setting up the OSINT framework on your system. I'll explain each step in detail and provide solutions for common issues you might encounter.

## System Requirements

Before we begin the installation, ensure your system meets these minimum requirements:

- Python 3.8 or higher
- 4GB RAM (8GB recommended for larger scans)
- Operating System: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+ recommended)
- Internet connection for downloading dependencies and performing scans

## Basic Installation

Let's go through the installation process step by step.

### 1. Setting Up Python

First, ensure you have Python 3.8 or higher installed:

```bash
python --version
```

If you need to install Python, you can download it from (python.org)[python.org] or use your system's package manager:

For Ubuntu/Debian:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

For macOS (using Homebrew):
```bash
brew install python
```

### 2. Creating a Virtual Environment

It's recommended to use a virtual environment to keep your project dependencies isolated:

```bash
# Create a new directory for your project
mkdir osint-project
cd osint-project

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Installing the Framework

Now you can install the OSINT framework using pip:

```bash
# Install the basic package
pip install osint-framework

# For development (includes testing tools)
pip install osint-framework[dev]

# For documentation
pip install osint-framework[docs]
```

### 4. System Dependencies

Some features require additional system packages:

For Ubuntu/Debian:
```bash
sudo apt install nmap libssl-dev libffi-dev build-essential
```

For macOS:
```bash
brew install nmap openssl
```

For Windows:
- Download and install Nmap from (nmap.org)[nmap.org]
- Install Build Tools for Visual Studio

## Advanced Installation

### Installing from Source

If you want to contribute or modify the framework:

```bash
# Clone the repository
git clone https://github.com/yourusername/osint-framework.git
cd osint-framework

# Install in development mode
pip install -e .[dev]
```

### Docker Installation

For containerized deployment:

```bash
# Build the Docker image
docker build -t osint-framework .

# Run the container
docker run -it --name osint osint-framework
```

## Configuration Setup

After installation, you'll need to set up your configuration:

1. Create a configuration directory:
```bash
mkdir ~/.osint-framework
```

2. Copy the default configuration:
```bash
cp config.yaml.example ~/.osint-framework/config.yaml
```

3. Edit the configuration with your API keys:
```bash
# Use your favorite text editor
nano ~/.osint-framework/config.yaml
```

## Verifying Installation

To verify your installation:

```bash
# Activate your virtual environment if not already active
source venv/bin/activate

# Run the test suite
pytest

# Try a basic scan
osint-scan example.com
```

## Common Issues and Solutions

### SSL Certificate Errors

If you encounter SSL certificate errors:

```bash
# Update certificates
pip install --upgrade certifi
```

### Permission Issues

For Linux/macOS systems, if you encounter permission errors:

```bash
# Fix permissions on the configuration directory
chmod 700 ~/.osint-framework
chmod 600 ~/.osint-framework/config.yaml
```

### Module Import Errors

If you see import errors:

```bash
# Verify PYTHONPATH
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

## Updating the Framework

To update to the latest version:

```bash
pip install --upgrade osint-framework
```

## Development Setup

For developers, additional setup is recommended:

```bash
# Install development tools
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Set up documentation tools
pip install -e .[docs]
```

## Getting Help

If you encounter any issues:

1. Check the troubleshooting guide in the documentation
2. Open an issue on GitHub
3. Join our community Discord server (coming soon)
4. Email support at (hguaddim@gmail.com)[hguaddim@gmail.com]

Remember to keep your installation updated and regularly check for security advisories related to the dependencies.
