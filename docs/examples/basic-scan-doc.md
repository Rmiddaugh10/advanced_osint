# Basic Scanning with OSINT Framework

This guide will walk you through performing basic scans using the OSINT Framework. We'll start with simple examples and gradually move to more complex scenarios, explaining each step along the way to ensure you understand the full capabilities of the framework.

## Your First Scan

Let's begin with the simplest possible scan. This example will help you understand the basic workflow of the framework:

```python
from osint.framework import OSINTFramework

# Initialize the framework
framework = OSINTFramework()

# Perform a basic scan
async def basic_scan():
    # The framework will automatically handle all the complexity
    # of running different modules and gathering information
    result = await framework.scan("example.com")
    print(f"Scan completed: {result.status}")
    
    # View the results in a structured way
    if result.status == "success":
        print("\nFindings:")
        for module_name, data in result.data.items():
            print(f"\n{module_name} Results:")
            print(json.dumps(data, indent=2))

# Run the scan
import asyncio
asyncio.run(basic_scan())
```

When you run this code, the framework performs several actions:
1. Initializes all default modules for comprehensive scanning
2. Performs passive reconnaissance without directly interacting with the target
3. Gathers basic information about the target's infrastructure
4. Organizes and saves the results in a structured format

## Understanding Scan Results

Let's examine the structure of scan results in detail:

```python
async def examine_results():
    result = await framework.scan("example.com")
    
    # Basic information about the scan
    print(f"Target: {result.target.domain}")
    print(f"Scan Time: {result.timestamp}")
    print(f"Status: {result.status}")
    
    # Let's look at module-specific results
    if result.data.get('passive_recon'):
        whois_data = result.data['passive_recon'].get('whois', {})
        print("\nWHOIS Information:")
        print(f"Registrar: {whois_data.get('registrar')}")
        print(f"Creation Date: {whois_data.get('creation_date')}")
        print(f"Expiration Date: {whois_data.get('expiration_date')}")
        print(f"Name Servers: {', '.join(whois_data.get('name_servers', []))}")
    
    if result.data.get('active_recon'):
        ports = result.data['active_recon'].get('open_ports', [])
        print("\nOpen Ports:", ', '.join(map(str, ports)))
        
        technologies = result.data['active_recon'].get('technologies', {})
        print("\nDetected Technologies:")
        for tech_type, tech_list in technologies.items():
            print(f"{tech_type}: {', '.join(tech_list)}")
```

## Configuring Your Scan

You can customize how the scan operates to match your specific needs. Here's a detailed example with common configurations:

```python
async def configured_scan():
    # Create a comprehensive custom configuration
    config = {
        'modules': {
            'passive_recon': {
                'enabled': True,
                'subdomain_enumeration': True,
                'dns_analysis': True
            },
            'active_recon': {
                'enabled': True,
                'port_scan': True,
                'service_detection': True
            },
            'social_media': {
                'enabled': False
            },
            'dark_web': {
                'enabled': False
            }
        },
        'scan_options': {
            'timeout': 30,
            'max_subdomains': 100,
            'ports': [80, 443, 8080, 8443],
            'threads': 5,
            'retry_count': 3
        },
        'output': {
            'format': 'json',
            'directory': 'scan_results',
            'detailed': True
        }
    }
    
    # Initialize framework with custom config
    framework = OSINTFramework(config_path="custom_config.yaml")
    
    # Perform the configured scan
    result = await framework.scan("example.com")
    
    # Process and analyze the detailed results
    await process_scan_results(result)

async def process_scan_results(result):
    """Process and analyze scan results in detail."""
    if result.status == "success":
        # Create a structured summary
        summary = {
            'scan_time': result.timestamp,
            'target_info': {
                'domain': result.target.domain,
                'ip_addresses': result.target.ip_addresses,
                'subdomains': len(result.target.subdomains or [])
            },
            'findings': {
                'critical': [],
                'high': [],
                'medium': [],
                'low': []
            }
        }

        # Analyze each module's results
        for module_name, data in result.data.items():
            await analyze_module_data(module_name, data, summary)

        # Generate detailed report
        await generate_scan_report(summary)
```

## Working with Multiple Targets

Here's how to efficiently scan multiple targets while managing resources and handling errors:

```python
async def multi_target_scan():
    # Define your targets with optional metadata
    targets = [
        {"domain": "example1.com", "priority": "high"},
        {"domain": "example2.com", "priority": "medium"},
        {"domain": "example3.com", "priority": "low"}
    ]
    
    # Create a semaphore to limit concurrent scans
    sem = asyncio.Semaphore(5)  # Limit to 5 concurrent scans
    
    async def scan_with_limit(target_info):
        """Perform scan with rate limiting and error handling."""
        async with sem:
            try:
                domain = target_info["domain"]
                print(f"Starting scan of {domain} (Priority: {target_info['priority']})")
                
                result = await framework.scan(domain)
                
                # Process results based on priority
                await process_priority_results(result, target_info['priority'])
                
                return result
            except Exception as e:
                print(f"Error scanning {domain}: {str(e)}")
                return None
    
    # Create tasks for each target
    tasks = [scan_with_limit(target) for target in targets]
    
    # Run all scans with proper concurrency management
    results = await asyncio.gather(*tasks)
    
    # Analyze and correlate results
    await analyze_multiple_scan_results(results)
```

## Real-World Security Assessment

Here's a complete example that demonstrates how to perform a thorough security assessment:

```python
async def security_assessment():
    """Perform a comprehensive security assessment."""
    
    # Initialize with detailed configuration
    config = {
        'modules': {
            'passive_recon': {
                'enabled': True,
                'subdomain_enumeration': True,
                'dns_analysis': True,
                'ssl_analysis': True
            },
            'active_recon': {
                'enabled': True,
                'port_scan': True,
                'service_detection': True,
                'vulnerability_scan': True
            },
            'social_media': {
                'enabled': True,
                'platforms': ['linkedin', 'twitter', 'github']
            },
            'dark_web': {
                'enabled': True,
                'breach_detection': True
            }
        },
        'scan_options': {
            'timeout': 60,
            'max_subdomains': 500,
            'ports': [21, 22, 23, 25, 80, 443, 8080, 8443],
            'subdomain_enumeration': True,
            'screenshot_enabled': True,
            'risk_assessment': True
        }
    }
    
    framework = OSINTFramework(config)
    target = "example.com"
    
    try:
        # Phase 1: Initial Reconnaissance
        print(f"Starting passive reconnaissance for {target}")
        passive_result = await framework.scan_with_modules(target, ['passive_recon'])
        
        # Phase 2: Infrastructure Analysis
        subdomains = passive_result.data.get('passive_recon', {}).get('subdomains', [])
        print(f"Found {len(subdomains)} subdomains")
        
        # Phase 3: Detailed Scanning
        scan_results = []
        for subdomain in subdomains:
            print(f"Analyzing subdomain: {subdomain}")
            result = await framework.scan(subdomain)
            scan_results.append(result)
        
        # Phase 4: Risk Analysis
        risk_assessment = await analyze_security_risks(scan_results)
        
        # Phase 5: Report Generation
        report = await generate_security_report(target, scan_results, risk_assessment)
        
        # Save detailed findings
        await save_assessment_results(report)
        
    except Exception as e:
        print(f"Assessment error: {str(e)}")
        await handle_assessment_error(e)

async def analyze_security_risks(results):
    """Analyze security risks from scan results."""
    risk_assessment = {
        'critical_risks': [],
        'high_risks': [],
        'medium_risks': [],
        'low_risks': [],
        'recommendations': []
    }
    
    for result in results:
        # Analyze various security aspects
        await analyze_infrastructure_risks(result, risk_assessment)
        await analyze_application_risks(result, risk_assessment)
        await analyze_configuration_risks(result, risk_assessment)
        
        # Generate recommendations
        await generate_risk_recommendations(result, risk_assessment)
    
    return risk_assessment

async def generate_security_report(target, results, risk_assessment):
    """Generate a comprehensive security assessment report."""
    report = {
        'executive_summary': {
            'target': target,
            'scan_date': datetime.now().isoformat(),
            'risk_level': calculate_overall_risk(risk_assessment),
            'key_findings': summarize_key_findings(risk_assessment)
        },
        'technical_details': {
            'infrastructure': extract_infrastructure_details(results),
            'vulnerabilities': extract_vulnerability_details(results),
            'exposure': extract_exposure_details(results)
        },
        'recommendations': {
            'immediate_actions': generate_immediate_actions(risk_assessment),
            'short_term': generate_short_term_recommendations(risk_assessment),
            'long_term': generate_long_term_recommendations(risk_assessment)
        }
    }
    
    return report
```

This guide demonstrates the fundamental operations of the OSINT Framework while providing practical examples for real-world security assessments. Remember to always follow security best practices and ensure you have proper authorization before scanning any targets.

For more advanced usage, refer to our other documentation sections:
- Module Development Guide
- API Documentation
- Custom Workflows Guide
- Advanced Configuration Guide
