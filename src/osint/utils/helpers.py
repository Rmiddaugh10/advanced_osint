import asyncio
import re
import socket
import ssl
import ipaddress
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup
import dns.resolver
import tldextract

class NetworkUtils:
    """Utility functions for network operations and validation."""
    
    @staticmethod
    async def is_valid_domain(domain: str) -> bool:
        """
        Verify if a domain is valid and properly formatted.
        
        Args:
            domain: The domain name to validate
            
        Returns:
            bool: True if domain is valid, False otherwise
        """
        if not domain or len(domain) > 255:
            return False
            
        pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        if not re.match(pattern, domain):
            return False
            
        try:
            # Extract domain parts
            ext = tldextract.extract(domain)
            if not all([ext.domain, ext.suffix]):
                return False
                
            # Verify domain resolves
            await asyncio.get_event_loop().getaddrinfo(domain, None)
            return True
        except Exception:
            return False

    @staticmethod
    async def get_ip_info(ip: str) -> Dict[str, Any]:
        """
        Gather detailed information about an IP address.
        
        Args:
            ip: The IP address to analyze
            
        Returns:
            Dict containing IP information including geolocation and network details
        """
        info = {'ip': ip, 'type': None, 'details': {}}
        
        try:
            ip_obj = ipaddress.ip_address(ip)
            info['type'] = 'IPv6' if isinstance(ip_obj, ipaddress.IPv6Address) else 'IPv4'
            info['is_global'] = ip_obj.is_global
            info['is_private'] = ip_obj.is_private
            
            if ip_obj.is_global:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f'https://ipapi.co/{ip}/json/') as response:
                        if response.status == 200:
                            info['details'] = await response.json()
            
            return info
        except Exception as e:
            return {'ip': ip, 'error': str(e)}

class WebUtils:
    """Utilities for web-based operations and analysis."""
    
    @staticmethod
    async def get_web_technologies(soup: BeautifulSoup, headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Detect technologies used by a website based on HTML content and headers.
        
        Args:
            soup: BeautifulSoup object of the page
            headers: HTTP response headers
            
        Returns:
            Dict containing detected technologies and their details
        """
        technologies = {
            'server': headers.get('Server', 'Unknown'),
            'frameworks': [],
            'analytics': [],
            'cms': None,
            'javascript_libraries': []
        }
        
        # Detect JavaScript libraries
        script_patterns = {
            'jQuery': r'jquery.*\.js',
            'React': r'react.*\.js',
            'Vue.js': r'vue.*\.js',
            'Angular': r'angular.*\.js',
            'Bootstrap': r'bootstrap.*\.js'
        }
        
        scripts = soup.find_all('script', src=True)
        for script in scripts:
            src = script['src'].lower()
            for library, pattern in script_patterns.items():
                if re.search(pattern, src):
                    technologies['javascript_libraries'].append(library)
        
        # Detect CMS
        cms_patterns = {
            'WordPress': {'meta': {'name': 'generator', 'content': re.compile(r'WordPress')}},
            'Drupal': {'meta': {'name': 'generator', 'content': re.compile(r'Drupal')}},
            'Joomla': {'meta': {'name': 'generator', 'content': re.compile(r'Joomla')}}
        }
        
        for cms, patterns in cms_patterns.items():
            if soup.find('meta', patterns['meta']):
                technologies['cms'] = cms
                break
        
        # Detect analytics
        analytics_patterns = {
            'Google Analytics': r'google-analytics\.com|ga\.js',
            'Mixpanel': r'mixpanel\.com',
            'Hotjar': r'hotjar\.com'
        }
        
        scripts_text = ' '.join(str(script) for script in scripts)
        for analytics, pattern in analytics_patterns.items():
            if re.search(pattern, scripts_text):
                technologies['analytics'].append(analytics)
        
        return technologies

    @staticmethod
    async def extract_metadata(soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract metadata from HTML content.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            Dict containing extracted metadata
        """
        metadata = {
            'title': None,
            'description': None,
            'keywords': [],
            'author': None,
            'social_media': {},
            'emails': set(),
            'phone_numbers': set()
        }
        
        # Extract basic metadata
        title_tag = soup.find('title')
        metadata['title'] = title_tag.text.strip() if title_tag else None
        
        meta_tags = {
            'description': ('name', 'description'),
            'keywords': ('name', 'keywords'),
            'author': ('name', 'author')
        }
        
        for key, (attr, name) in meta_tags.items():
            meta = soup.find('meta', {attr: name})
            if meta and meta.get('content'):
                metadata[key] = meta['content']
                if key == 'keywords':
                    metadata[key] = [k.strip() for k in meta['content'].split(',')]
        
        # Extract social media links
        social_patterns = {
            'twitter': r'twitter\.com/([^/\s"\']+)',
            'facebook': r'facebook\.com/([^/\s"\']+)',
            'linkedin': r'linkedin\.com/(?:company|in)/([^/\s"\']+)',
            'instagram': r'instagram\.com/([^/\s"\']+)'
        }
        
        for platform, pattern in social_patterns.items():
            links = soup.find_all('a', href=re.compile(pattern))
            if links:
                metadata['social_media'][platform] = [
                    re.search(pattern, link['href']).group(1) for link in links
                ]
        
        # Extract emails and phone numbers
        text = soup.get_text()
        metadata['emails'] = set(
            re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        )
        metadata['phone_numbers'] = set(
            re.findall(r'\+?[\d\s-]{10,}', text)
        )
        
        return metadata

class SecurityUtils:
    """Security-related utility functions."""
    
    @staticmethod
    async def analyze_ssl_cert(domain: str) -> Dict[str, Any]:
        """
        Analyze SSL/TLS certificate of a domain.
        
        Args:
            domain: Domain to analyze
            
        Returns:
            Dict containing certificate information and analysis
        """
        cert_info = {
            'valid': False,
            'issuer': None,
            'subject': None,
            'expires': None,
            'version': None,
            'serial_number': None,
            'extensions': {},
            'issues': []
        }
        
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    cert_info.update({
                        'valid': True,
                        'issuer': dict(x[0] for x in cert['issuer']),
                        'subject': dict(x[0] for x in cert['subject']),
                        'expires': cert['notAfter'],
                        'version': cert['version'],
                        'serial_number': cert['serialNumber']
                    })
                    
                    # Check certificate issues
                    expiry = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    if expiry < datetime.now():
                        cert_info['issues'].append('Certificate expired')
                    
                    if 'subjectAltName' in cert:
                        cert_info['extensions']['san'] = cert['subjectAltName']
        
        except ssl.SSLError as e:
            cert_info['issues'].append(f'SSL Error: {str(e)}')
        except socket.gaierror as e:
            cert_info['issues'].append(f'DNS Error: {str(e)}')
        except Exception as e:
            cert_info['issues'].append(f'Error: {str(e)}')
        
        return cert_info

    @staticmethod
    def calculate_password_strength(password: str) -> Dict[str, Any]:
        """
        Calculate password strength and provide recommendations.
        
        Args:
            password: Password to analyze
            
        Returns:
            Dict containing password analysis and recommendations
        """
        analysis = {
            'length': len(password),
            'score': 0,
            'has_uppercase': bool(re.search(r'[A-Z]', password)),
            'has_lowercase': bool(re.search(r'[a-z]', password)),
            'has_numbers': bool(re.search(r'\d', password)),
            'has_symbols': bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password)),
            'recommendations': []
        }
        
        # Calculate base score
        if analysis['length'] >= 12:
            analysis['score'] += 40
        elif analysis['length'] >= 8:
            analysis['score'] += 25
        else:
            analysis['recommendations'].append('Password should be at least 12 characters long')
        
        # Add points for character types
        for key in ['has_uppercase', 'has_lowercase', 'has_numbers', 'has_symbols']:
            if analysis[key]:
                analysis['score'] += 15
            else:
                analysis['recommendations'].append(
                    f'Add {key.replace("has_", "")} to strengthen password'
                )
        
        # Check for common patterns
        if re.search(r'(.)\1{2,}', password):  # Repeated characters
            analysis['score'] -= 10
            analysis['recommendations'].append('Avoid repeated characters')
        
        if re.search(r'(123|abc|qwerty)', password.lower()):  # Common sequences
            analysis['score'] -= 15
            analysis['recommendations'].append('Avoid common sequences')
        
        # Normalize score
        analysis['score'] = max(0, min(100, analysis['score']))
        
        return analysis

class DataUtils:
    """Data processing and analysis utilities."""
    
    @staticmethod
    def normalize_domain(domain: str) -> str:
        """
        Normalize a domain name for consistent comparison.
        
        Args:
            domain: Domain name to normalize
            
        Returns:
            Normalized domain name
        """
        return domain.lower().strip().rstrip('.')

    @staticmethod
    def extract_iocs(text: str) -> Dict[str, Set[str]]:
        """
        Extract Indicators of Compromise (IoCs) from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict containing different types of IoCs
        """
        iocs = {
            'ipv4': set(),
            'ipv6': set(),
            'domains': set(),
            'urls': set(),
            'emails': set(),
            'md5': set(),
            'sha1': set(),
            'sha256': set()
        }
        
        # IP addresses
        iocs['ipv4'].update(
            re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text)
        )
        iocs['ipv6'].update(
            re.findall(r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b', text)
        )
        
        # Domains and URLs
        urls = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*', text)
        for url in urls:
            iocs['urls'].add(url)
            parsed = urlparse(url)
            if parsed.netloc:
                iocs['domains'].add(parsed.netloc)
        
        # Emails
        iocs['emails'].update(
            re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        )
        
        # Hashes
        iocs['md5'].update(re.findall(r'\b[a-fA-F0-9]{32}\b', text))
        iocs['sha1'].update(re.findall(r'\b[a-fA-F0-9]{40}\b', text))
        iocs['sha256'].update(re.findall(r'\b[a-fA-F0-9]{64}\b', text))
        
        return iocs

    @staticmethod
    def detect_anomalies(data: List[float], threshold: float = 2.0) -> List[Tuple[int, float]]:
        """
        Detect anomalies in numerical data using Z-score method.
        
        Args:
            data: List of numerical values
            threshold: Z-score threshold for anomaly detection
            
        Returns:
            List of tuples containing (index, value) of anomalies
        """
        if not data:
            return []
            
        mean = sum(data) / len(data)
        std = (sum((x - mean) ** 2 for x in data) / len(data)) ** 0.5
        
        anomalies = []
        for i, value in enumerate(data):
            z_score = (value - mean) / std if std > 0 else 0
            if abs(z_score) > threshold:
                anomalies.append((i, value))
                
        return anomalies
