"""
Main Policy Assessment Framework.

This module provides the core functionality for assessing policy impacts,
managing policy collections, and coordinating analysis workflows.
"""

import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Union, Tuple
from pathlib import Path

from models import (
    Policy, PolicyAssessment, AssessmentCriteria, WeightingConfig,
    PolicyCategory, PolicyCollection
)
from analysis import PolicyAnalyzer
from visualization import PolicyVisualizer


class PolicyAssessmentFramework:
    """
    Main framework class for policy impact assessment.
    
    This class coordinates policy data management, assessment workflows,
    analysis, and reporting capabilities.
    """
    
    def __init__(self, weighting_config: Optional[WeightingConfig] = None):
        """
        Initialize the framework.
        
        Args:
            weighting_config: Custom weighting configuration for assessments
        """
        self.policies = PolicyCollection()
        self.weighting_config = weighting_config or WeightingConfig()
        self.analyzer = PolicyAnalyzer()
        self.visualizer = PolicyVisualizer()
        
    def add_policy(self, policy: Policy) -> None:
        """Add a policy to the framework."""
        self.policies.add_policy(policy)
        
    def assess_policy(
        self, 
        policy: Union[Policy, str], 
        criteria_scores: Dict[str, int],
        assessor: Optional[str] = None,
        notes: Optional[str] = None,
        data_sources: Optional[List[str]] = None
    ) -> float:
        """
        Assess a policy with given criteria scores.
        
        Args:
            policy: Policy object or policy ID
            criteria_scores: Dictionary with criterion names and scores
            assessor: Name of the person conducting assessment
            notes: Additional notes about the assessment
            data_sources: List of data sources used
            
        Returns:
            float: Overall weighted impact score
        """
        if isinstance(policy, str):
            policy_obj = self.policies.get_policy_by_id(policy)
            if not policy_obj:
                raise ValueError(f"Policy with ID '{policy}' not found")
        else:
            policy_obj = policy
            
        # Create assessment criteria
        criteria = AssessmentCriteria(
            scope=criteria_scores.get('scope', 0),
            magnitude=criteria_scores.get('magnitude', 0),
            durability=criteria_scores.get('durability', 0),
            adaptability=criteria_scores.get('adaptability', 0),
            cross_referencing=criteria_scores.get('cross_referencing', 0)
        )
        
        # Create assessment
        assessment = PolicyAssessment(
            policy_id=policy_obj.id,
            assessment_date=datetime.now(),
            criteria=criteria,
            weighted_config=self.weighting_config,
            assessor=assessor,
            notes=notes,
            data_sources=data_sources or []
        )
        
        # Add assessment to policy
        policy_obj.add_assessment(assessment)
        
        return assessment.overall_score
    
    def load_policies_from_csv(self, file_path: str) -> None:
        """
        Load policies from a CSV file.
        
        Args:
            file_path: Path to CSV file with policy data
        """
        df = pd.read_csv(file_path)
        
        for _, row in df.iterrows():
            policy = Policy(
                id=str(row['id']),
                name=row['name'],
                category=row['category'],
                implementation_year=int(row['implementation_year']),
                description=row.get('description'),
                implementing_agency=row.get('implementing_agency'),
                budget=row.get('budget') if pd.notna(row.get('budget')) else None
            )
            
            # Add objectives if present
            if 'objectives' in row and pd.notna(row['objectives']):
                policy.objectives = [obj.strip() for obj in str(row['objectives']).split(';')]
            
            self.add_policy(policy)
    
    def save_policies_to_csv(self, file_path: str) -> None:
        """
        Save policies to a CSV file.
        
        Args:
            file_path: Output file path
        """
        data = []
        for policy in self.policies.policies:
            latest_assessment = policy.get_latest_assessment()
            
            row = {
                'id': policy.id,
                'name': policy.name,
                'category': policy.category_name,
                'implementation_year': policy.implementation_year,
                'description': policy.description,
                'implementing_agency': policy.implementing_agency,
                'budget': policy.budget,
                'objectives': '; '.join(policy.objectives) if policy.objectives else None,
                'latest_score': latest_assessment.overall_score if latest_assessment else None,
                'assessment_count': len(policy.assessments)
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)
    
    def load_assessments_from_csv(self, file_path: str) -> None:
        """
        Load historical assessments from a CSV file.
        
        Args:
            file_path: Path to CSV file with assessment data
        """
        df = pd.read_csv(file_path)
        
        for _, row in df.iterrows():
            policy = self.policies.get_policy_by_id(str(row['policy_id']))
            if not policy:
                continue
                
            criteria = AssessmentCriteria(
                scope=int(row['scope']),
                magnitude=int(row['magnitude']),
                durability=int(row['durability']),
                adaptability=int(row['adaptability']),
                cross_referencing=int(row['cross_referencing'])
            )
            
            assessment = PolicyAssessment(
                policy_id=policy.id,
                assessment_date=pd.to_datetime(row['assessment_date']),
                criteria=criteria,
                weighted_config=self.weighting_config,
                assessor=row.get('assessor'),
                notes=row.get('notes')
            )
            
            policy.add_assessment(assessment)
    
    def get_policy_rankings(self, category: Optional[str] = None) -> List[Tuple[Policy, float]]:
        """
        Get policies ranked by their latest impact scores.
        
        Args:
            category: Filter by specific category (optional)
            
        Returns:
            List of (Policy, score) tuples sorted by score descending
        """
        policies_to_rank = self.policies.policies
        
        if category:
            policies_to_rank = self.policies.get_policies_by_category(category)
        
        policy_scores = []
        for policy in policies_to_rank:
            latest_assessment = policy.get_latest_assessment()
            if latest_assessment:
                policy_scores.append((policy, latest_assessment.overall_score))
        
        # Sort by score descending
        policy_scores.sort(key=lambda x: x[1], reverse=True)
        return policy_scores
    
    def analyze_policy_evolution(self, policy_id: str) -> Dict:
        """
        Analyze how a policy's impact has evolved over time.
        
        Args:
            policy_id: ID of the policy to analyze
            
        Returns:
            Dictionary with evolution analysis results
        """
        policy = self.policies.get_policy_by_id(policy_id)
        if not policy:
            raise ValueError(f"Policy with ID '{policy_id}' not found")
        
        return self.analyzer.analyze_policy_evolution(policy)
    
    def compare_policies(self, policy_ids: List[str]) -> Dict:
        """
        Compare multiple policies across assessment criteria.
        
        Args:
            policy_ids: List of policy IDs to compare
            
        Returns:
            Dictionary with comparison results
        """
        policies = []
        for policy_id in policy_ids:
            policy = self.policies.get_policy_by_id(policy_id)
            if policy:
                policies.append(policy)
        
        if not policies:
            raise ValueError("No valid policies found for comparison")
        
        return self.analyzer.compare_policies(policies)
    
    def analyze_category_trends(self, category: str) -> Dict:
        """
        Analyze trends within a specific policy category.
        
        Args:
            category: Policy category to analyze
            
        Returns:
            Dictionary with trend analysis results
        """
        category_policies = self.policies.get_policies_by_category(category)
        return self.analyzer.analyze_category_trends(category_policies)
    
    def generate_summary_report(self) -> Dict:
        """
        Generate a comprehensive summary report of all policies.
        
        Returns:
            Dictionary with summary statistics and insights
        """
        total_policies = self.policies.total_policies
        categories_summary = self.policies.categories_summary
        
        # Calculate average scores by category
        category_scores = {}
        for category, count in categories_summary.items():
            category_policies = self.policies.get_policies_by_category(category)
            scores = []
            for policy in category_policies:
                latest_assessment = policy.get_latest_assessment()
                if latest_assessment:
                    scores.append(latest_assessment.overall_score)
            
            if scores:
                category_scores[category] = {
                    'average_score': sum(scores) / len(scores),
                    'policy_count': count,
                    'assessed_policies': len(scores)
                }
        
        # Find top performing policies
        top_policies = self.get_policy_rankings()[:5]
        
        return {
            'total_policies': total_policies,
            'categories_summary': categories_summary,
            'category_scores': category_scores,
            'top_policies': [(p.name, score) for p, score in top_policies],
            'assessment_coverage': sum(1 for p in self.policies.policies 
                                     if p.get_latest_assessment()) / total_policies * 100
        }
    
    def export_data(self, output_dir: str) -> None:
        """
        Export all framework data to files.
        
        Args:
            output_dir: Directory to save export files
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Export policies
        self.save_policies_to_csv(str(output_path / "policies.csv"))
        
        # Export assessments
        assessments_data = []
        for policy in self.policies.policies:
            for assessment in policy.assessments:
                assessments_data.append({
                    'policy_id': assessment.policy_id,
                    'assessment_date': assessment.assessment_date.isoformat(),
                    'scope': assessment.criteria.scope,
                    'magnitude': assessment.criteria.magnitude,
                    'durability': assessment.criteria.durability,
                    'adaptability': assessment.criteria.adaptability,
                    'cross_referencing': assessment.criteria.cross_referencing,
                    'overall_score': assessment.overall_score,
                    'assessor': assessment.assessor,
                    'notes': assessment.notes
                })
        
        df_assessments = pd.DataFrame(assessments_data)
        df_assessments.to_csv(str(output_path / "assessments.csv"), index=False)
        
        # Export summary report
        summary = self.generate_summary_report()
        with open(output_path / "summary_report.json", 'w') as f:
            json.dump(summary, f, indent=2, default=str)
    
    def create_visualization(self, chart_type: str, **kwargs):
        """
        Create visualizations using the visualization module.
        
        Args:
            chart_type: Type of chart to create
            **kwargs: Additional arguments for visualization
        """
        return self.visualizer.create_chart(self.policies, chart_type, **kwargs)
    
    def analyze_temporal_concatenation(self, policies: Optional[List[str]] = None) -> Dict:
        """
        Phân tích hiệu ứng concatenation và temporal patterns của các chính sách.
        
        Args:
            policies: List of policy IDs to analyze (optional, analyzes all if None)
            
        Returns:
            Dictionary with comprehensive temporal concatenation analysis
        """
        if policies:
            policy_objects = []
            for policy_id in policies:
                policy = self.policies.get_policy_by_id(policy_id)
                if policy:
                    policy_objects.append(policy)
        else:
            policy_objects = self.policies.policies
        
        if not policy_objects:
            raise ValueError("No valid policies found for temporal concatenation analysis")
        
        return self.analyzer.analyze_policy_concatenation_effects(policy_objects)
    
    def analyze_contextual_timing(self, category: Optional[str] = None) -> Dict:
        """
        Phân tích tác động của timing và bối cảnh lên hiệu quả chính sách.
        
        Args:
            category: Analyze only policies in specific category (optional)
            
        Returns:
            Dictionary with contextual timing analysis
        """
        if category:
            policy_objects = self.policies.get_policies_by_category(category)
        else:
            policy_objects = self.policies.policies
        
        if not policy_objects:
            raise ValueError("No valid policies found for contextual timing analysis")
        
        return self.analyzer.analyze_contextual_timing_impact(policy_objects)
    
    def predict_policy_trajectory(
        self, 
        policy_id: str, 
        scenario: str = 'current_trend'
    ) -> Dict:
        """
        Dự đoán quỹ đạo phát triển của chính sách theo các kịch bản khác nhau.
        
        Args:
            policy_id: ID of policy to predict
            scenario: Prediction scenario ('current_trend', 'optimistic', 'pessimistic', 'disruptive')
            
        Returns:
            Dictionary with evolution trajectory predictions
        """
        policy = self.policies.get_policy_by_id(policy_id)
        if not policy:
            raise ValueError(f"Policy with ID '{policy_id}' not found")
        
        return self.analyzer.predict_policy_evolution_trajectory(policy, scenario)
    
    def identify_slow_burn_policies(self, min_improvement: float = 1.0) -> List[Dict]:
        """
        Nhận diện các chính sách 'slow burn' - bắt đầu thấp nhưng phát triển mạnh theo thời gian.
        
        Args:
            min_improvement: Minimum improvement score required
            
        Returns:
            List of slow burn policies with analysis
        """
        from .utils import analyze_temporal_impact_patterns
        
        temporal_patterns = analyze_temporal_impact_patterns(self.policies.policies)
        slow_burn_policies = temporal_patterns.get('slow_burn_policies', [])
        
        # Filter by minimum improvement
        filtered_policies = [
            policy_data for policy_data in slow_burn_policies
            if (policy_data['latest_score'] - policy_data['initial_score']) >= min_improvement
        ]
        
        # Sort by improvement rate
        filtered_policies.sort(key=lambda x: x['improvement_rate'], reverse=True)
        
        return filtered_policies
    
    def identify_timely_response_policies(self, min_score: float = 4.0) -> List[Dict]:
        """
        Nhận diện các chính sách phản ứng kịp thời với bối cảnh.
        
        Args:
            min_score: Minimum impact score required
            
        Returns:
            List of timely response policies
        """
        from .utils import detect_contextual_timing_advantage
        
        timing_analysis = detect_contextual_timing_advantage(self.policies.policies)
        
        # Combine well-timed and proactive policies
        timely_policies = []
        
        for policy_data in timing_analysis['well_timed_policies']:
            if policy_data['timing_score'] >= min_score:
                timely_policies.append({
                    **policy_data,
                    'response_type': 'immediate_response'
                })
        
        for policy_data in timing_analysis['proactive_policies']:
            if policy_data['effectiveness'] >= min_score:
                timely_policies.append({
                    **policy_data,
                    'response_type': 'proactive_response'
                })
        
        return timely_policies
    
    def analyze_policy_maturity_distribution(self) -> Dict:
        """
        Phân tích phân bố độ trưởng thành của các chính sách.
        
        Returns:
            Dictionary with maturity distribution analysis
        """
        from .utils import calculate_policy_maturity_index
        
        maturity_data = {}
        maturity_stages = {
            'Highly Mature': [],
            'Mature': [],
            'Developing': [],
            'Early Stage': [],
            'Nascent': []
        }
        
        for policy in self.policies.policies:
            maturity_analysis = calculate_policy_maturity_index(policy)
            maturity_data[policy.id] = {
                'policy_name': policy.name,
                'category': policy.category_name,
                **maturity_analysis
            }
            
            stage = maturity_analysis['stage']
            maturity_stages[stage].append({
                'policy_id': policy.id,
                'policy_name': policy.name,
                'maturity_index': maturity_analysis['maturity_index']
            })
        
        # Calculate stage statistics
        stage_stats = {}
        for stage, policies in maturity_stages.items():
            if policies:
                indices = [p['maturity_index'] for p in policies]
                stage_stats[stage] = {
                    'count': len(policies),
                    'percentage': len(policies) / len(self.policies.policies) * 100,
                    'avg_maturity_index': sum(indices) / len(indices),
                    'policies': policies
                }
        
        return {
            'detailed_analysis': maturity_data,
            'stage_distribution': stage_stats,
            'summary': {
                'total_policies': len(self.policies.policies),
                'most_common_stage': max(stage_stats.keys(), key=lambda k: stage_stats[k]['count']),
                'highly_mature_count': len(maturity_stages['Highly Mature']),
                'needs_development_count': len(maturity_stages['Early Stage']) + len(maturity_stages['Nascent'])
            }
        }
    
    def generate_advanced_insights_report(self) -> Dict:
        """
        Tạo báo cáo insights nâng cao với phân tích temporal và contextual.
        
        Returns:
            Dictionary with comprehensive insights
        """
        report = {
            'executive_summary': {},
            'temporal_analysis': {},
            'contextual_analysis': {},
            'maturity_analysis': {},
            'strategic_recommendations': []
        }
        
        # Basic summary
        basic_summary = self.generate_summary_report()
        report['executive_summary'] = basic_summary
        
        # Temporal concatenation analysis
        try:
            temporal_analysis = self.analyze_temporal_concatenation()
            report['temporal_analysis'] = temporal_analysis
        except Exception as e:
            report['temporal_analysis'] = {'error': str(e)}
        
        # Contextual timing analysis
        try:
            contextual_analysis = self.analyze_contextual_timing()
            report['contextual_analysis'] = contextual_analysis
        except Exception as e:
            report['contextual_analysis'] = {'error': str(e)}
        
        # Maturity analysis
        try:
            maturity_analysis = self.analyze_policy_maturity_distribution()
            report['maturity_analysis'] = maturity_analysis
        except Exception as e:
            report['maturity_analysis'] = {'error': str(e)}
        
        # Generate strategic recommendations
        recommendations = self._generate_strategic_recommendations(
            basic_summary, 
            report['temporal_analysis'], 
            report['contextual_analysis'],
            report['maturity_analysis']
        )
        report['strategic_recommendations'] = recommendations
        
        return report
    
    def _generate_strategic_recommendations(
        self, 
        summary: Dict, 
        temporal: Dict, 
        contextual: Dict,
        maturity: Dict
    ) -> List[Dict]:
        """Generate strategic recommendations based on analysis results."""
        recommendations = []
        
        # Based on temporal patterns
        if 'temporal_patterns' in temporal:
            slow_burn_count = len(temporal['temporal_patterns'].get('slow_burn_policies', []))
            if slow_burn_count > 0:
                recommendations.append({
                    'category': 'Temporal Optimization',
                    'priority': 'High',
                    'recommendation': f'Monitor and support {slow_burn_count} slow-burn policies '
                                    f'that show strong potential for long-term impact.',
                    'rationale': 'These policies may need additional resources or time to reach full potential.'
                })
        
        # Based on contextual timing
        if 'timing_analysis' in contextual:
            well_timed_count = len(contextual['timing_analysis'].get('well_timed_policies', []))
            if well_timed_count > 0:
                recommendations.append({
                    'category': 'Contextual Alignment',
                    'priority': 'Medium',
                    'recommendation': f'Analyze success factors from {well_timed_count} well-timed policies '
                                    f'for future policy design.',
                    'rationale': 'Understanding timing success can improve future policy effectiveness.'
                })
        
        # Based on maturity analysis
        if 'summary' in maturity:
            needs_development = maturity['summary'].get('needs_development_count', 0)
            if needs_development > 0:
                recommendations.append({
                    'category': 'Policy Development',
                    'priority': 'High', 
                    'recommendation': f'Prioritize development support for {needs_development} policies '
                                    f'in early stages or nascent phases.',
                    'rationale': 'Early intervention can significantly improve policy maturation trajectory.'
                })
        
        # Category-specific recommendations
        if 'category_scores' in summary:
            low_performing_categories = [
                cat for cat, data in summary['category_scores'].items()
                if data['average_score'] < 3.0
            ]
            
            if low_performing_categories:
                recommendations.append({
                    'category': 'Category Improvement',
                    'priority': 'High',
                    'recommendation': f'Focus improvement efforts on categories: {", ".join(low_performing_categories)}',
                    'rationale': 'These categories show consistently lower performance and need strategic attention.'
                })
        
        return recommendations
