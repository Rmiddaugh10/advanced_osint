# OSINT Framework Modules

This document provides a comprehensive guide to understanding, using, and creating modules for the OSINT Framework. The module system is designed to be flexible, extensible, and powerful while maintaining ease of use.

## Understanding Modules

Modules are the building blocks of the OSINT Framework. Each module is designed to perform a specific type of reconnaissance or analysis task. The framework comes with several core modules:

### Core Modules Overview

#### 1. Passive Reconnaissance Module
This module gathers information without directly interacting with the target:

```python
class PassiveReconModule(BaseModule):
    async def run(self, target: ScanTarget) -> ScanResult:
        data = {
            'whois': await self._get_whois_info(target.domain),
            'dns_records': await self._get_dns_records(target.domain),
            'certificate_info': await self._get_certificate_info(target.domain)
        }
        return ScanResult(target=target, module_name=self.module_name, data=data)
```

Key features:
- WHOIS information gathering
- DNS record enumeration
- SSL/TLS certificate analysis
- Subdomain discovery

#### 2. Active Reconnaissance Module
This module performs direct interaction with the target:

```python
class ActiveReconModule(BaseModule):
    async def run(self, target: ScanTarget) -> ScanResult:
        data = {
            'open_ports': await self._scan_ports(target),
            'vulnerabilities': await self._scan_vulnerabilities(target),
            'technologies': await self._detect_technologies(target)
        }
        return ScanResult(target=target, module_name=self.module_name, data=data)
```

Key features:
- Port scanning
- Service detection
- Technology fingerprinting
- Basic vulnerability assessment

#### 3. Social Media Module
This module analyzes social media presence:

```python
class SocialMediaModule(BaseModule):
    async def run(self, target: ScanTarget) -> ScanResult:
        data = {
            'profiles': await self._find_profiles(target),
            'mentions': await self._gather_mentions(target),
            'related_accounts': await self._find_related_accounts(target)
        }
        return ScanResult(target=target, module_name=self.module_name, data=data)
```

Key features:
- Profile discovery
- Mention monitoring
- Network analysis
- Content analysis

#### 4. Dark Web Module
This module performs dark web monitoring:

```python
class DarkWebModule(BaseModule):
    async def run(self, target: ScanTarget) -> ScanResult:
        data = {
            'leaks': await self._search_leaks(target),
            'mentions': await self._search_mentions(target),
            'related_data': await self._gather_related_data(target)
        }
        return ScanResult(target=target, module_name=self.module_name, data=data)
```

Key features:
- Data breach monitoring
- Dark web mention tracking
- Credential leak detection
- Threat intelligence gathering

## Creating Custom Modules

### Basic Module Structure

To create a custom module, extend the BaseModule class:

```python
from osint.framework import BaseModule, ScanTarget, ScanResult

class CustomModule(BaseModule):
    @property
    def module_name(self) -> str:
        return "custom_module"

    async def run(self, target: ScanTarget) -> ScanResult:
        try:
            # Implement your scanning logic here
            data = await self._gather_custom_data(target)
            return ScanResult(
                target=target,
                module_name=self.module_name,
                data=data
            )
        except Exception as e:
            return ScanResult(
                target=target,
                module_name=self.module_name,
                data={},
                status="error",
                error=str(e)
            )
```

### Module Development Guidelines

#### 1. Configuration Management
Handle module configuration properly:

```python
class CustomModule(BaseModule):
    def __init__(self, config):
        super().__init__(config)
        self.custom_setting = self.config.get('custom_module', {}).get(
            'custom_setting', 'default_value'
        )
```

#### 2. Error Handling
Implement comprehensive error handling:

```python
async def _gather_custom_data(self, target: ScanTarget) -> Dict[str, Any]:
    try:
        # Your data gathering logic
        pass
    except ConnectionError as e:
        self.logger.error(f"Connection error: {str(e)}")
        raise
    except TimeoutError as e:
        self.logger.error(f"Timeout error: {str(e)}")
        raise
    except Exception as e:
        self.logger.error(f"Unexpected error: {str(e)}")
        raise
```

#### 3. Resource Management
Properly manage resources:

```python
async def _gather_custom_data(self, target: ScanTarget) -> Dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        try:
            # Use session for HTTP requests
            pass
        finally:
            # Cleanup any resources
            pass
```

### Module Integration

#### 1. Registration
Register your module with the framework:

```python
# In your module file
from osint.framework import register_module

@register_module
class CustomModule(BaseModule):
    pass
```

#### 2. Configuration
Add module configuration to config.yaml:

```yaml
modules:
  custom_module:
    enabled: true
    custom_setting: value
    rate_limit: 100
```

#### 3. Testing
Create tests for your module:

```python
class TestCustomModule:
    @pytest.mark.asyncio
    async def test_custom_module(self, mock_config):
        module = CustomModule(mock_config)
        result = await module.run(ScanTarget("example.com"))
        assert result.status == "success"
        assert "expected_key" in result.data
```

## Module Best Practices

### 1. Performance Optimization

Optimize your module's performance:

```python
class OptimizedModule(BaseModule):
    def __init__(self, config):
        super().__init__(config)
        self._cache = {}

    async def _gather_data(self, target: ScanTarget) -> Dict[str, Any]:
        cache_key = f"{target.domain}:{self.module_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        data = await self._fetch_data(target)
        self._cache[cache_key] = data
        return data
```

### 2. Rate Limiting

Implement proper rate limiting:

```python
from asyncio import sleep

class RateLimitedModule(BaseModule):
    async def _rate_limited_request(self, url: str) -> Dict[str, Any]:
        await sleep(1 / self.config.get('rate_limit', 10))
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()
```

### 3. Documentation

Document your module thoroughly:

```python
class WellDocumentedModule(BaseModule):
    """
    A well-documented custom module for the OSINT Framework.

    This module performs specific reconnaissance tasks by:
    1. Gathering initial data
    2. Processing the information
    3. Analyzing the results

    Configuration Options:
        - option1: Description of option1
        - option2: Description of option2

    Example Usage:
        module = WellDocumentedModule(config)
        result = await module.run(target)
    """
```

## Advanced Module Features

### 1. Event System

Implement event handling:

```python
class EventAwareModule(BaseModule):
    async def run(self, target: ScanTarget) -> ScanResult:
        self.emit_event('scan_started', target)
        try:
            result = await self._perform_scan(target)
            self.emit_event('scan_completed', result)
            return result
        except Exception as e:
            self.emit_event('scan_error', e)
            raise
```

### 2. Pipelines

Create processing pipelines:

```python
class PipelineModule(BaseModule):
    async def run(self, target: ScanTarget) -> ScanResult:
        data = await self._gather_raw_data(target)
        processed_data = await self._process_data(data)
        analyzed_data = await self._analyze_data(processed_data)
        return ScanResult(target=target, data=analyzed_data)
```

### 3. Integration Points

Provide integration capabilities:

```python
class IntegratedModule(BaseModule):
    async def run(self, target: ScanTarget) -> ScanResult:
        # Support external tool integration
        external_results = await self._run_external_tool(target)
        
        # Support API integration
        api_results = await self._query_external_api(target)
        
        # Combine results
        combined_results = self._merge_results(
            external_results,
            api_results
        )
        
        return ScanResult(target=target, data=combined_results)
```

Remember to follow these guidelines when developing modules to ensure consistency, reliability, and maintainability of the OSINT Framework.
