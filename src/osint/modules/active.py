import asyncio
import aiohttp
import socket
import nmap
from typing import Dict, Any, List
from bs4 import BeautifulSoup
from ..framework import BaseModule, ScanTarget, ScanResult
from ..utils.helpers import get_web_technologies

class ActiveReconModule(BaseModule):
    """
    Active Reconnaissance Module for direct interaction with target systems.
    This module performs:
    - Port scanning
    - Service identification
    - Web technology detection
    - Basic vulnerability assessment
    """

    @property
    def module_name(self) -> str:
        return "active_recon"

    async def run(self, target: ScanTarget) -> ScanResult:
        """Execute all active reconnaissance methods."""
        try:
            self.logger.info(f"Starting active reconnaissance for {target.domain}")
            
            # Get target IP if not already available
            if not target.ip_addresses:
                ip = await asyncio.to_thread(socket.gethostbyname, target.domain)
                target.ip_addresses = [ip]

            # Run active recon tasks
            ports_task = asyncio.create_task(self._scan_ports(target))
            web_task = asyncio.create_task(self._analyze_web_presence(target))
            vuln_task = asyncio.create_task(self._check_vulnerabilities(target))

            # Gather results
            ports_info = await ports_task
            web_info = await web_task
            vuln_info = await vuln_task

            data = {
                'port_scan': ports_info,
                'web_technologies': web_info,
                'vulnerabilities': vuln_info
            }

            return ScanResult(target=target, module_name=self.module_name, data=data)

        except Exception as e:
            self.logger.error(f"Error in active reconnaissance: {str(e)}")
            return ScanResult(
                target=target,
                module_name=self.module_name,
                data={},
                status="error",
                error=str(e)
            )

    async def _scan_ports(self, target: ScanTarget) -> Dict[str, Any]:
        """Perform port scanning and service detection."""
        try:
            # Initialize scanner
            scanner = nmap.PortScanner()
            
            # Get scan options from config
            scan_options = self.config.config['scan_options'].get('ports', {})
            port_range = scan_options.get('range', '21-443')
            
            # Perform scan using asyncio.to_thread for CPU-bound operation
            scan_arguments = f'-sS -sV -p{port_range} -T4'
            results = await asyncio.to_thread(
                scanner.scan,
                target.ip_addresses[0],
                arguments=scan_arguments
            )

            # Process results
            scan_data = {}
            if target.ip_addresses[0] in scanner.all_hosts():
                host_data = scanner[target.ip_addresses[0]]
                scan_data = {
                    'status': host_data.state(),
                    'ports': {
                        port: {
                            'state': data['state'],
                            'service': data['name'],
                            'product': data.get('product', ''),
                            'version': data.get('version', '')
                        }
                        for port, data in host_data['tcp'].items()
                    }
                }

            return scan_data

        except Exception as e:
            self.logger.error(f"Port scanning failed: {str(e)}")
            return {'error': str(e)}

    async def _analyze_web_presence(self, target: ScanTarget) -> Dict[str, Any]:
        """Analyze web technologies and server information."""
        results = {}
        
        async with aiohttp.ClientSession() as session:
            for protocol in ['http', 'https']:
                url = f"{protocol}://{target.domain}"
                try:
                    async with session.get(url, timeout=10) as response:
                        # Get headers
                        headers = dict(response.headers)
                        
                        # Get page content
                        content = await response.text()
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Use helper to detect technologies
                        technologies = await get_web_technologies(soup, headers)
                        
                        results[protocol] = {
                            'status_code': response.status,
                            'server': headers.get('Server', ''),
                            'technologies': technologies,
                            'headers': headers
                        }
                except Exception as e:
                    self.logger.error(f"Web analysis failed for {url}: {str(e)}")
                    results[protocol] = {'error': str(e)}
        
        return results

    async def _check_vulnerabilities(self, target: ScanTarget) -> Dict[str, Any]:
        """Perform basic vulnerability checks."""
        vulnerabilities = {}
        
        # Check for common security headers
        async with aiohttp.ClientSession() as session:
            try:
                url = f"https://{target.domain}"
                async with session.get(url) as response:
                    headers = response.headers
                    security_headers = {
                        'Strict-Transport-Security': headers.get('Strict-Transport-Security'),
                        'Content-Security-Policy': headers.get('Content-Security-Policy'),
                        'X-Frame-Options': headers.get('X-Frame-Options'),
                        'X-XSS-Protection': headers.get('X-XSS-Protection'),
                        'X-Content-Type-Options': headers.get('X-Content-Type-Options')
                    }
                    
                    vulnerabilities['missing_security_headers'] = [
                        header for header, value in security_headers.items()
                        if not value
                    ]
            except Exception as e:
                self.logger.error(f"Security header check failed: {str(e)}")
        
        return vulnerabilities
