import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from bs4 import BeautifulSoup
import aiohttp
from datetime import datetime

from src.osint.framework import ScanTarget, ScanResult
from src.osint.modules.passive import PassiveReconModule
from src.osint.modules.active import ActiveReconModule
from src.osint.modules.social import SocialMediaModule
from src.osint.modules.dark import DarkWebModule
from src.osint.utils.helpers import NetworkUtils, WebUtils, SecurityUtils

# Fixture for configuration
@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    config = Mock()
    config.get_api_key.return_value = "test-api-key"
    config.config = {
        'scan_options': {
            'timeout': 30,
            'threads': 5,
            'max_subdomains': 100,
            'ports': [80, 443, 8080]
        }
    }
    return config

# Fixture for scan target
@pytest.fixture
def scan_target():
    """Create a test scan target."""
    return ScanTarget(
        domain="example.com",
        ip_addresses=["93.184.216.34"],
        subdomains=["www.example.com", "api.example.com"]
    )

class TestPassiveReconModule:
    """Test suite for passive reconnaissance module."""

    @pytest.mark.asyncio
    async def test_whois_lookup(self, mock_config, scan_target):
        """Test WHOIS information gathering."""
        module = PassiveReconModule(mock_config)
        
        with patch('whois.whois') as mock_whois:
            mock_whois.return_value = Mock(
                registrar="Test Registrar",
                creation_date="2020-01-01",
                expiration_date="2025-01-01",
                name_servers=["ns1.example.com"]
            )
            
            result = await module._get_whois_info(scan_target.domain)
            assert result['registrar'] == "Test Registrar"
            assert "2020-01-01" in str(result['creation_date'])

    @pytest.mark.asyncio
    async def test_dns_records(self, mock_config, scan_target):
        """Test DNS record gathering."""
        module = PassiveReconModule(mock_config)
        
        with patch('dns.resolver.Resolver') as mock_resolver:
            mock_resolver.return_value.resolve.return_value = [
                Mock(to_text=lambda: "93.184.216.34")
            ]
            
            result = await module._get_dns_records(scan_target.domain)
            assert 'A' in result
            assert isinstance(result['A'], list)

    @pytest.mark.asyncio
    async def test_full_scan(self, mock_config, scan_target):
        """Test complete passive reconnaissance scan."""
        module = PassiveReconModule(mock_config)
        result = await module.run(scan_target)
        
        assert isinstance(result, ScanResult)
        assert result.module_name == "passive_recon"
        assert result.target == scan_target

class TestActiveReconModule:
    """Test suite for active reconnaissance module."""

    @pytest.mark.asyncio
    async def test_port_scanning(self, mock_config, scan_target):
        """Test port scanning functionality."""
        module = ActiveReconModule(mock_config)
        
        with patch('nmap.PortScanner') as mock_scanner:
            mock_scanner.return_value.scan.return_value = {
                'scan': {
                    '93.184.216.34': {
                        'tcp': {
                            80: {'state': 'open', 'name': 'http'},
                            443: {'state': 'open', 'name': 'https'}
                        }
                    }
                }
            }
            
            result = await module._scan_ports(scan_target)
            assert isinstance(result, dict)
            assert 'ports' in result

    @pytest.mark.asyncio
    async def test_web_technology_detection(self, mock_config, scan_target):
        """Test web technology detection."""
        module = ActiveReconModule(mock_config)
        
        mock_response = Mock()
        mock_response.text = "<html><head><script src='jquery.min.js'></script></head></html>"
        mock_response.headers = {'Server': 'nginx'}
        
        with patch('aiohttp.ClientSession.get', return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_response)
        )):
            result = await module._analyze_web_presence(scan_target)
            assert isinstance(result, dict)
            assert 'technologies' in result.get('http', {})

class TestSocialMediaModule:
    """Test suite for social media analysis module."""

    @pytest.mark.asyncio
    async def test_profile_discovery(self, mock_config, scan_target):
        """Test social media profile discovery."""
        module = SocialMediaModule(mock_config)
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(
            return_value="<html><body>Company Profile</body></html>"
        )
        
        with patch('aiohttp.ClientSession.get', return_value=mock_response):
            result = await module._find_profiles(scan_target)
            assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_mention_analysis(self, mock_config, scan_target):
        """Test social media mention analysis."""
        module = SocialMediaModule(mock_config)
        
        with patch.object(module, '_search_platform_mentions', return_value=[]):
            result = await module._analyze_mentions(scan_target)
            assert isinstance(result, dict)
            assert 'mentions' in result

class TestDarkWebModule:
    """Test suite for dark web monitoring module."""

    @pytest.mark.asyncio
    async def test_breach_detection(self, mock_config, scan_target):
        """Test data breach detection."""
        module = DarkWebModule(mock_config)
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=[
            {"Name": "Test Breach", "Domain": "example.com"}
        ])
        
        with patch('aiohttp.ClientSession.get', return_value=mock_response):
            result = await module._check_data_breaches(scan_target)
            assert isinstance(result, dict)
            assert 'known_breaches' in result

    @pytest.mark.asyncio
    async def test_paste_monitoring(self, mock_config, scan_target):
        """Test paste site monitoring."""
        module = DarkWebModule(mock_config)
        
        with patch.object(module, '_search_pastebin', return_value={'recent': []}):
            result = await module._monitor_paste_sites(scan_target)
            assert isinstance(result, dict)
            assert 'recent_pastes' in result

class TestHelperFunctions:
    """Test suite for helper utilities."""

    @pytest.mark.asyncio
    async def test_domain_validation(self):
        """Test domain validation functionality."""
        assert await NetworkUtils.is_valid_domain("example.com") == True
        assert await NetworkUtils.is_valid_domain("invalid@domain") == False

    @pytest.mark.asyncio
    async def test_web_technology_detection(self):
        """Test web technology detection."""
        html = """
        <html>
            <head>
                <script src="jquery.min.js"></script>
                <meta name="generator" content="WordPress" />
            </head>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        headers = {'Server': 'nginx'}
        
        result = await WebUtils.get_web_technologies(soup, headers)
        assert isinstance(result, dict)
        assert 'server' in result
        assert 'javascript_libraries' in result

    @pytest.mark.asyncio
    async def test_ssl_certificate_analysis(self):
        """Test SSL certificate analysis."""
        with patch('socket.create_connection'), \
             patch('ssl.create_default_context'):
            result = await SecurityUtils.analyze_ssl_cert("example.com")
            assert isinstance(result, dict)
            assert 'valid' in result

if __name__ == '__main__':
    pytest.main([__file__])