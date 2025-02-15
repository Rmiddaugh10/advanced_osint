import asyncio
import aiohttp
import re
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from datetime import datetime
from ..framework import BaseModule, ScanTarget, ScanResult

class SocialMediaModule(BaseModule):
    """
    Social Media Analysis Module for discovering and analyzing social media presence.
    This module performs:
    - Social media profile discovery
    - Mention monitoring
    - Related account finding
    - Basic social media content analysis
    """

    @property
    def module_name(self) -> str:
        return "social_media"

    async def run(self, target: ScanTarget) -> ScanResult:
        """Execute all social media analysis methods."""
        try:
            self.logger.info(f"Starting social media analysis for {target.domain}")
            
            # Run social media tasks concurrently
            profiles_task = asyncio.create_task(self._find_profiles(target))
            mentions_task = asyncio.create_task(self._analyze_mentions(target))
            metadata_task = asyncio.create_task(self._gather_metadata(target))
            employees_task = asyncio.create_task(self._find_employees(target))

            # Gather results
            profiles = await profiles_task
            mentions = await mentions_task
            metadata = await metadata_task
            employees = await employees_task

            data = {
                'profiles': profiles,
                'mentions': mentions,
                'metadata': metadata,
                'employees': employees
            }

            return ScanResult(target=target, module_name=self.module_name, data=data)

        except Exception as e:
            self.logger.error(f"Error in social media analysis: {str(e)}")
            return ScanResult(
                target=target,
                module_name=self.module_name,
                data={},
                status="error",
                error=str(e)
            )

    async def _find_profiles(self, target: ScanTarget) -> Dict[str, Any]:
        """Find social media profiles associated with the domain."""
        profiles = {}
        platforms = {
            'twitter': {
                'url': f"https://twitter.com/search?q={target.domain}",
                'selectors': {
                    'profile': 'div[data-testid="UserCell"]',
                    'name': 'div[data-testid="UserName"]',
                    'bio': 'div[data-testid="UserDescription"]'
                }
            },
            'linkedin': {
                'url': f"https://www.linkedin.com/company/{target.domain.split('.')[0]}",
                'selectors': {
                    'profile': '.org-top-card',
                    'name': '.org-top-card-summary__title',
                    'description': '.org-top-card-summary__info'
                }
            },
            'github': {
                'url': f"https://github.com/search?q={target.domain}&type=users",
                'selectors': {
                    'profile': '.user-list-item',
                    'name': '.user-list-info',
                    'bio': '.user-list-bio'
                }
            }
        }

        async with aiohttp.ClientSession() as session:
            for platform, config in platforms.items():
                try:
                    headers = await self._get_platform_headers(platform)
                    async with session.get(config['url'], headers=headers) as response:
                        if response.status == 200:
                            content = await response.text()
                            profiles[platform] = await self._extract_profile_info(
                                platform, content, config['selectors']
                            )
                except Exception as e:
                    self.logger.error(f"Error finding profiles for {platform}: {str(e)}")
                    profiles[platform] = {'error': str(e)}

        return profiles

    async def _analyze_mentions(self, target: ScanTarget) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze mentions of the target across social media platforms."""
        mentions = {}
        search_terms = [target.domain] + [domain.split('.')[-2] for domain in target.subdomains or []]
        
        async with aiohttp.ClientSession() as session:
            for platform in ['twitter', 'reddit', 'hackernews']:
                try:
                    mentions[platform] = await self._search_platform_mentions(
                        session, platform, search_terms
                    )
                except Exception as e:
                    self.logger.error(f"Error analyzing mentions for {platform}: {str(e)}")
                    mentions[platform] = {'error': str(e)}

        return mentions

    async def _gather_metadata(self, target: ScanTarget) -> Dict[str, Any]:
        """Gather metadata about social media presence."""
        metadata = {
            'statistics': {},
            'engagement_metrics': {},
            'posting_frequency': {},
            'common_hashtags': set(),
            'linked_profiles': set()
        }

        try:
            async with aiohttp.ClientSession() as session:
                for platform in ['twitter', 'linkedin', 'github']:
                    platform_meta = await self._get_platform_metadata(
                        session, platform, target
                    )
                    metadata['statistics'][platform] = platform_meta.get('statistics', {})
                    metadata['engagement_metrics'][platform] = platform_meta.get('engagement', {})
                    metadata['posting_frequency'][platform] = platform_meta.get('frequency', {})
                    
                    if 'hashtags' in platform_meta:
                        metadata['common_hashtags'].update(platform_meta['hashtags'])
                    if 'linked_profiles' in platform_meta:
                        metadata['linked_profiles'].update(platform_meta['linked_profiles'])

        except Exception as e:
            self.logger.error(f"Error gathering metadata: {str(e)}")
            metadata['error'] = str(e)

        return metadata

    async def _find_employees(self, target: ScanTarget) -> List[Dict[str, Any]]:
        """Find potential employees through social media profiles."""
        employees = []
        
        try:
            async with aiohttp.ClientSession() as session:
                # Search LinkedIn for employees
                linkedin_employees = await self._search_linkedin_employees(session, target)
                employees.extend(linkedin_employees)

                # Search GitHub for contributors
                github_employees = await self._search_github_contributors(session, target)
                employees.extend(github_employees)

                # Deduplicate and enrich employee data
                employees = await self._enrich_employee_data(employees)

        except Exception as e:
            self.logger.error(f"Error finding employees: {str(e)}")
            return [{'error': str(e)}]

        return employees

    async def _get_platform_headers(self, platform: str) -> Dict[str, str]:
        """Get appropriate headers for different platforms."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Add platform-specific headers
        if platform == 'twitter':
            headers['Authorization'] = f"Bearer {self.config.get_api_key('twitter')}"
        elif platform == 'linkedin':
            headers['X-Restli-Protocol-Version'] = '2.0.0'
        
        return headers

    async def _search_platform_mentions(
        self, 
        session: aiohttp.ClientSession,
        platform: str,
        search_terms: List[str]
    ) -> List[Dict[str, Any]]:
        """Search for mentions on a specific platform."""
        mentions = []
        # Implementation would vary by platform
        # This is a placeholder for platform-specific implementation
        return mentions

    async def _get_platform_metadata(
        self,
        session: aiohttp.ClientSession,
        platform: str,
        target: ScanTarget
    ) -> Dict[str, Any]:
        """Get metadata for a specific platform."""
        metadata = {}
        # Implementation would vary by platform
        # This is a placeholder for platform-specific implementation
        return metadata

    async def _extract_profile_info(
        self,
        platform: str,
        content: str,
        selectors: Dict[str, str]
    ) -> Dict[str, Any]:
        """Extract profile information from platform-specific content."""
        info = {}
        soup = BeautifulSoup(content, 'html.parser')
        
        try:
            profile_elements = soup.select(selectors['profile'])
            for element in profile_elements:
                name = element.select_one(selectors['name'])
                if name:
                    profile_data = {
                        'name': name.text.strip(),
                        'url': self._extract_profile_url(element, platform),
                        'metadata': self._extract_additional_metadata(element, platform)
                    }
                    info[profile_data['name']] = profile_data
        except Exception as e:
            self.logger.error(f"Error extracting profile info from {platform}: {str(e)}")
            info['error'] = str(e)

        return info

    def _extract_profile_url(self, element: BeautifulSoup, platform: str) -> Optional[str]:
        """Extract profile URL from an element based on the platform."""
        try:
            if platform == 'twitter':
                link = element.find('a', href=re.compile(r'/\w+$'))
                return f"https://twitter.com{link['href']}" if link else None
            elif platform == 'linkedin':
                link = element.find('a', href=re.compile(r'/company/'))
                return link['href'] if link else None
            elif platform == 'github':
                link = element.find('a', href=re.compile(r'/\w+$'))
                return f"https://github.com{link['href']}" if link else None
        except Exception:
            return None

    def _extract_additional_metadata(
        self,
        element: BeautifulSoup,
        platform: str
    ) -> Dict[str, Any]:
        """Extract additional metadata based on the platform."""
        metadata = {}
        try:
            if platform == 'twitter':
                metadata['followers'] = self._extract_twitter_followers(element)
                metadata['verified'] = bool(element.select_one('svg[aria-label="Verified Account"]'))
            elif platform == 'linkedin':
                metadata['employees'] = self._extract_linkedin_employees(element)
                metadata['industry'] = self._extract_linkedin_industry(element)
            elif platform == 'github':
                metadata['repositories'] = self._extract_github_repos(element)
                metadata['contributions'] = self._extract_github_contributions(element)
        except Exception as e:
            self.logger.error(f"Error extracting metadata for {platform}: {str(e)}")
            metadata['error'] = str(e)

        return metadata
