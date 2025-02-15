import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from ..framework import BaseModule, ScanTarget, ScanResult

class DarkWebModule(BaseModule):
    """
    Dark Web Monitoring Module for ethical security research.
    This module focuses on:
    - Data breach monitoring
    - Credential leak detection
    - Threat intelligence gathering
    - Dark web mention monitoring
    
    Note: This module uses only legitimate APIs and public breach databases
    to ensure ethical operation.
    """

    @property
    def module_name(self) -> str:
        return "dark_web"

    async def run(self, target: ScanTarget) -> ScanResult:
        """Execute all dark web monitoring methods."""
        try:
            self.logger.info(f"Starting dark web monitoring for {target.domain}")
            
            # Initialize monitoring tasks
            breach_task = asyncio.create_task(self._check_data_breaches(target))
            paste_task = asyncio.create_task(self._monitor_paste_sites(target))
            forum_task = asyncio.create_task(self._scan_security_forums(target))
            market_task = asyncio.create_task(self._monitor_markets(target))

            # Gather all results
            breach_data = await breach_task
            paste_data = await paste_task
            forum_data = await forum_task
            market_data = await market_task

            # Compile all findings
            data = {
                'breaches': breach_data,
                'pastes': paste_data,
                'forum_mentions': forum_data,
                'market_mentions': market_data,
                'analysis': await self._analyze_findings(
                    breach_data, paste_data, forum_data, market_data
                )
            }

            return ScanResult(target=target, module_name=self.module_name, data=data)

        except Exception as e:
            self.logger.error(f"Error in dark web monitoring: {str(e)}")
            return ScanResult(
                target=target,
                module_name=self.module_name,
                data={},
                status="error",
                error=str(e)
            )

    async def _check_data_breaches(self, target: ScanTarget) -> Dict[str, Any]:
        """Check for data breaches using legitimate breach databases."""
        breaches = {
            'known_breaches': [],
            'potential_exposures': [],
            'last_checked': datetime.now().isoformat()
        }

        try:
            # Check HaveIBeenPwned API
            hibp_key = self.config.get_api_key('haveibeenpwned')
            if hibp_key:
                async with aiohttp.ClientSession() as session:
                    headers = {
                        'hibp-api-key': hibp_key,
                        'user-agent': 'OSINT-Framework-Research'
                    }
                    url = f"https://haveibeenpwned.com/api/v3/breaches"
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            all_breaches = await response.json()
                            domain_breaches = [
                                breach for breach in all_breaches
                                if target.domain in breach.get('Domain', '')
                            ]
                            breaches['known_breaches'].extend(domain_breaches)

            # Check other legitimate breach databases
            additional_sources = [
                self._check_security_scorecard(target),
                self._check_risk_recon(target),
                self._check_recorded_future(target)
            ]
            
            additional_results = await asyncio.gather(*additional_sources)
            for result in additional_results:
                if result.get('breaches'):
                    breaches['known_breaches'].extend(result['breaches'])
                if result.get('potential'):
                    breaches['potential_exposures'].extend(result['potential'])

        except Exception as e:
            self.logger.error(f"Error checking breaches: {str(e)}")
            breaches['error'] = str(e)

        return breaches

    async def _monitor_paste_sites(self, target: ScanTarget) -> Dict[str, Any]:
        """Monitor paste sites for leaked data."""
        paste_data = {
            'recent_pastes': [],
            'historical_pastes': [],
            'monitoring_status': 'active'
        }

        try:
            # Check public paste sites through legitimate APIs
            async with aiohttp.ClientSession() as session:
                # Monitor legitimate paste search engines
                searches = [
                    self._search_pastebin(session, target),
                    self._search_ghostbin(session, target),
                    self._search_archive_sites(session, target)
                ]
                
                results = await asyncio.gather(*searches)
                
                for result in results:
                    if result.get('recent'):
                        paste_data['recent_pastes'].extend(result['recent'])
                    if result.get('historical'):
                        paste_data['historical_pastes'].extend(result['historical'])

        except Exception as e:
            self.logger.error(f"Error monitoring paste sites: {str(e)}")
            paste_data['error'] = str(e)

        return paste_data

    async def _scan_security_forums(self, target: ScanTarget) -> Dict[str, Any]:
        """Scan security research forums for mentions."""
        forum_data = {
            'mentions': [],
            'discussions': [],
            'research_posts': []
        }

        try:
            # Scan legitimate security forums and research communities
            async with aiohttp.ClientSession() as session:
                forums = [
                    'https://www.reddit.com/r/netsec',
                    'https://www.reddit.com/r/InfoSecNews',
                    'https://community.riskiq.com'
                ]

                for forum in forums:
                    try:
                        async with session.get(
                            f"{forum}/search.json?q={target.domain}"
                        ) as response:
                            if response.status == 200:
                                data = await response.json()
                                forum_data['mentions'].extend(
                                    self._process_forum_data(data, forum)
                                )
                    except Exception as e:
                        self.logger.error(f"Error scanning forum {forum}: {str(e)}")

        except Exception as e:
            self.logger.error(f"Error scanning security forums: {str(e)}")
            forum_data['error'] = str(e)

        return forum_data

    async def _monitor_markets(self, target: ScanTarget) -> Dict[str, Any]:
        """Monitor security marketplaces for mentions."""
        market_data = {
            'mentions': [],
            'listings': [],
            'last_checked': datetime.now().isoformat()
        }

        try:
            # Use legitimate threat intelligence platforms
            platforms = [
                self._check_recorded_future_marketplace(target),
                self._check_flashpoint_marketplace(target),
                self._check_digital_shadows_marketplace(target)
            ]

            results = await asyncio.gather(*platforms)
            
            for result in results:
                if result.get('mentions'):
                    market_data['mentions'].extend(result['mentions'])
                if result.get('listings'):
                    market_data['listings'].extend(result['listings'])

        except Exception as e:
            self.logger.error(f"Error monitoring markets: {str(e)}")
            market_data['error'] = str(e)

        return market_data

    async def _analyze_findings(
        self,
        breach_data: Dict[str, Any],
        paste_data: Dict[str, Any],
        forum_data: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze and correlate all findings."""
        analysis = {
            'risk_score': 0,
            'summary': [],
            'recommendations': [],
            'timeline': [],
            'statistics': {}
        }

        try:
            # Calculate risk score based on findings
            risk_factors = {
                'recent_breaches': len(breach_data.get('known_breaches', [])) * 10,
                'paste_exposure': len(paste_data.get('recent_pastes', [])) * 5,
                'forum_mentions': len(forum_data.get('mentions', [])) * 2,
                'market_mentions': len(market_data.get('mentions', [])) * 8
            }
            
            analysis['risk_score'] = min(sum(risk_factors.values()), 100)

            # Generate timeline of events
            all_events = []
            all_events.extend(self._events_from_breaches(breach_data))
            all_events.extend(self._events_from_pastes(paste_data))
            all_events.extend(self._events_from_forums(forum_data))
            
            analysis['timeline'] = sorted(
                all_events,
                key=lambda x: x['date'],
                reverse=True
            )

            # Generate recommendations based on findings
            analysis['recommendations'] = self._generate_recommendations(
                breach_data,
                paste_data,
                forum_data,
                market_data
            )

            # Calculate statistics
            analysis['statistics'] = {
                'total_breaches': len(breach_data.get('known_breaches', [])),
                'total_pastes': len(paste_data.get('recent_pastes', [])),
                'total_mentions': len(forum_data.get('mentions', [])),
                'exposure_trend': self._calculate_exposure_trend(analysis['timeline'])
            }

        except Exception as e:
            self.logger.error(f"Error analyzing findings: {str(e)}")
            analysis['error'] = str(e)

        return analysis

    def _calculate_exposure_trend(self, timeline: List[Dict[str, Any]]) -> str:
        """Calculate the trend of exposures over time."""
        if not timeline:
            return "insufficient_data"

        try:
            # Group events by month
            months = {}
            for event in timeline:
                month = event['date'][:7]  # YYYY-MM format
                months[month] = months.get(month, 0) + 1

            # Calculate trend
            sorted_months = sorted(months.items())
            if len(sorted_months) < 2:
                return "insufficient_data"

            recent_events = sum(count for _, count in sorted_months[-3:])
            older_events = sum(count for _, count in sorted_months[:-3])

            if recent_events > older_events * 1.5:
                return "increasing"
            elif recent_events * 1.5 < older_events:
                return "decreasing"
            else:
                return "stable"

        except Exception:
            return "calculation_error"

    def _generate_recommendations(self, *data_sources) -> List[str]:
        """Generate security recommendations based on findings."""
        recommendations = set()

        for source in data_sources:
            if source.get('known_breaches'):
                recommendations.add(
                    "Implement regular security assessments and penetration testing"
                )
                recommendations.add(
                    "Review and update incident response procedures"
                )
            
            if source.get('recent_pastes') or source.get('mentions'):
                recommendations.add(
                    "Enhance monitoring of public data exposure"
                )
                recommendations.add(
                    "Implement data loss prevention (DLP) solutions"
                )

        return sorted(list(recommendations))
