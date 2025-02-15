# Advanced OSINT Framework

A comprehensive Open Source Intelligence (OSINT) framework designed for security research and digital investigation. This framework provides modular, extensible capabilities for gathering and analyzing information from various sources.

## Features

- Modular architecture supporting multiple reconnaissance methods
- Asynchronous execution for improved performance
- Comprehensive configuration system
- Structured result storage and management
- Multiple specialized modules:
  - Passive Reconnaissance
  - Active Scanning
  - Social Media Analysis
  - Dark Web Monitoring

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/advanced-osint.git
cd advanced-osint
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
```

4. Configure your settings:
Copy `config.yaml.example` to `config.yaml` and add your API keys and preferences:
```bash
cp config.yaml.example config.yaml
```

## Usage

Basic usage with default configuration:
```bash
python -m src.osint.framework example.com
```

Using a custom configuration file:
```bash
python -m src.osint.framework example.com --config custom_config.yaml
```

## Module Overview

### Passive Reconnaissance
- WHOIS information gathering
- DNS record enumeration
- SSL/TLS certificate analysis

### Active Reconnaissance
- Port scanning
- Vulnerability assessment
- Technology stack detection

### Social Media Analysis
- Profile discovery
- Mention monitoring
- Related account finding

### Dark Web Monitoring
- Data leak detection
- Dark web mention tracking
- Related information gathering

## Configuration

The `config.yaml` file controls the framework's behavior. Key configuration sections:

```yaml
api_keys:
  shodan: 'your-api-key'
  virustotal: 'your-api-key'
  censys: 'your-api-key'

modules:
  passive_recon: true
  active_recon: true
  social_media: true
  dark_web: false

scan_options:
  timeout: 30
  threads: 5
  max_subdomains: 100
```

## Development

To add a new module:

1. Create a new module file in `src/osint/modules/`
2. Inherit from `BaseModule`
3. Implement required methods
4. Add module configuration to `config.yaml`

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

Run specific tests:
```bash
python -m pytest tests/test_config.py
```

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Security Considerations

This tool is designed for legal and ethical use only. Always ensure you have permission to scan any targets and comply with all applicable laws and regulations.
