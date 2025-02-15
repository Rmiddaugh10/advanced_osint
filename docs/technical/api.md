# OSINT Framework API Documentation

The OSINT Framework provides a comprehensive API that allows you to integrate its capabilities into your own applications and workflows. This documentation explains how to use the API effectively, with practical examples and best practices.

## Getting Started with the API

The framework's API is designed to be intuitive and easy to use while providing powerful functionality. Here's a basic example of how to use the API:

```python
from osint.framework import OSINTFramework, ScanTarget

async def perform_scan():
    # Initialize the framework
    framework = OSINTFramework()
    
    # Create a scan target
    target = ScanTarget(domain="example.com")
    
    # Perform the scan
    results = await framework.scan(target)
    
    # Process results
    print(f"Scan completed with status: {results.status}")
    for module_result in results.module_results:
        print(f"Module {module_result.module_name}: {module_result.status}")
```

## Core API Components

### The OSINTFramework Class

The main entry point for the API is the OSINTFramework class. It provides several key methods:

```python
class OSINTFramework:
    async def scan(self, target: ScanTarget) -> ScanResult:
        """Perform a complete scan of the target."""
        pass
    
    async def scan_with_modules(
        self, 
        target: ScanTarget, 
        modules: List[str]
    ) -> ScanResult:
        """Perform a scan using specific modules."""
        pass
    
    def get_available_modules(self) -> List[str]:
        """Get a list of available modules."""
        pass
    
    def configure_module(
        self, 
        module_name: str, 
        config: Dict[str, Any]
    ) -> None:
        """Configure a specific module."""
        pass
```

### Data Models

The API uses several data models to structure information:

```python
@dataclass
class ScanTarget:
    domain: str
    ip_addresses: Optional[List[str]] = None
    subdomains: Optional[List[str]] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class ScanResult:
    target: ScanTarget
    module_name: str
    data: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "success"
    error: Optional[str] = None
```

## API Integration Examples

### Basic Integration

Here's how to integrate the framework into your application:

```python
from osint.framework import OSINTFramework
import asyncio

class SecurityScanner:
    def __init__(self):
        self.framework = OSINTFramework()
    
    async def scan_domain(self, domain: str) -> Dict[str, Any]:
        target = ScanTarget(domain=domain)
        results = await self.framework.scan(target)
        return self._process_results(results)
    
    def _process_results(self, results: ScanResult) -> Dict[str, Any]:
        return {
            'domain': results.target.domain,
            'findings': results.data,
            'timestamp': results.timestamp
        }

# Usage
scanner = SecurityScanner()
results = asyncio.run(scanner.scan_domain("example.com"))
```

### Custom Module Integration

You can integrate custom modules through the API:

```python
from osint.framework import BaseModule, register_module

@register_module
class CustomModule(BaseModule):
    @property
    def module_name(self) -> str:
        return "custom_module"
    
    async def run(self, target: ScanTarget) -> ScanResult:
        # Custom implementation
        data = await self._gather_custom_data(target)
        return ScanResult(target=target, module_name=self.module_name, data=data)

# Usage with framework
framework = OSINTFramework()
framework.register_module(CustomModule)
```

## API Webhooks

The framework supports webhooks for event notifications:

```python
from osint.framework import OSINTFramework, WebhookHandler

class CustomWebhookHandler(WebhookHandler):
    async def on_scan_complete(self, result: ScanResult):
        # Handle scan completion
        await self._notify_security_team(result)
    
    async def on_error(self, error: Exception):
        # Handle errors
        await self._log_error(error)

# Usage
framework = OSINTFramework()
framework.set_webhook_handler(CustomWebhookHandler())
```

## Batch Processing API

For handling multiple targets efficiently:

```python
async def batch_scan(domains: List[str]) -> Dict[str, ScanResult]:
    framework = OSINTFramework()
    results = {}
    
    async def scan_single(domain: str):
        target = ScanTarget(domain=domain)
        results[domain] = await framework.scan(target)
    
    # Create tasks for all domains
    tasks = [scan_single(domain) for domain in domains]
    
    # Run scans concurrently
    await asyncio.gather(*tasks)
    return results

# Usage
domains = ["example1.com", "example2.com", "example3.com"]
batch_results = asyncio.run(batch_scan(domains))
```

## API Rate Limiting

The API includes built-in rate limiting:

```python
from osint.framework import RateLimiter

class CustomRateLimiter(RateLimiter):
    async def acquire(self):
        """Custom rate limiting logic."""
        await self._check_limits()
        await self._update_counters()
    
    async def release(self):
        """Release rate limit slot."""
        await self._decrease_counters()

# Usage
framework = OSINTFramework()
framework.set_rate_limiter(CustomRateLimiter(
    requests_per_second=10,
    burst_limit=20
))
```

## Error Handling

The API provides comprehensive error handling:

```python
from osint.framework import OSINTError, ModuleError

async def safe_scan(domain: str) -> Dict[str, Any]:
    try:
        framework = OSINTFramework()
        result = await framework.scan(ScanTarget(domain=domain))
        return result.data
    except OSINTError as e:
        # Handle framework-level errors
        logger.error(f"Framework error: {str(e)}")
        raise
    except ModuleError as e:
        # Handle module-specific errors
        logger.error(f"Module error in {e.module_name}: {str(e)}")
        raise
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error: {str(e)}")
        raise
```

## API Best Practices

1. Always use async/await properly:
```python
# Good
async def scan_domain(domain: str):
    async with OSINTFramework() as framework:
        return await framework.scan(ScanTarget(domain=domain))

# Bad
def scan_domain(domain: str):
    framework = OSINTFramework()
    return framework.scan(ScanTarget(domain=domain))  # Wrong!
```

2. Implement proper error handling:
```python
try:
    result = await framework.scan(target)
except OSINTError as e:
    # Handle framework errors
    pass
except Exception as e:
    # Handle unexpected errors
    pass
```

3. Use resource cleanup:
```python
async with OSINTFramework() as framework:
    result = await framework.scan(target)
    # Resources are automatically cleaned up
```

4. Implement rate limiting:
```python
framework = OSINTFramework()
framework.configure_rate_limits(
    requests_per_second=10,
    burst_limit=20
)
```

Remember to check the framework's documentation for updates and new features as they become available. The API is continuously evolving to provide better functionality and improved performance.
