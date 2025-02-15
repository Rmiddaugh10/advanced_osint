#!/usr/bin/env python3

from abc import ABC, abstractmethod
import argparse
import asyncio
import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import yaml

# Core data structures
@dataclass
class ScanTarget:
    domain: str
    ip_addresses: List[str] = None
    subdomains: List[str] = None
    timestamp: str = datetime.now().isoformat()

@dataclass
class ScanResult:
    target: ScanTarget
    module_name: str
    data: Dict[str, Any]
    timestamp: str = datetime.now().isoformat()
    status: str = "success"
    error: Optional[str] = None

class ConfigManager:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> dict:
        if not os.path.exists(self.config_path):
            return self._create_default_config()
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def _create_default_config(self) -> dict:
        config = {
            'api_keys': {
                'shodan': '',
                'virustotal': '',
                'censys': ''
            },
            'modules': {
                'passive_recon': True,
                'active_recon': True,
                'social_media': True,
                'dark_web': False
            },
            'scan_options': {
                'timeout': 30,
                'threads': 5,
                'max_subdomains': 100
            },
            'output': {
                'format': 'json',
                'directory': 'results'
            }
        }
        
        with open(self.config_path, 'w') as f:
            yaml.dump(config, f)
        
        return config

    def get_api_key(self, service: str) -> str:
        return self.config['api_keys'].get(service, '')

class BaseModule(ABC):
    def __init__(self, config: ConfigManager):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def run(self, target: ScanTarget) -> ScanResult:
        pass

    @property
    @abstractmethod
    def module_name(self) -> str:
        pass

class PassiveReconModule(BaseModule):
    @property
    def module_name(self) -> str:
        return "passive_recon"

    async def run(self, target: ScanTarget) -> ScanResult:
        try:
            # Implement passive reconnaissance logic
            data = {
                'whois': await self._get_whois(target.domain),
                'dns_records': await self._get_dns_records(target.domain),
                'certificate_info': await self._get_certificate_info(target.domain)
            }
            return ScanResult(target=target, module_name=self.module_name, data=data)
        except Exception as e:
            return ScanResult(
                target=target,
                module_name=self.module_name,
                data={},
                status="error",
                error=str(e)
            )

    async def _get_whois(self, domain: str) -> dict:
        # Implement WHOIS lookup
        pass

    async def _get_dns_records(self, domain: str) -> dict:
        # Implement DNS record gathering
        pass

    async def _get_certificate_info(self, domain: str) -> dict:
        # Implement certificate analysis
        pass

class ActiveReconModule(BaseModule):
    @property
    def module_name(self) -> str:
        return "active_recon"

    async def run(self, target: ScanTarget) -> ScanResult:
        try:
            data = {
                'open_ports': await self._scan_ports(target),
                'vulnerabilities': await self._scan_vulnerabilities(target),
                'technologies': await self._detect_technologies(target)
            }
            return ScanResult(target=target, module_name=self.module_name, data=data)
        except Exception as e:
            return ScanResult(
                target=target,
                module_name=self.module_name,
                data={},
                status="error",
                error=str(e)
            )

class SocialMediaModule(BaseModule):
    @property
    def module_name(self) -> str:
        return "social_media"

    async def run(self, target: ScanTarget) -> ScanResult:
        try:
            data = {
                'profiles': await self._find_profiles(target),
                'mentions': await self._gather_mentions(target),
                'related_accounts': await self._find_related_accounts(target)
            }
            return ScanResult(target=target, module_name=self.module_name, data=data)
        except Exception as e:
            return ScanResult(
                target=target,
                module_name=self.module_name,
                data={},
                status="error",
                error=str(e)
            )

class DarkWebModule(BaseModule):
    @property
    def module_name(self) -> str:
        return "dark_web"

    async def run(self, target: ScanTarget) -> ScanResult:
        try:
            data = {
                'leaks': await self._search_leaks(target),
                'mentions': await self._search_mentions(target),
                'related_data': await self._gather_related_data(target)
            }
            return ScanResult(target=target, module_name=self.module_name, data=data)
        except Exception as e:
            return ScanResult(
                target=target,
                module_name=self.module_name,
                data={},
                status="error",
                error=str(e)
            )

class ResultsManager:
    def __init__(self, config: ConfigManager):
        self.config = config
        self.results_dir = config.config['output']['directory']
        os.makedirs(self.results_dir, exist_ok=True)

    def save_results(self, results: List[ScanResult], target: ScanTarget):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.results_dir}/osint_{target.domain}_{timestamp}.json"
        
        output = {
            'target': asdict(target),
            'scan_results': [asdict(result) for result in results],
            'metadata': {
                'timestamp': timestamp,
                'framework_version': '1.0.0'
            }
        }

        with open(filename, 'w') as f:
            json.dump(output, f, indent=4)
        
        return filename

class OSINTFramework:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = ConfigManager(config_path)
        self.results_manager = ResultsManager(self.config)
        
        # Initialize modules
        self.modules = []
        if self.config.config['modules']['passive_recon']:
            self.modules.append(PassiveReconModule(self.config))
        if self.config.config['modules']['active_recon']:
            self.modules.append(ActiveReconModule(self.config))
        if self.config.config['modules']['social_media']:
            self.modules.append(SocialMediaModule(self.config))
        if self.config.config['modules']['dark_web']:
            self.modules.append(DarkWebModule(self.config))

    async def scan(self, domain: str) -> str:
        target = ScanTarget(domain=domain)
        results = []

        for module in self.modules:
            result = await module.run(target)
            results.append(result)

        return self.results_manager.save_results(results, target)

def main():
    parser = argparse.ArgumentParser(description='Advanced OSINT Framework')
    parser.add_argument('domain', help='Target domain to investigate')
    parser.add_argument('--config', default='config.yaml', help='Path to configuration file')
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Run the framework
    framework = OSINTFramework(args.config)
    result_file = asyncio.run(framework.scan(args.domain))
    print(f"\n[+] Scan completed. Results saved to: {result_file}")

if __name__ == "__main__":
    main()
