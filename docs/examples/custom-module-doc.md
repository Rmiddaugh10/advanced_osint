# Creating Custom Modules for OSINT Framework

This guide will walk you through the process of creating custom modules for the OSINT Framework. We'll explore the architecture of modules, best practices for development, and provide practical examples that you can build upon for your own custom modules.

## Understanding Module Architecture

At its core, a module in the OSINT Framework is a specialized component designed to perform specific types of reconnaissance or analysis. Let's start by examining the basic structure of a module and then build up to more complex implementations.

### Basic Module Structure

Here's the fundamental structure of a custom module:

```python
from osint.framework import BaseModule, ScanTarget, ScanResult
from typing import Dict, Any

class CustomReconModule(BaseModule):
    """
    A custom reconnaissance module that demonstrates the basic structure
    of OSINT Framework modules. This module serves as a template for
    building more specialized functionality.
    """

    @property
    def module_name(self) -> str:
        """
        Provides a unique identifier for the module. This name will be used
        in configuration and results.
        """
        return "custom_recon"

    async def run(self, target: ScanTarget) -> ScanResult:
        """
        The main entry point for module execution. This method coordinates
        all the module's activities and returns consolidated results.
        """
        try:
            # Initialize our results container
            data = {
                'findings': [],
                'metadata': {},
                'analysis': {}
            }

            # Perform the primary reconnaissance steps
            basic_info = await self._gather_basic_info(target)
            detailed_info = await self._analyze_target(target, basic_info)
            
            # Compile our findings
            data['findings'] = basic_info
            data['analysis'] = detailed_info
            data['metadata'] = {
                'scan_time': self._get_scan_duration(),
                'methods_used': self._get_active_methods()
            }

            return ScanResult(
                target=target,
                module_name=self.module_name,
                data=data
            )

        except Exception as e:
            # Provide detailed error information for debugging
            self.logger.error(
                f"Error in {self.module_name}: {str(e)}",
                exc_info=True
            )
            return ScanResult(
                target=target,
                module_name=self.module_name,
                data={},
                status="error",
                error=str(e)
            )

    async def _gather_basic_info(self, target: ScanTarget) -> Dict[str, Any]:
        """
        Gathers fundamental information about the target. This method
        demonstrates proper error handling and resource management.
        """
        info = {}
        try:
            async with aiohttp.ClientSession() as session:
                # Implement your basic information gathering logic here
                # For example, checking domain information:
                async with session.get(
                    f"https://api.example.com/domain/{target.domain}"
                ) as response:
                    if response.status == 200:
                        info['domain_data'] = await response.json()
                        
            return info
            
        except aiohttp.ClientError as e:
            self.logger.warning(f"Network error during basic info gathering: {e}")
            return {'error': 'Network error during data collection'}
        except Exception as e:
            self.logger.error(f"Unexpected error in basic info gathering: {e}")
            raise

    async def _analyze_target(
        self,
        target: ScanTarget,
        basic_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Performs detailed analysis using the gathered basic information.
        This method shows how to build upon initial findings.
        """
        analysis_results = {
            'risk_factors': [],
            'recommendations': [],
            'technical_details': {}
        }

        try:
            # Implement your analysis logic here
            # For example, analyzing domain information:
            if 'domain_data' in basic_info:
                await self._analyze_domain_risks(
                    basic_info['domain_data'],
                    analysis_results
                )
                
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Error during target analysis: {e}")
            raise
```

### Building a Practical Custom Module

Let's create a more practical example: a module that analyzes SSL/TLS configurations and security headers:

```python
class SecurityHeaderModule(BaseModule):
    """
    A module that analyzes security headers and SSL/TLS configurations
    of web services. This practical example demonstrates real-world
    security analysis techniques.
    """

    @property
    def module_name(self) -> str:
        return "security_headers"

    async def run(self, target: ScanTarget) -> ScanResult:
        try:
            # Organize our analysis structure
            data = {
                'ssl_analysis': {},
                'security_headers': {},
                'recommendations': [],
                'risk_score': 0
            }

            # Perform our security analyses
            ssl_results = await self._analyze_ssl(target.domain)
            header_results = await self._check_security_headers(target.domain)
            
            # Calculate risk scores and generate recommendations
            risk_data = self._calculate_risks(ssl_results, header_results)
            
            # Compile all our findings
            data.update({
                'ssl_analysis': ssl_results,
                'security_headers': header_results,
                'recommendations': risk_data['recommendations'],
                'risk_score': risk_data['score']
            })

            return ScanResult(target=target, module_name=self.module_name, data=data)

        except Exception as e:
            self.logger.error(f"Error in security header analysis: {str(e)}")
            return ScanResult(
                target=target,
                module_name=self.module_name,
                data={},
                status="error",
                error=str(e)
            )

    async def _analyze_ssl(self, domain: str) -> Dict[str, Any]:
        """
        Analyzes SSL/TLS configuration of the target domain.
        """
        ssl_info = {
            'protocol_versions': [],
            'cipher_suites': [],
            'certificate_info': {},
            'vulnerabilities': []
        }

        try:
            # Create SSL context for analysis
            context = ssl.create_default_context()
            
            # Connect and analyze SSL configuration
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://{domain}") as response:
                    # Extract SSL information from connection
                    ssl_info['protocol_versions'].append(
                        response.connection.transport.get_extra_info('ssl_object').version()
                    )
                    
                    # Get certificate information
                    cert = response.connection.transport.get_extra_info('ssl_object').getpeercert()
                    ssl_info['certificate_info'] = self._parse_certificate(cert)

            return ssl_info

        except ssl.SSLError as e:
            self.logger.error(f"SSL Error: {str(e)}")
            ssl_info['vulnerabilities'].append(f"SSL Error: {str(e)}")
            return ssl_info
        except Exception as e:
            self.logger.error(f"Error in SSL analysis: {str(e)}")
            raise

    async def _check_security_headers(self, domain: str) -> Dict[str, Any]:
        """
        Analyzes security headers of the target domain.
        """
        headers_info = {
            'present_headers': {},
            'missing_headers': [],
            'header_analysis': {}
        }

        # Define expected security headers
        expected_headers = {
            'Strict-Transport-Security': self._analyze_hsts,
            'Content-Security-Policy': self._analyze_csp,
            'X-Frame-Options': self._analyze_xfo,
            'X-Content-Type-Options': self._analyze_xcto
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://{domain}") as response:
                    headers = response.headers
                    
                    # Analyze present headers
                    for header, analyzer in expected_headers.items():
                        if header in headers:
                            headers_info['present_headers'][header] = headers[header]
                            headers_info['header_analysis'][header] = await analyzer(
                                headers[header]
                            )
                        else:
                            headers_info['missing_headers'].append(header)

            return headers_info

        except Exception as e:
            self.logger.error(f"Error checking security headers: {str(e)}")
            raise

    def _calculate_risks(
        self,
        ssl_results: Dict[str, Any],
        header_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculates risk scores and generates recommendations based on findings.
        """
        risk_data = {
            'score': 0,
            'recommendations': []
        }

        # Analyze SSL risks
        if ssl_results.get('vulnerabilities'):
            risk_data['score'] += len(ssl_results['vulnerabilities']) * 10
            risk_data['recommendations'].extend([
                f"Fix SSL vulnerability: {vuln}"
                for vuln in ssl_results['vulnerabilities']
            ])

        # Analyze header risks
        for header in header_results.get('missing_headers', []):
            risk_data['score'] += 5
            risk_data['recommendations'].append(
                f"Implement missing security header: {header}"
            )

        # Normalize risk score
        risk_data['score'] = min(risk_data['score'], 100)

        return risk_data
```

### Module Integration and Testing

Here's how to properly test and integrate your custom module:

```python
import pytest
from unittest.mock import Mock, patch

class TestSecurityHeaderModule:
    """
    Test suite for the SecurityHeaderModule.
    """

    @pytest.fixture
    def module(self):
        """Create a module instance for testing."""
        config = Mock()
        config.get_api_key.return_value = "test-key"
        return SecurityHeaderModule(config)

    @pytest.mark.asyncio
    async def test_ssl_analysis(self, module):
        """Test SSL/TLS analysis functionality."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock SSL connection
            mock_get.return_value.__aenter__.return_value = Mock(
                connection=Mock(
                    transport=Mock(
                        get_extra_info=Mock(
                            return_value=Mock(
                                version=Mock(return_value='TLSv1.2'),
                                getpeercert=Mock(return_value={})
                            )
                        )
                    )
                )
            )
            
            result = await module._analyze_ssl("example.com")
            assert 'protocol_versions' in result
            assert 'certificate_info' in result

    @pytest.mark.asyncio
    async def test_security_headers(self, module):
        """Test security header analysis functionality."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value = Mock(
                headers={
                    'Strict-Transport-Security': 'max-age=31536000',
                    'Content-Security-Policy': "default-src 'self'"
                }
            )
            
            result = await module._check_security_headers("example.com")
            assert 'present_headers' in result
            assert 'missing_headers' in result
```

## Best Practices for Module Development

When developing custom modules, follow these guidelines to ensure reliability and maintainability:

1. Error Handling: Implement comprehensive error handling to ensure graceful failure:
```python
try:
    result = await self._perform_analysis()
except ConnectionError as e:
    self.logger.error(f"Connection error: {str(e)}")
    # Handle network errors appropriately
except TimeoutError as e:
    self.logger.error(f"Operation timed out: {str(e)}")
    # Handle timeout conditions
except Exception as e:
    self.logger.error(f"Unexpected error: {str(e)}")
    # Handle unexpected errors
```

2. Resource Management: Properly manage system resources:
```python
async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
        # Work with response
        pass  # Resources are automatically cleaned up
```

3. Configuration Management: Handle configuration properly:
```python
def __init__(self, config):
    super().__init__(config)
    self.timeout = self.config.get('timeout', 30)
    self.max_retries = self.config.get('max_retries', 3)
```

4. Documentation: Maintain clear documentation:
```python
class WellDocumentedModule(BaseModule):
    """
    A well-documented module that demonstrates proper documentation practices.

    This module performs specific analysis tasks including:
    1. Data gathering
    2. Analysis
    3. Risk assessment

    Configuration Options:
        - timeout: Maximum time for operations (default: 30s)
        - max_retries: Maximum retry attempts (default: 3)
    """
```

Your custom modules should enhance the framework's capabilities while maintaining its quality and reliability standards. Remember to thoroughly test your modules and document their functionality for other users.

