"""
Policy analysis module for statistical analysis and trend identification.

This module provides advanced analytics capabilities including time-series
analysis, policy evolution tracking, and comparative analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

from models import Policy, PolicyAssessment, PolicyCollection


class PolicyAnalyzer:
    """
    Advanced analytics engine for policy impact analysis.
    
    Provides statistical analysis, trend identification, and predictive
    modeling capabilities for policy assessment data.
    """
    
    def __init__(self):
        """Initialize the policy analyzer."""
        self.scaler = StandardScaler()
    
    def analyze_policy_evolution(self, policy: Policy) -> Dict[str, Any]:
        """
        Analyze how a policy's impact has evolved over time.
        
        Args:
            policy: Policy to analyze
            
        Returns:
            Dictionary containing evolution analysis results
        """
        if len(policy.assessments) < 2:
            return {
                'error': 'Insufficient data for evolution analysis',
                'required_assessments': 2,
                'available_assessments': len(policy.assessments)
            }
        
        # Sort assessments by date
        assessments = sorted(policy.assessments, key=lambda x: x.assessment_date)
        
        # Extract time series data
        dates = [a.assessment_date for a in assessments]
        overall_scores = [a.overall_score for a in assessments]
        scope_scores = [a.criteria.scope for a in assessments]
        magnitude_scores = [a.criteria.magnitude for a in assessments]
        durability_scores = [a.criteria.durability for a in assessments]
        adaptability_scores = [a.criteria.adaptability for a in assessments]
        cross_ref_scores = [a.criteria.cross_referencing for a in assessments]
        
        # Calculate trends
        trends = self._calculate_trends(dates, {
            'overall': overall_scores,
            'scope': scope_scores,
            'magnitude': magnitude_scores,
            'durability': durability_scores,
            'adaptability': adaptability_scores,
            'cross_referencing': cross_ref_scores
        })
        
        # Calculate volatility
        volatility = {
            'overall': np.std(overall_scores),
            'scope': np.std(scope_scores),
            'magnitude': np.std(magnitude_scores),
            'durability': np.std(durability_scores),
            'adaptability': np.std(adaptability_scores),
            'cross_referencing': np.std(cross_ref_scores)
        }
        
        # Performance phases
        phases = self._identify_performance_phases(dates, overall_scores)
        
        return {
            'policy_id': policy.id,
            'policy_name': policy.name,
            'assessment_period': {
                'start': min(dates).isoformat(),
                'end': max(dates).isoformat(),
                'duration_years': (max(dates) - min(dates)).days / 365.25
            },
            'trends': trends,
            'volatility': volatility,
            'performance_phases': phases,
            'summary': {
                'total_assessments': len(assessments),
                'overall_trend': trends['overall']['direction'],
                'strongest_improvement': max(trends.items(), key=lambda x: x[1]['slope'])[0],
                'highest_volatility': max(volatility.items(), key=lambda x: x[1])[0]
            }
        }
    
    def compare_policies(self, policies: List[Policy]) -> Dict[str, Any]:
        """
        Compare multiple policies across assessment criteria.
        
        Args:
            policies: List of policies to compare
            
        Returns:
            Dictionary with comparison results
        """
        if len(policies) < 2:
            return {'error': 'At least 2 policies required for comparison'}
        
        comparison_data = []
        
        for policy in policies:
            latest_assessment = policy.get_latest_assessment()
            if not latest_assessment:
                continue
            
            policy_data = {
                'policy_id': policy.id,
                'policy_name': policy.name,
                'category': policy.category_name,
                'implementation_year': policy.implementation_year,
                'years_active': policy.years_since_implementation,
                'overall_score': latest_assessment.overall_score,
                'scope': latest_assessment.criteria.scope,
                'magnitude': latest_assessment.criteria.magnitude,
                'durability': latest_assessment.criteria.durability,
                'adaptability': latest_assessment.criteria.adaptability,
                'cross_referencing': latest_assessment.criteria.cross_referencing,
                'assessment_count': len(policy.assessments)
            }
            comparison_data.append(policy_data)
        
        if not comparison_data:
            return {'error': 'No policies with assessments found'}
        
        df = pd.DataFrame(comparison_data)
        
        # Statistical analysis
        criteria_cols = ['scope', 'magnitude', 'durability', 'adaptability', 'cross_referencing']
        
        # Correlation analysis
        correlations = df[criteria_cols + ['overall_score']].corr()['overall_score'].to_dict()
        
        # Rankings
        rankings = {
            'overall_score': df.nlargest(len(df), 'overall_score')[['policy_name', 'overall_score']].to_dict('records'),
            'scope': df.nlargest(len(df), 'scope')[['policy_name', 'scope']].to_dict('records'),
            'magnitude': df.nlargest(len(df), 'magnitude')[['policy_name', 'magnitude']].to_dict('records'),
            'durability': df.nlargest(len(df), 'durability')[['policy_name', 'durability']].to_dict('records'),
            'adaptability': df.nlargest(len(df), 'adaptability')[['policy_name', 'adaptability']].to_dict('records'),
            'cross_referencing': df.nlargest(len(df), 'cross_referencing')[['policy_name', 'cross_referencing']].to_dict('records')
        }
        
        # Statistical tests
        statistical_tests = self._perform_statistical_tests(df, criteria_cols)
        
        return {
            'comparison_summary': {
                'policies_compared': len(comparison_data),
                'average_overall_score': df['overall_score'].mean(),
                'score_range': {
                    'min': df['overall_score'].min(),
                    'max': df['overall_score'].max(),
                    'std': df['overall_score'].std()
                }
            },
            'rankings': rankings,
            'correlations': correlations,
            'statistical_tests': statistical_tests,
            'detailed_data': comparison_data
        }
    
    def analyze_category_trends(self, policies: List[Policy]) -> Dict[str, Any]:
        """
        Analyze trends within a specific policy category.
        
        Args:
            policies: List of policies in the same category
            
        Returns:
            Dictionary with trend analysis results
        """
        if not policies:
            return {'error': 'No policies provided for analysis'}
        
        category = policies[0].category_name
        
        # Collect time series data
        time_series_data = []
        for policy in policies:
            for assessment in policy.assessments:
                time_series_data.append({
                    'policy_id': policy.id,
                    'policy_name': policy.name,
                    'assessment_date': assessment.assessment_date,
                    'overall_score': assessment.overall_score,
                    'scope': assessment.criteria.scope,
                    'magnitude': assessment.criteria.magnitude,
                    'durability': assessment.criteria.durability,
                    'adaptability': assessment.criteria.adaptability,
                    'cross_referencing': assessment.criteria.cross_referencing,
                    'implementation_year': policy.implementation_year
                })
        
        if not time_series_data:
            return {'error': 'No assessment data found for category analysis'}
        
        df = pd.DataFrame(time_series_data)
        df['assessment_date'] = pd.to_datetime(df['assessment_date'])
        
        # Annual aggregation
        df['year'] = df['assessment_date'].dt.year
        annual_trends = df.groupby('year').agg({
            'overall_score': ['mean', 'std', 'count'],
            'scope': 'mean',
            'magnitude': 'mean',
            'durability': 'mean',
            'adaptability': 'mean',
            'cross_referencing': 'mean'
        }).round(2)
        
        # Policy lifecycle analysis
        lifecycle_analysis = self._analyze_policy_lifecycle(policies)
        
        # Performance distribution
        performance_distribution = self._analyze_performance_distribution(df)
        
        return {
            'category': category,
            'analysis_period': {
                'start_year': df['year'].min(),
                'end_year': df['year'].max(),
                'total_policies': len(policies),
                'total_assessments': len(time_series_data)
            },
            'annual_trends': annual_trends.to_dict(),
            'lifecycle_analysis': lifecycle_analysis,
            'performance_distribution': performance_distribution,
            'category_insights': self._generate_category_insights(df, policies)
        }
    
    def predict_policy_impact(self, policy: Policy, months_ahead: int = 12) -> Dict[str, Any]:
        """
        Predict future policy impact based on historical trends.
        
        Args:
            policy: Policy to predict
            months_ahead: Number of months to predict ahead
            
        Returns:
            Dictionary with prediction results
        """
        if len(policy.assessments) < 3:
            return {
                'error': 'Insufficient historical data for prediction',
                'required_assessments': 3,
                'available_assessments': len(policy.assessments)
            }
        
        # Prepare time series data
        assessments = sorted(policy.assessments, key=lambda x: x.assessment_date)
        
        # Convert dates to numeric format (days since first assessment)
        base_date = assessments[0].assessment_date
        days = [(a.assessment_date - base_date).days for a in assessments]
        scores = [a.overall_score for a in assessments]
        
        # Fit linear regression model
        X = np.array(days).reshape(-1, 1)
        y = np.array(scores)
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Generate predictions
        future_days = [(base_date + timedelta(days=30*i)).replace(day=1) for i in range(1, months_ahead + 1)]
        future_days_numeric = [(d - base_date).days for d in future_days]
        
        X_future = np.array(future_days_numeric).reshape(-1, 1)
        predictions = model.predict(X_future)
        
        # Calculate confidence intervals (simplified)
        residuals = y - model.predict(X)
        mse = np.mean(residuals**2)
        std_error = np.sqrt(mse)
        
        confidence_intervals = [(pred - 1.96*std_error, pred + 1.96*std_error) for pred in predictions]
        
        return {
            'policy_id': policy.id,
            'policy_name': policy.name,
            'prediction_horizon': months_ahead,
            'model_performance': {
                'r_squared': model.score(X, y),
                'mse': mse,
                'trend_slope': model.coef_[0],
                'trend_direction': 'improving' if model.coef_[0] > 0 else 'declining'
            },
            'predictions': [
                {
                    'date': future_days[i].isoformat(),
                    'predicted_score': float(predictions[i]),
                    'confidence_interval': {
                        'lower': float(confidence_intervals[i][0]),
                        'upper': float(confidence_intervals[i][1])
                    }
                }
                for i in range(len(predictions))
            ]
        }
    
    def analyze_policy_concatenation_effects(self, policies: List[Policy]) -> Dict[str, Any]:
        """
        Phân tích hiệu ứng concatenation - cách các chính sách liên kết và khuếch đại tác động của nhau.
        
        Args:
            policies: List of policies to analyze
            
        Returns:
            Dictionary with concatenation analysis results
        """
        from .utils import (analyze_temporal_impact_patterns, 
                           identify_policy_interconnections,
                           calculate_policy_maturity_index)
        
        # Get temporal patterns
        temporal_patterns = analyze_temporal_impact_patterns(policies)
        
        # Get interconnections
        interconnections = identify_policy_interconnections(policies)
        
        # Analyze synergy effects
        synergy_effects = self._calculate_synergy_effects(policies, interconnections)
        
        # Policy maturity distribution
        maturity_analysis = {}
        for policy in policies:
            maturity_data = calculate_policy_maturity_index(policy)
            maturity_analysis[policy.id] = maturity_data
        
        return {
            'temporal_patterns': temporal_patterns,
            'interconnections': interconnections,
            'synergy_effects': synergy_effects,
            'maturity_distribution': maturity_analysis,
            'concatenation_insights': self._generate_concatenation_insights(
                temporal_patterns, interconnections, synergy_effects
            )
        }
    
    def analyze_contextual_timing_impact(self, policies: List[Policy]) -> Dict[str, Any]:
        """
        Phân tích tác động của timing và bối cảnh lên hiệu quả chính sách.
        
        Args:
            policies: List of policies to analyze
            
        Returns:
            Dictionary with contextual timing analysis
        """
        from .utils import detect_contextual_timing_advantage
        
        timing_analysis = detect_contextual_timing_advantage(policies)
        
        # Analyze timing effectiveness
        timing_effectiveness = {
            'high_impact_timely': [],
            'high_impact_proactive': [],
            'missed_timing_opportunities': []
        }
        
        # Well-timed policies with high impact
        for policy_data in timing_analysis['well_timed_policies']:
            if policy_data['timing_score'] >= 4.0:
                timing_effectiveness['high_impact_timely'].append(policy_data)
        
        # Proactive policies that proved effective
        for policy_data in timing_analysis['proactive_policies']:
            if policy_data['effectiveness'] >= 4.0:
                timing_effectiveness['high_impact_proactive'].append(policy_data)
        
        # Calculate timing success rate by category
        category_timing_success = {}
        for policy in policies:
            category = policy.category_name
            if category not in category_timing_success:
                category_timing_success[category] = {
                    'total_policies': 0,
                    'well_timed_policies': 0,
                    'proactive_policies': 0
                }
            
            category_timing_success[category]['total_policies'] += 1
            
            # Check if policy appears in timing analysis
            policy_in_well_timed = any(p['policy'].id == policy.id 
                                     for p in timing_analysis['well_timed_policies'])
            policy_in_proactive = any(p['policy'].id == policy.id 
                                    for p in timing_analysis['proactive_policies'])
            
            if policy_in_well_timed:
                category_timing_success[category]['well_timed_policies'] += 1
            if policy_in_proactive:
                category_timing_success[category]['proactive_policies'] += 1
        
        return {
            'timing_analysis': timing_analysis,
            'timing_effectiveness': timing_effectiveness,
            'category_timing_success': category_timing_success,
            'contextual_insights': self._generate_contextual_insights(timing_analysis)
        }
    
    def predict_policy_evolution_trajectory(self, policy: Policy, scenario: str = 'current_trend') -> Dict[str, Any]:
        """
        Dự đoán quỹ đạo phát triển của chính sách với các kịch bản khác nhau.
        
        Args:
            policy: Policy to predict
            scenario: Prediction scenario ('current_trend', 'optimistic', 'pessimistic', 'disruptive')
            
        Returns:
            Dictionary with evolution predictions
        """
        if len(policy.assessments) < 3:
            return {
                'error': 'Insufficient data for trajectory prediction',
                'required_assessments': 3,
                'available_assessments': len(policy.assessments)
            }
        
        # Prepare historical data
        assessments = sorted(policy.assessments, key=lambda x: x.assessment_date)
        
        base_date = assessments[0].assessment_date
        days = [(a.assessment_date - base_date).days for a in assessments]
        overall_scores = [a.overall_score for a in assessments]
        
        # Individual criteria trends
        criteria_data = {
            'scope': [a.criteria.scope for a in assessments],
            'magnitude': [a.criteria.magnitude for a in assessments],
            'durability': [a.criteria.durability for a in assessments],
            'adaptability': [a.criteria.adaptability for a in assessments],
            'cross_referencing': [a.criteria.cross_referencing for a in assessments]
        }
        
        # Calculate scenario multipliers
        scenario_multipliers = {
            'current_trend': 1.0,
            'optimistic': 1.2,
            'pessimistic': 0.8,
            'disruptive': 0.5  # Major disruption could reset trajectory
        }
        
        multiplier = scenario_multipliers.get(scenario, 1.0)
        
        # Predict using polynomial fitting for more complex trends
        from sklearn.preprocessing import PolynomialFeatures
        from sklearn.linear_model import LinearRegression
        from sklearn.pipeline import Pipeline
        
        # Use polynomial degree based on data points
        poly_degree = min(2, len(assessments) - 1)
        
        X = np.array(days).reshape(-1, 1)
        y = np.array(overall_scores)
        
        # Create polynomial model
        poly_model = Pipeline([
            ('poly', PolynomialFeatures(degree=poly_degree)),
            ('linear', LinearRegression())
        ])
        
        poly_model.fit(X, y)
        
        # Generate future predictions (next 3 years)
        future_months = range(1, 37)  # 36 months
        future_days = [max(days) + (30 * month) for month in future_months]
        
        X_future = np.array(future_days).reshape(-1, 1)
        base_predictions = poly_model.predict(X_future)
        
        # Apply scenario multiplier and constraints
        scenario_predictions = []
        for pred in base_predictions:
            adjusted_pred = pred * multiplier
            # Constrain to valid range [0, 5]
            adjusted_pred = max(0, min(5, adjusted_pred))
            scenario_predictions.append(adjusted_pred)
        
        # Calculate trajectory characteristics
        trajectory_slope = np.mean(np.diff(scenario_predictions))
        trajectory_volatility = np.std(scenario_predictions)
        
        # Predict individual criteria evolution
        criteria_predictions = {}
        for criterion, scores in criteria_data.items():
            if len(set(scores)) > 1:  # Only if there's variation
                criterion_model = Pipeline([
                    ('poly', PolynomialFeatures(degree=poly_degree)),
                    ('linear', LinearRegression())
                ])
                criterion_model.fit(X, np.array(scores))
                criterion_pred = criterion_model.predict(X_future[-12:])  # Last 12 months
                criteria_predictions[criterion] = {
                    'trend': 'improving' if np.mean(np.diff(criterion_pred)) > 0 else 'declining',
                    'final_score': max(0, min(5, criterion_pred[-1] * multiplier))
                }
        
        return {
            'policy_id': policy.id,
            'policy_name': policy.name,
            'scenario': scenario,
            'prediction_horizon': '36 months',
            'trajectory_characteristics': {
                'slope': trajectory_slope,
                'volatility': trajectory_volatility,
                'trend_direction': 'improving' if trajectory_slope > 0 else 'declining',
                'stability': 'stable' if trajectory_volatility < 0.3 else 'volatile'
            },
            'predictions': [
                {
                    'month': i + 1,
                    'predicted_score': float(scenario_predictions[i]),
                    'confidence': max(0.5, 1.0 - (i * 0.02))  # Decreasing confidence over time
                }
                for i in range(len(scenario_predictions))
            ],
            'criteria_evolution': criteria_predictions,
            'key_milestones': self._identify_prediction_milestones(scenario_predictions, future_months)
        }
    
    def _calculate_trends(self, dates: List[datetime], score_series: Dict[str, List[float]]) -> Dict[str, Dict]:
        """Calculate trend statistics for score series."""
        trends = {}
        
        # Convert dates to numeric format for regression
        base_date = min(dates)
        days = [(d - base_date).days for d in dates]
        
        for series_name, scores in score_series.items():
            if len(scores) < 2:
                trends[series_name] = {'error': 'Insufficient data'}
                continue
            
            # Linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(days, scores)
            
            trends[series_name] = {
                'slope': slope,
                'r_squared': r_value**2,
                'p_value': p_value,
                'direction': 'improving' if slope > 0 else 'declining' if slope < 0 else 'stable',
                'significance': 'significant' if p_value < 0.05 else 'not_significant'
            }
        
        return trends
    
    def _identify_performance_phases(self, dates: List[datetime], scores: List[float]) -> List[Dict]:
        """Identify distinct performance phases in policy evolution."""
        if len(scores) < 3:
            return []
        
        # Simple phase identification based on score changes
        phases = []
        current_phase = {
            'start_date': dates[0],
            'phase_type': 'initial',
            'start_score': scores[0]
        }
        
        for i in range(1, len(scores)):
            score_change = scores[i] - scores[i-1]
            
            # Detect significant changes (threshold can be adjusted)
            if abs(score_change) > 0.5:
                # End current phase
                current_phase['end_date'] = dates[i-1]
                current_phase['end_score'] = scores[i-1]
                current_phase['duration_days'] = (current_phase['end_date'] - current_phase['start_date']).days
                phases.append(current_phase)
                
                # Start new phase
                current_phase = {
                    'start_date': dates[i],
                    'phase_type': 'improvement' if score_change > 0 else 'decline',
                    'start_score': scores[i]
                }
        
        # Close final phase
        if 'end_date' not in current_phase:
            current_phase['end_date'] = dates[-1]
            current_phase['end_score'] = scores[-1]
            current_phase['duration_days'] = (current_phase['end_date'] - current_phase['start_date']).days
            phases.append(current_phase)
        
        return phases
    
    def _perform_statistical_tests(self, df: pd.DataFrame, criteria_cols: List[str]) -> Dict:
        """Perform statistical tests on policy comparison data."""
        tests = {}
        
        # ANOVA test for differences between policies
        if len(df) > 2:
            try:
                f_stat, p_value = stats.f_oneway(*[df[col] for col in criteria_cols])
                tests['anova'] = {
                    'f_statistic': f_stat,
                    'p_value': p_value,
                    'significant_difference': p_value < 0.05
                }
            except Exception as e:
                tests['anova'] = {'error': str(e)}
        
        return tests
    
    def _analyze_policy_lifecycle(self, policies: List[Policy]) -> Dict:
        """Analyze policy lifecycle patterns."""
        lifecycle_data = []
        
        for policy in policies:
            if policy.assessments:
                lifecycle_data.append({
                    'implementation_year': policy.implementation_year,
                    'years_active': policy.years_since_implementation,
                    'assessment_count': len(policy.assessments),
                    'latest_score': policy.get_latest_assessment().overall_score
                })
        
        if not lifecycle_data:
            return {'error': 'No lifecycle data available'}
        
        df = pd.DataFrame(lifecycle_data)
        
        return {
            'average_years_active': df['years_active'].mean(),
            'average_assessments_per_policy': df['assessment_count'].mean(),
            'implementation_distribution': df['implementation_year'].value_counts().to_dict(),
            'maturity_vs_performance': {
                'correlation': df['years_active'].corr(df['latest_score'])
            }
        }
    
    def _analyze_performance_distribution(self, df: pd.DataFrame) -> Dict:
        """Analyze the distribution of performance scores."""
        return {
            'overall_score_distribution': {
                'mean': df['overall_score'].mean(),
                'median': df['overall_score'].median(),
                'std': df['overall_score'].std(),
                'min': df['overall_score'].min(),
                'max': df['overall_score'].max(),
                'quartiles': {
                    'q1': df['overall_score'].quantile(0.25),
                    'q3': df['overall_score'].quantile(0.75)
                }
            },
            'criteria_distributions': {
                col: {
                    'mean': df[col].mean(),
                    'std': df[col].std()
                }
                for col in ['scope', 'magnitude', 'durability', 'adaptability', 'cross_referencing']
            }
        }
    
    def _generate_category_insights(self, df: pd.DataFrame, policies: List[Policy]) -> List[str]:
        """Generate textual insights about category performance."""
        insights = []
        
        # Average performance insight
        avg_score = df['overall_score'].mean()
        if avg_score >= 4.0:
            insights.append("Category shows excellent overall performance with high impact scores.")
        elif avg_score >= 3.0:
            insights.append("Category demonstrates solid performance with good impact outcomes.")
        else:
            insights.append("Category has room for improvement in policy effectiveness.")
        
        # Trend insight
        if len(df) > 1:
            recent_scores = df.nlargest(int(len(df)*0.3), 'assessment_date')['overall_score'].mean()
            older_scores = df.nsmallest(int(len(df)*0.3), 'assessment_date')['overall_score'].mean()
            
            if recent_scores > older_scores + 0.2:
                insights.append("Recent policies show improved performance compared to earlier implementations.")
            elif recent_scores < older_scores - 0.2:
                insights.append("Policy effectiveness appears to have declined in recent implementations.")
        
        # Durability insight
        avg_durability = df['durability'].mean()
        if avg_durability >= 4.0:
            insights.append("Policies in this category demonstrate strong long-term sustainability.")
        elif avg_durability < 2.5:
            insights.append("Long-term durability is a concern for policies in this category.")
        
        return insights
    
    def _calculate_synergy_effects(self, policies: List[Policy], interconnections: Dict) -> Dict[str, Any]:
        """Calculate synergy effects between interconnected policies."""
        synergy_effects = {
            'high_synergy_pairs': [],
            'category_synergies': {},
            'agency_synergies': {}
        }
        
        # Analyze direct links for synergy
        for link in interconnections['direct_links']:
            policy1 = link['policy1']
            policy2 = link['policy2']
            
            # Get latest assessments
            assess1 = policy1.get_latest_assessment()
            assess2 = policy2.get_latest_assessment()
            
            if assess1 and assess2:
                # Calculate synergy score (both policies performing well together)
                combined_score = (assess1.overall_score + assess2.overall_score) / 2
                
                if combined_score >= 4.0:
                    synergy_effects['high_synergy_pairs'].append({
                        'policy1': policy1.name,
                        'policy2': policy2.name,
                        'synergy_score': combined_score,
                        'link_type': link['link_type']
                    })
        
        return synergy_effects
    
    def _generate_concatenation_insights(self, temporal_patterns: Dict, 
                                       interconnections: Dict, 
                                       synergy_effects: Dict) -> List[str]:
        """Generate insights about policy concatenation effects."""
        insights = []
        
        # Slow burn insights
        if temporal_patterns['slow_burn_policies']:
            count = len(temporal_patterns['slow_burn_policies'])
            insights.append(f"Identified {count} 'slow burn' policies that started with low impact "
                          f"but developed significant effectiveness over time.")
        
        # Immediate response insights
        if temporal_patterns['immediate_response_policies']:
            count = len(temporal_patterns['immediate_response_policies'])
            insights.append(f"Found {count} policies with immediate high impact, "
                          f"demonstrating effective rapid deployment capabilities.")
        
        # Interconnection insights
        if interconnections['policy_chains']:
            insights.append("Policy evolution chains detected, showing how newer policies "
                          "build upon the foundation of earlier implementations.")
        
        # Synergy insights
        if synergy_effects['high_synergy_pairs']:
            insights.append("High-synergy policy pairs identified, suggesting coordinated "
                          "policy design enhances overall effectiveness.")
        
        return insights
    
    def _generate_contextual_insights(self, timing_analysis: Dict) -> List[str]:
        """Generate insights about contextual timing effects."""
        insights = []
        
        if timing_analysis['well_timed_policies']:
            insights.append("Several policies demonstrated excellent timing alignment "
                          "with contextual needs, achieving high impact scores.")
        
        if timing_analysis['proactive_policies']:
            insights.append("Proactive policy implementation before crisis periods "
                          "showed superior preparation and effectiveness.")
        
        if timing_analysis['reactive_policies']:
            reactive_count = len(timing_analysis['reactive_policies'])
            insights.append(f"Identified {reactive_count} reactive policies implemented "
                          f"in response to crisis situations.")
        
        return insights
    
    def _identify_prediction_milestones(self, predictions: List[float], months: range) -> List[Dict]:
        """Identify key milestones in prediction trajectory."""
        milestones = []
        
        # Score crossing thresholds
        thresholds = [3.0, 3.5, 4.0, 4.5]
        
        for i, score in enumerate(predictions):
            month = months[i] if i < len(months) else i + 1
            
            for threshold in thresholds:
                if i > 0 and predictions[i-1] < threshold <= score:
                    milestones.append({
                        'month': month,
                        'milestone': f'Crosses {threshold} threshold',
                        'predicted_score': score
                    })
                elif i > 0 and predictions[i-1] > threshold >= score:
                    milestones.append({
                        'month': month,
                        'milestone': f'Falls below {threshold} threshold',
                        'predicted_score': score
                    })
        
        return milestones
