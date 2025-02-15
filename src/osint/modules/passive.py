import asyncio
import dns.resolver
import whois
import ssl
import socket
import OpenSSL
from datetime import datetime
from typing import Dict, Any, List
import aiohttp
from ..framework import BaseModule, ScanTarget, ScanResult

class PassiveReconModule(BaseModule):
    """
    Passive Reconnaissance Module for gathering information without directly
    interacting with the target systems. This module performs:
    - WHOIS lookups
    - DNS enumeration
    - SSL/TLS certificate analysis
    - Subdomain discovery through passive means
    """

    @property
    def module_name(self) -> str:
        return "passive_recon"

    async def run(self, target: ScanTarget) -> ScanResult:
        """Execute all passive reconnaissance methods."""
        try:
            self.logger.info(f"Starting passive reconnaissance for {target.domain}")
            
            # Run all passive recon tasks concurrently
            whois_task = asyncio.create_task(self._get_whois_info(target.domain))
            dns_task = asyncio.create_task(self._get_dns_records(target.domain))
            ssl_task = asyncio.create_task(self._get_ssl_info(target.domain))
            subdomain_task = asyncio.create_task(self._discover_subdomains(target.domain))

            # Gather all results
            whois_info = await whois_task
            dns_records = await dns_task
            ssl_info = await ssl_task
            subdomains = await subdomain_task

            data = {
                'whois_information': whois_info,
                'dns_records': dns_records,
                'ssl_certificate': ssl_info,
                'discovered_subdomains': subdomains
            }

            return ScanResult(target=target, module_name=self.module_name, data=data)

        except Exception as e:
            self.logger.error(f"Error in passive reconnaissance: {str(e)}")
            return ScanResult(
                target=target,
                module_name=self.module_name,
                data={},
                status="error",
                error=str(e)
            )

    async def _get_whois_info(self, domain: str) -> Dict[str, Any]:
        """Retrieve WHOIS information for the domain."""
        try:
            # Use asyncio.to_thread for CPU-bound WHOIS lookup
            w = await asyncio.to_thread(whois.whois, domain)
            return {
                'registrar': w.registrar,
                'creation_date': str(w.creation_date),
                'expiration_date': str(w.expiration_date),
                'name_servers': w.name_servers,
                'status': w.status,
                'emails': w.emails,
                'org': w.org
            }
        except Exception as e:
            self.logger.error(f"WHOIS lookup failed: {str(e)}")
            return {'error': str(e)}

    async def _get_dns_records(self, domain: str) -> Dict[str, List[str]]:
        """Gather DNS records for the domain."""
        records = {}
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME']
        
        for record_type in record_types:
            try:
                resolver = dns.resolver.Resolver()
                answers = await asyncio.to_thread(resolver.resolve, domain, record_type)
                records[record_type] = [str(answer) for answer in answers]
            except Exception as e:
                self.logger.debug(f"No {record_type} records found: {str(e)}")
                records[record_type] = []
        
        return records

    async def _get_ssl_info(self, domain: str) -> Dict[str, Any]:
        """Analyze SSL/TLS certificate information."""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
            return {
                'subject': dict(x[0] for x in cert['subject']),
                'issuer': dict(x[0] for x in cert['issuer']),
                'version': cert['version'],
                'serial_number': cert['serialNumber'],
                'not_before': cert['notBefore'],
                'not_after': cert['notAfter'],
                'san': cert.get('subjectAltName', [])
            }
        except Exception as e:
            self.logger.error(f"SSL certificate analysis failed: {str(e)}")
            return {'error': str(e)}

    async def _discover_subdomains(self, domain: str) -> List[str]:
        """Discover subdomains through passive means."""
        subdomains = set()
        
        # Check Certificate Transparency logs
        async with aiohttp.ClientSession() as session:
            try:
                url = f"https://crt.sh/?q=%.{domain}&output=json"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        for entry in data:
                            name = entry['name_value'].lower()
                            # Split by newlines and commas (crt.sh sometimes returns multiple domains)
                            for subdomain in name.replace('*', '').split('\n'):
                                for sub in subdomain.split(','):
                                    if sub.strip().endswith(domain):
                                        subdomains.add(sub.strip())
            except Exception as e:
                self.logger.error(f"Subdomain discovery failed: {str(e)}")
        
        return sorted(list(subdomains))
