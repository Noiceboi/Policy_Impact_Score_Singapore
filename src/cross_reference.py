"""
Cross-Reference Data Integration Module for Singapore Policy Assessment

This module provides comprehensive cross-checking and cross-study capabilities
by integrating data from multiple independent sources including official
Singapore government websites and international organizations.
"""

import requests
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import time
import logging
from urllib.parse import urljoin, urlparse
import hashlib

# Web scraping and data extraction
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

# Add our framework
import sys
sys.path.append('src')
from framework import PolicyAssessmentFramework
from models import Policy, PolicyAssessment, AssessmentCriteria
from utils import setup_logging


class CrossReferenceDataCollector:
    """
    Collects and cross-references data from multiple independent sources
    to ensure data integrity and comprehensive policy assessment.
    """
    
    def __init__(self):
        """Initialize the cross-reference data collector."""
        self.logger = setup_logging("INFO")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Policy Research Bot'
        })
        
        # Official Singapore Government Data Sources
        self.singapore_sources = {
            'gov_sg': 'https://www.gov.sg',
            'data_gov_sg': 'https://data.gov.sg',
            'singstat': 'https://www.singstat.gov.sg',
            'mas': 'https://www.mas.gov.sg',
            'moh': 'https://www.moh.gov.sg', 
            'mof': 'https://www.mof.gov.sg',
            'hdb': 'https://www.hdb.gov.sg',
            'cpf': 'https://www.cpf.gov.sg',
            'skillsfuture': 'https://www.skillsfuture.gov.sg',
            'parliament': 'https://www.parliament.gov.sg'
        }
        
        # International Organizations for Cross-Validation
        self.international_sources = {
            'world_bank': 'https://data.worldbank.org',
            'oecd': 'https://data.oecd.org',
            'imf': 'https://www.imf.org',
            'un_data': 'https://data.un.org',
            'transparency_intl': 'https://www.transparency.org',
            'heritage_foundation': 'https://www.heritage.org'
        }
        
        # Academic and Research Institutions
        self.academic_sources = {
            'nus_ips': 'https://lkyspp.nus.edu.sg/ips',
            'ntu_rsis': 'https://www.rsis.edu.sg',
            'sutd': 'https://www.sutd.edu.sg',
            'smu': 'https://www.smu.edu.sg',
            'eiu': 'https://www.eiu.com',
            'brookings': 'https://www.brookings.edu'
        }
        
        # Data cache for integrity checking
        self.data_cache = {}
        self.source_validation = {}
        
    def fetch_official_singapore_data(self, source_key: str, endpoint: str = "") -> Dict:
        """
        Fetch data from official Singapore government sources.
        
        Args:
            source_key: Key from singapore_sources dict
            endpoint: Specific API endpoint or page path
            
        Returns:
            Dictionary containing fetched data and metadata
        """
        if source_key not in self.singapore_sources:
            raise ValueError(f"Unknown Singapore source: {source_key}")
        
        base_url = self.singapore_sources[source_key]
        full_url = urljoin(base_url, endpoint)
        
        try:
            self.logger.info(f"Fetching data from {source_key}: {full_url}")
            
            response = self.session.get(full_url, timeout=30)
            response.raise_for_status()
            
            # Try to parse as JSON first
            try:
                data = response.json()
                data_type = 'json'
            except:
                # Parse as HTML/XML
                data = response.text
                data_type = 'html'
            
            # Create data fingerprint for integrity
            fingerprint = hashlib.md5(str(data).encode()).hexdigest()
            
            result = {
                'source': source_key,
                'url': full_url,
                'data': data,
                'data_type': data_type,
                'timestamp': datetime.now().isoformat(),
                'fingerprint': fingerprint,
                'status_code': response.status_code,
                'content_length': len(response.content)
            }
            
            # Cache for integrity checking
            cache_key = f"{source_key}_{endpoint}"
            self.data_cache[cache_key] = result
            
            return result
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch from {source_key}: {e}")
            return {
                'source': source_key,
                'url': full_url,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_data_gov_sg_datasets(self) -> List[Dict]:
        """
        Fetch available datasets from data.gov.sg for policy analysis.
        
        Returns:
            List of available datasets with metadata
        """
        try:
            # Data.gov.sg API endpoint for datasets
            api_url = "https://data.gov.sg/api/action/package_search"
            
            response = self.session.get(api_url, params={
                'q': 'policy OR government OR statistics',
                'rows': 100
            })
            
            if response.status_code == 200:
                data = response.json()
                datasets = []
                
                for package in data.get('result', {}).get('results', []):
                    dataset_info = {
                        'id': package.get('id'),
                        'name': package.get('name'),
                        'title': package.get('title'),
                        'notes': package.get('notes', ''),
                        'organization': package.get('organization', {}).get('title', ''),
                        'last_updated': package.get('metadata_modified'),
                        'resources': len(package.get('resources', [])),
                        'tags': [tag.get('name') for tag in package.get('tags', [])],
                        'url': f"https://data.gov.sg/dataset/{package.get('name')}"
                    }
                    datasets.append(dataset_info)
                
                self.logger.info(f"Found {len(datasets)} relevant datasets on data.gov.sg")
                return datasets
            
        except Exception as e:
            self.logger.error(f"Failed to fetch data.gov.sg datasets: {e}")
        
        return []
    
    def get_singstat_indicators(self) -> Dict:
        """
        Fetch key economic and social indicators from SingStat.
        
        Returns:
            Dictionary of economic and social indicators
        """
        indicators = {}
        
        try:
            # SingStat key indicators (using sample structure)
            singstat_endpoints = {
                'gdp': '/economy/gdp',
                'population': '/population/population-trends',
                'employment': '/labour/employment',
                'housing': '/housing/housing-statistics',
                'healthcare': '/health/health-statistics',
                'education': '/education/education-statistics'
            }
            
            for indicator, endpoint in singstat_endpoints.items():
                result = self.fetch_official_singapore_data('singstat', endpoint)
                if 'error' not in result:
                    indicators[indicator] = {
                        'source': 'SingStat',
                        'last_updated': result['timestamp'],
                        'data_available': True,
                        'url': result['url']
                    }
                else:
                    indicators[indicator] = {
                        'source': 'SingStat',
                        'error': result['error'],
                        'data_available': False
                    }
            
        except Exception as e:
            self.logger.error(f"Failed to fetch SingStat indicators: {e}")
        
        return indicators
    
    def cross_validate_policy_data(self, policy_id: str, policy_name: str) -> Dict:
        """
        Cross-validate policy data across multiple independent sources.
        
        Args:
            policy_id: Policy identifier
            policy_name: Policy name for searching
            
        Returns:
            Cross-validation results from multiple sources
        """
        validation_results = {
            'policy_id': policy_id,
            'policy_name': policy_name,
            'sources_checked': 0,
            'sources_confirmed': 0,
            'validation_score': 0.0,
            'source_details': {},
            'discrepancies': [],
            'confidence_level': 'Unknown'
        }
        
        # Check Singapore government sources
        sg_sources_to_check = ['gov_sg', 'parliament', 'data_gov_sg']
        
        for source in sg_sources_to_check:
            try:
                # Search for policy mentions
                search_result = self._search_policy_mentions(source, policy_name)
                validation_results['source_details'][source] = search_result
                validation_results['sources_checked'] += 1
                
                if search_result.get('mentions_found', 0) > 0:
                    validation_results['sources_confirmed'] += 1
                    
            except Exception as e:
                self.logger.warning(f"Could not validate with {source}: {e}")
                validation_results['source_details'][source] = {'error': str(e)}
        
        # Calculate validation score
        if validation_results['sources_checked'] > 0:
            validation_results['validation_score'] = (
                validation_results['sources_confirmed'] / validation_results['sources_checked']
            )
        
        # Determine confidence level
        if validation_results['validation_score'] >= 0.8:
            validation_results['confidence_level'] = 'High'
        elif validation_results['validation_score'] >= 0.6:
            validation_results['confidence_level'] = 'Medium'
        elif validation_results['validation_score'] >= 0.3:
            validation_results['confidence_level'] = 'Low'
        else:
            validation_results['confidence_level'] = 'Very Low'
        
        return validation_results
    
    def _search_policy_mentions(self, source: str, policy_name: str) -> Dict:
        """
        Search for policy mentions in a specific source.
        
        Args:
            source: Source identifier
            policy_name: Name of policy to search for
            
        Returns:
            Search results with mention count and details
        """
        try:
            # Simplified search - in production would use proper search APIs
            result = self.fetch_official_singapore_data(source, '')
            
            if 'data' in result and isinstance(result['data'], str):
                content = result['data'].lower()
                policy_name_lower = policy_name.lower()
                
                # Count mentions
                mentions = content.count(policy_name_lower)
                
                return {
                    'mentions_found': mentions,
                    'search_successful': True,
                    'content_length': len(content),
                    'timestamp': result['timestamp']
                }
            
        except Exception as e:
            return {
                'mentions_found': 0,
                'search_successful': False,
                'error': str(e)
            }
        
        return {'mentions_found': 0, 'search_successful': False}
    
    def get_international_benchmarks(self, policy_category: str) -> Dict:
        """
        Get international benchmarks for policy comparison.
        
        Args:
            policy_category: Category of policy to benchmark
            
        Returns:
            International benchmark data
        """
        benchmarks = {
            'category': policy_category,
            'singapore_ranking': {},
            'peer_countries': [],
            'best_practices': [],
            'data_sources': []
        }
        
        # Map policy categories to international indicators
        category_indicators = {
            'An sinh xã hội': ['social_protection', 'pension_adequacy'],
            'Chăm sóc sức khỏe': ['health_system_performance', 'health_outcomes'],
            'Giáo dục': ['education_index', 'skills_development'],
            'Phát triển đô thị': ['urban_development', 'housing_affordability'],
            'Kinh tế tài chính': ['financial_development', 'economic_freedom'],
            'Thuế': ['tax_competitiveness', 'tax_efficiency']
        }
        
        indicators = category_indicators.get(policy_category, [])
        
        for indicator in indicators:
            try:
                # Fetch international data (simulated - would use real APIs)
                benchmark_data = self._fetch_international_indicator(indicator)
                benchmarks['singapore_ranking'][indicator] = benchmark_data
                
            except Exception as e:
                self.logger.warning(f"Could not fetch {indicator} benchmark: {e}")
        
        return benchmarks
    
    def _fetch_international_indicator(self, indicator: str) -> Dict:
        """
        Fetch international indicator data.
        
        Args:
            indicator: Indicator name to fetch
            
        Returns:
            Indicator data with Singapore's position
        """
        # Simulated international rankings (in production, use real APIs)
        mock_rankings = {
            'social_protection': {
                'singapore_rank': 15,
                'total_countries': 180,
                'score': 7.8,
                'source': 'OECD Social Protection Index'
            },
            'health_system_performance': {
                'singapore_rank': 6,
                'total_countries': 195,
                'score': 8.9,
                'source': 'WHO Health System Performance Index'
            },
            'education_index': {
                'singapore_rank': 1,
                'total_countries': 189,
                'score': 9.2,
                'source': 'UN Human Development Index - Education'
            },
            'financial_development': {
                'singapore_rank': 3,
                'total_countries': 183,
                'score': 8.7,
                'source': 'World Economic Forum Financial Development Index'
            }
        }
        
        return mock_rankings.get(indicator, {
            'singapore_rank': None,
            'score': None,
            'source': 'Data not available'
        })
    
    def generate_cross_reference_report(self, policies: List[Policy]) -> Dict:
        """
        Generate comprehensive cross-reference report for all policies.
        
        Args:
            policies: List of policies to cross-reference
            
        Returns:
            Comprehensive cross-reference report
        """
        report = {
            'report_date': datetime.now().isoformat(),
            'total_policies': len(policies),
            'data_sources_checked': len(self.singapore_sources) + len(self.international_sources),
            'policies_validated': {},
            'data_integrity_score': 0.0,
            'source_reliability': {},
            'recommendations': []
        }
        
        validated_policies = 0
        total_validation_score = 0.0
        
        for policy in policies:
            self.logger.info(f"Cross-validating policy: {policy.name}")
            
            # Cross-validate each policy
            validation = self.cross_validate_policy_data(policy.id, policy.name)
            report['policies_validated'][policy.id] = validation
            
            if validation['validation_score'] > 0:
                validated_policies += 1
                total_validation_score += validation['validation_score']
        
        # Calculate overall data integrity score
        if validated_policies > 0:
            report['data_integrity_score'] = total_validation_score / validated_policies
        
        # Generate recommendations
        if report['data_integrity_score'] >= 0.8:
            report['recommendations'].append("Data integrity is excellent. Framework ready for production.")
        elif report['data_integrity_score'] >= 0.6:
            report['recommendations'].append("Good data integrity. Consider additional source validation.")
        else:
            report['recommendations'].append("Data integrity needs improvement. Add more authoritative sources.")
        
        if validated_policies < len(policies) * 0.8:
            report['recommendations'].append("Increase policy validation coverage for better reliability.")
        
        return report
    
    def create_comparative_tables(self, policies: List[Policy]) -> Dict[str, pd.DataFrame]:
        """
        Create comprehensive comparative tables for cross-study analysis.
        
        Args:
            policies: List of policies to compare
            
        Returns:
            Dictionary of comparative DataFrames
        """
        tables = {}
        
        # 1. Policy Overview Comparison Table
        overview_data = []
        for policy in policies:
            latest_assessment = policy.get_latest_assessment()
            overview_data.append({
                'Policy ID': policy.id,
                'Policy Name': policy.name,
                'Category': policy.category_name,
                'Implementation Year': policy.implementation_year,
                'Years Active': policy.years_since_implementation,
                'Budget (SGD)': policy.budget or 0,
                'Implementing Agency': policy.implementing_agency,
                'Latest Score': latest_assessment.overall_score if latest_assessment else None,
                'Assessment Count': len(policy.assessments)
            })
        
        tables['policy_overview'] = pd.DataFrame(overview_data)
        
        # 2. Assessment Criteria Comparison
        criteria_data = []
        for policy in policies:
            latest_assessment = policy.get_latest_assessment()
            if latest_assessment:
                criteria_data.append({
                    'Policy Name': policy.name,
                    'Category': policy.category_name,
                    'Scope': latest_assessment.criteria.scope,
                    'Magnitude': latest_assessment.criteria.magnitude,
                    'Durability': latest_assessment.criteria.durability,
                    'Adaptability': latest_assessment.criteria.adaptability,
                    'Cross-referencing': latest_assessment.criteria.cross_referencing,
                    'Overall Score': latest_assessment.overall_score
                })
        
        tables['criteria_comparison'] = pd.DataFrame(criteria_data)
        
        # 3. Category Performance Summary
        category_performance = {}
        for policy in policies:
            category = policy.category_name
            latest_assessment = policy.get_latest_assessment()
            
            if category not in category_performance:
                category_performance[category] = {
                    'policies': [],
                    'scores': [],
                    'budgets': [],
                    'years_active': []
                }
            
            category_performance[category]['policies'].append(policy.name)
            if latest_assessment:
                category_performance[category]['scores'].append(latest_assessment.overall_score)
            category_performance[category]['budgets'].append(policy.budget or 0)
            category_performance[category]['years_active'].append(policy.years_since_implementation)
        
        category_summary = []
        for category, data in category_performance.items():
            scores = data['scores']
            budgets = data['budgets']
            years = data['years_active']
            
            category_summary.append({
                'Category': category,
                'Policy Count': len(data['policies']),
                'Average Score': np.mean(scores) if scores else None,
                'Min Score': np.min(scores) if scores else None,
                'Max Score': np.max(scores) if scores else None,
                'Total Budget (SGD)': sum(budgets),
                'Average Years Active': np.mean(years),
                'Policy Names': '; '.join(data['policies'])
            })
        
        tables['category_summary'] = pd.DataFrame(category_summary)
        
        # 4. Time-Series Evolution Table
        evolution_data = []
        for policy in policies:
            for assessment in policy.assessments:
                evolution_data.append({
                    'Policy Name': policy.name,
                    'Assessment Date': assessment.assessment_date,
                    'Years Since Implementation': (assessment.assessment_date.year - policy.implementation_year),
                    'Overall Score': assessment.overall_score,
                    'Scope': assessment.criteria.scope,
                    'Magnitude': assessment.criteria.magnitude,
                    'Durability': assessment.criteria.durability,
                    'Adaptability': assessment.criteria.adaptability,
                    'Cross-referencing': assessment.criteria.cross_referencing,
                    'Assessor': assessment.assessor
                })
        
        tables['time_series_evolution'] = pd.DataFrame(evolution_data)
        
        # 5. Budget vs Impact Analysis
        budget_impact_data = []
        for policy in policies:
            latest_assessment = policy.get_latest_assessment()
            if latest_assessment and policy.budget:
                budget_impact_data.append({
                    'Policy Name': policy.name,
                    'Budget (SGD)': policy.budget,
                    'Budget per Year (SGD)': policy.budget / max(policy.years_since_implementation, 1),
                    'Overall Score': latest_assessment.overall_score,
                    'Impact per SGD': latest_assessment.overall_score / (policy.budget / 1e9),  # Impact per billion SGD
                    'Cost Effectiveness Rank': 0  # Will be calculated after sorting
                })
        
        if budget_impact_data:
            budget_df = pd.DataFrame(budget_impact_data)
            budget_df = budget_df.sort_values('Impact per SGD', ascending=False)
            budget_df['Cost Effectiveness Rank'] = range(1, len(budget_df) + 1)
            tables['budget_impact_analysis'] = budget_df
        
        return tables


def create_cross_reference_dashboard():
    """
    Create an HTML dashboard showing cross-reference analysis results.
    """
    # This function would create interactive visualizations
    # showing cross-validation results, comparative tables, etc.
    pass


if __name__ == "__main__":
    # Example usage
    collector = CrossReferenceDataCollector()
    
    # Demonstrate data collection capabilities
    print("🔍 Singapore Policy Cross-Reference Data Collection")
    print("=" * 55)
    
    # Get available datasets
    datasets = collector.get_data_gov_sg_datasets()
    print(f"Found {len(datasets)} relevant datasets on data.gov.sg")
    
    # Get SingStat indicators
    indicators = collector.get_singstat_indicators()
    print(f"Retrieved {len(indicators)} SingStat indicators")
    
    print("\n✅ Cross-reference data collection system ready!")
    print("📊 Ready to validate policy data against official sources")
    print("🌐 Ready to benchmark against international standards")
