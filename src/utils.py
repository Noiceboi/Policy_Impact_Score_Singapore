"""
Utility functions for the Policy Impact Assessment Framework.

This module provides common utility functions for data processing,
validation, file operations, and other supporting functionality.
"""

import csv
import json
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
import logging

from models import Policy, PolicyAssessment, AssessmentCriteria, PolicyCategory


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Set up logging configuration for the framework.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Configured logger instance
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    return logging.getLogger('PolicyFramework')


def validate_assessment_scores(scores: Dict[str, int]) -> bool:
    """
    Validate that assessment scores are within valid ranges.
    
    Args:
        scores: Dictionary of criterion names and scores
        
    Returns:
        True if all scores are valid, raises ValueError otherwise
    """
    required_criteria = ['scope', 'magnitude', 'durability', 'adaptability', 'cross_referencing']
    
    for criterion in required_criteria:
        if criterion not in scores:
            raise ValueError(f"Missing required criterion: {criterion}")
        
        score = scores[criterion]
        if not isinstance(score, int) or not 0 <= score <= 5:
            raise ValueError(f"Score for {criterion} must be an integer between 0 and 5, got {score}")
    
    return True


def normalize_category_name(category: Union[str, PolicyCategory]) -> str:
    """
    Normalize policy category names to standard format.
    
    Args:
        category: Category name or PolicyCategory enum
        
    Returns:
        Normalized category name string
    """
    if isinstance(category, PolicyCategory):
        return category.value
    
    # Mapping of common variations to standard names
    category_mapping = {
        'social welfare': 'An sinh xã hội',
        'urban order': 'Giữ gìn trật tự đô thị',
        'economic': 'Kinh tế tài chính',
        'finance': 'Kinh tế tài chính',
        'economic & financial': 'Kinh tế tài chính',
        'social wellbeing': 'Phúc lợi xã hội',
        'social well-being': 'Phúc lợi xã hội',
        'taxation': 'Thuế',
        'tax': 'Thuế',
        'security': 'An ninh quốc phòng',
        'defense': 'An ninh quốc phòng',
        'national security': 'An ninh quốc phòng',
        'culture': 'Văn hóa xã hội',
        'society': 'Văn hóa xã hội',
        'culture & society': 'Văn hóa xã hội',
        'education': 'Giáo dục',
        'urban development': 'Phát triển đô thị',
        'development': 'Phát triển đô thị',
        'healthcare': 'Chăm sóc sức khỏe',
        'health': 'Chăm sóc sức khỏe',
        'health care': 'Chăm sóc sức khỏe'
    }
    
    category_lower = category.lower().strip()
    return category_mapping.get(category_lower, category)


def export_to_excel(policies: List[Policy], file_path: str) -> None:
    """
    Export policies and assessments to Excel file with multiple sheets.
    
    Args:
        policies: List of policies to export
        file_path: Output Excel file path
    """
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        # Policy summary sheet
        policy_data = []
        for policy in policies:
            latest_assessment = policy.get_latest_assessment()
            
            policy_data.append({
                'ID': policy.id,
                'Name': policy.name,
                'Category': policy.category_name,
                'Implementation Year': policy.implementation_year,
                'Years Active': policy.years_since_implementation,
                'Description': policy.description,
                'Implementing Agency': policy.implementing_agency,
                'Budget': policy.budget,
                'Objectives': '; '.join(policy.objectives) if policy.objectives else '',
                'Latest Score': latest_assessment.overall_score if latest_assessment else None,
                'Assessment Count': len(policy.assessments)
            })
        
        pd.DataFrame(policy_data).to_excel(writer, sheet_name='Policies', index=False)
        
        # Detailed assessments sheet
        assessment_data = []
        for policy in policies:
            for assessment in policy.assessments:
                assessment_data.append({
                    'Policy ID': policy.id,
                    'Policy Name': policy.name,
                    'Category': policy.category_name,
                    'Assessment Date': assessment.assessment_date,
                    'Scope': assessment.criteria.scope,
                    'Magnitude': assessment.criteria.magnitude,
                    'Durability': assessment.criteria.durability,
                    'Adaptability': assessment.criteria.adaptability,
                    'Cross-referencing': assessment.criteria.cross_referencing,
                    'Overall Score': assessment.overall_score,
                    'Assessor': assessment.assessor,
                    'Notes': assessment.notes
                })
        
        if assessment_data:
            pd.DataFrame(assessment_data).to_excel(writer, sheet_name='Assessments', index=False)
        
        # Category summary sheet
        categories = {}
        for policy in policies:
            category = policy.category_name
            if category not in categories:
                categories[category] = {'policies': [], 'scores': []}
            
            categories[category]['policies'].append(policy.name)
            latest_assessment = policy.get_latest_assessment()
            if latest_assessment:
                categories[category]['scores'].append(latest_assessment.overall_score)
        
        category_summary = []
        for category, data in categories.items():
            scores = data['scores']
            category_summary.append({
                'Category': category,
                'Policy Count': len(data['policies']),
                'Assessed Policies': len(scores),
                'Average Score': sum(scores) / len(scores) if scores else None,
                'Min Score': min(scores) if scores else None,
                'Max Score': max(scores) if scores else None,
                'Policy Names': '; '.join(data['policies'])
            })
        
        pd.DataFrame(category_summary).to_excel(writer, sheet_name='Category Summary', index=False)


def import_from_excel(file_path: str) -> List[Policy]:
    """
    Import policies from Excel file.
    
    Args:
        file_path: Path to Excel file
        
    Returns:
        List of Policy objects
    """
    policies = []
    
    try:
        # Read policies sheet
        df_policies = pd.read_excel(file_path, sheet_name='Policies')
        
        for _, row in df_policies.iterrows():
            policy = Policy(
                id=str(row['ID']),
                name=row['Name'],
                category=row['Category'],
                implementation_year=int(row['Implementation Year']),
                description=row.get('Description') if pd.notna(row.get('Description')) else None,
                implementing_agency=row.get('Implementing Agency') if pd.notna(row.get('Implementing Agency')) else None,
                budget=row.get('Budget') if pd.notna(row.get('Budget')) else None
            )
            
            # Add objectives if present
            if 'Objectives' in row and pd.notna(row['Objectives']):
                policy.objectives = [obj.strip() for obj in str(row['Objectives']).split(';')]
            
            policies.append(policy)
        
        # Read assessments if available
        try:
            df_assessments = pd.read_excel(file_path, sheet_name='Assessments')
            
            for _, row in df_assessments.iterrows():
                policy_id = str(row['Policy ID'])
                policy = next((p for p in policies if p.id == policy_id), None)
                
                if policy:
                    criteria = AssessmentCriteria(
                        scope=int(row['Scope']),
                        magnitude=int(row['Magnitude']),
                        durability=int(row['Durability']),
                        adaptability=int(row['Adaptability']),
                        cross_referencing=int(row['Cross-referencing'])
                    )
                    
                    assessment = PolicyAssessment(
                        policy_id=policy_id,
                        assessment_date=pd.to_datetime(row['Assessment Date']),
                        criteria=criteria,
                        assessor=row.get('Assessor') if pd.notna(row.get('Assessor')) else None,
                        notes=row.get('Notes') if pd.notna(row.get('Notes')) else None
                    )
                    
                    policy.add_assessment(assessment)
        
        except Exception as e:
            logging.warning(f"Could not import assessments: {e}")
    
    except Exception as e:
        raise ValueError(f"Error importing from Excel: {e}")
    
    return policies


def calculate_weighted_score(
    criteria: AssessmentCriteria, 
    weights: Optional[Dict[str, float]] = None
) -> float:
    """
    Calculate weighted impact score with custom weights.
    
    Args:
        criteria: AssessmentCriteria object
        weights: Custom weights dictionary (optional)
        
    Returns:
        Weighted score (0-5 scale)
    """
    default_weights = {
        'scope': 1.0,
        'magnitude': 1.5,
        'durability': 2.0,
        'adaptability': 1.5,
        'cross_referencing': 1.0
    }
    
    if weights:
        default_weights.update(weights)
    
    weighted_sum = (
        criteria.scope * default_weights['scope'] +
        criteria.magnitude * default_weights['magnitude'] +
        criteria.durability * default_weights['durability'] +
        criteria.adaptability * default_weights['adaptability'] +
        criteria.cross_referencing * default_weights['cross_referencing']
    )
    
    total_weight = sum(default_weights.values())
    return weighted_sum / total_weight


def create_sample_data() -> List[Policy]:
    """
    Create sample policy data for testing and demonstration.
    
    Returns:
        List of sample Policy objects with assessments
    """
    sample_policies = [
        {
            'id': 'HDB-001',
            'name': 'Housing Development Act',
            'category': 'Phát triển đô thị',
            'implementation_year': 1960,
            'description': 'Comprehensive public housing program for Singapore residents',
            'implementing_agency': 'Housing & Development Board',
            'objectives': ['Provide affordable housing', 'Urban planning', 'Community development'],
            'assessments': [
                {'date': '2020-01-15', 'scope': 5, 'magnitude': 5, 'durability': 5, 'adaptability': 4, 'cross_referencing': 5},
                {'date': '2022-06-10', 'scope': 5, 'magnitude': 5, 'durability': 5, 'adaptability': 5, 'cross_referencing': 5}
            ]
        },
        {
            'id': 'CPF-001',
            'name': 'Central Provident Fund',
            'category': 'An sinh xã hội',
            'implementation_year': 1955,
            'description': 'Mandatory savings scheme for retirement and healthcare',
            'implementing_agency': 'CPF Board',
            'objectives': ['Retirement savings', 'Healthcare coverage', 'Housing finance'],
            'assessments': [
                {'date': '2021-03-20', 'scope': 5, 'magnitude': 4, 'durability': 5, 'adaptability': 4, 'cross_referencing': 4}
            ]
        },
        {
            'id': 'GST-001',
            'name': 'Goods and Services Tax',
            'category': 'Thuế',
            'implementation_year': 1994,
            'description': 'Consumption tax system for government revenue',
            'implementing_agency': 'Inland Revenue Authority of Singapore',
            'objectives': ['Government revenue', 'Tax efficiency', 'Economic growth'],
            'assessments': [
                {'date': '2019-11-05', 'scope': 4, 'magnitude': 3, 'durability': 4, 'adaptability': 3, 'cross_referencing': 3},
                {'date': '2023-02-15', 'scope': 4, 'magnitude': 3, 'durability': 4, 'adaptability': 4, 'cross_referencing': 3}
            ]
        },
        {
            'id': 'EDU-001',
            'name': 'SkillsFuture Initiative',
            'category': 'Giáo dục',
            'implementation_year': 2015,
            'description': 'National movement to provide opportunities for lifelong learning',
            'implementing_agency': 'SkillsFuture Singapore',
            'objectives': ['Lifelong learning', 'Skills upgrading', 'Economic competitiveness'],
            'assessments': [
                {'date': '2020-08-12', 'scope': 4, 'magnitude': 4, 'durability': 3, 'adaptability': 5, 'cross_referencing': 4}
            ]
        },
        {
            'id': 'HC-001',
            'name': 'Medisave Scheme',
            'category': 'Chăm sóc sức khỏe',
            'implementation_year': 1984,
            'description': 'Medical savings account for healthcare expenses',
            'implementing_agency': 'Ministry of Health',
            'objectives': ['Healthcare financing', 'Medical cost control', 'Health security'],
            'assessments': [
                {'date': '2021-12-03', 'scope': 4, 'magnitude': 4, 'durability': 4, 'adaptability': 3, 'cross_referencing': 4}
            ]
        }
    ]
    
    policies = []
    
    for policy_data in sample_policies:
        policy = Policy(
            id=policy_data['id'],
            name=policy_data['name'],
            category=policy_data['category'],
            implementation_year=policy_data['implementation_year'],
            description=policy_data['description'],
            implementing_agency=policy_data['implementing_agency'],
            objectives=policy_data['objectives']
        )
        
        for assessment_data in policy_data['assessments']:
            criteria = AssessmentCriteria(
                scope=assessment_data['scope'],
                magnitude=assessment_data['magnitude'],
                durability=assessment_data['durability'],
                adaptability=assessment_data['adaptability'],
                cross_referencing=assessment_data['cross_referencing']
            )
            
            assessment = PolicyAssessment(
                policy_id=policy.id,
                assessment_date=datetime.strptime(assessment_data['date'], '%Y-%m-%d'),
                criteria=criteria,
                assessor='Sample Data Generator'
            )
            
            policy.add_assessment(assessment)
        
        policies.append(policy)
    
    return policies


def format_score_for_display(score: float, decimal_places: int = 2) -> str:
    """
    Format score for display with appropriate precision and color coding.
    
    Args:
        score: Numerical score to format
        decimal_places: Number of decimal places to show
        
    Returns:
        Formatted score string
    """
    formatted = f"{score:.{decimal_places}f}"
    
    # Add performance indicators
    if score >= 4.5:
        return f"🟢 {formatted} (Excellent)"
    elif score >= 3.5:
        return f"🟡 {formatted} (Good)"
    elif score >= 2.5:
        return f"🟠 {formatted} (Fair)"
    else:
        return f"🔴 {formatted} (Needs Improvement)"


def get_policy_lifecycle_stage(policy: Policy) -> str:
    """
    Determine the lifecycle stage of a policy based on its age and assessment history.
    
    Args:
        policy: Policy object to analyze
        
    Returns:
        Lifecycle stage string
    """
    years_active = policy.years_since_implementation
    assessment_count = len(policy.assessments)
    
    if years_active < 2:
        return "Newly Implemented"
    elif years_active < 5:
        return "Early Stage"
    elif years_active < 10:
        return "Established"
    elif years_active < 20:
        return "Mature"
    else:
        return "Legacy"


def analyze_temporal_impact_patterns(policies: List[Policy]) -> Dict[str, Any]:
    """
    Phân tích các pattern tác động theo thời gian, bao gồm:
    - Chính sách có tác động chậm nhưng lâu dài
    - Chính sách phản ứng kịp thời với bối cảnh
    - Sự concatenate của các chính sách liên quan
    
    Args:
        policies: List of policies to analyze
        
    Returns:
        Dictionary with temporal pattern analysis
    """
    import numpy as np
    from scipy import stats
    
    temporal_patterns = {
        'slow_burn_policies': [],  # Chính sách tác động chậm nhưng mạnh về sau
        'immediate_response_policies': [],  # Chính sách phản ứng kịp thời
        'contextual_policies': [],  # Chính sách phù hợp với bối cảnh thời đại
        'interconnected_clusters': []  # Cụm chính sách liên kết
    }
    
    for policy in policies:
        if len(policy.assessments) < 2:
            continue
            
        # Sort assessments by date
        sorted_assessments = sorted(policy.assessments, key=lambda x: x.assessment_date)
        
        # Tính trajectory của impact score
        scores = [a.overall_score for a in sorted_assessments]
        times = [(a.assessment_date - sorted_assessments[0].assessment_date).days 
                for a in sorted_assessments]
        
        # Phân tích trend
        if len(scores) >= 3:
            slope, intercept, r_value, p_value, std_err = stats.linregress(times, scores)
            
            # Slow burn policy: điểm đầu thấp nhưng tăng mạnh theo thời gian
            initial_score = scores[0]
            latest_score = scores[-1]
            
            if (slope > 0.01 and  # Trend tăng
                initial_score < 3.0 and  # Điểm đầu thấp
                latest_score > 4.0 and  # Điểm cuối cao
                r_value > 0.7):  # Correlation mạnh
                
                temporal_patterns['slow_burn_policies'].append({
                    'policy': policy,
                    'initial_score': initial_score,
                    'latest_score': latest_score,
                    'improvement_rate': slope,
                    'correlation': r_value,
                    'years_to_maturity': (sorted_assessments[-1].assessment_date - 
                                        sorted_assessments[0].assessment_date).days / 365.25
                })
        
        # Immediate response policy: có điểm cao ngay từ đầu
        if (len(policy.assessments) >= 1 and 
            policy.assessments[0].overall_score >= 4.0 and
            policy.years_since_implementation <= 3):
            
            temporal_patterns['immediate_response_policies'].append({
                'policy': policy,
                'initial_score': policy.assessments[0].overall_score,
                'implementation_year': policy.implementation_year,
                'rapid_deployment': True
            })
    
    # Phân tích contextual relevance (dựa trên implementation year và global events)
    contextual_events = {
        1997: "Asian Financial Crisis",
        2003: "SARS Outbreak",
        2008: "Global Financial Crisis", 
        2020: "COVID-19 Pandemic",
        2001: "9/11 Security Concerns",
        1965: "Independence Period",
        1987: "Economic Restructuring"
    }
    
    for policy in policies:
        for event_year, event_name in contextual_events.items():
            if abs(policy.implementation_year - event_year) <= 2:  # Within 2 years
                latest_assessment = policy.get_latest_assessment()
                if latest_assessment and latest_assessment.overall_score >= 3.5:
                    temporal_patterns['contextual_policies'].append({
                        'policy': policy,
                        'context_event': event_name,
                        'event_year': event_year,
                        'policy_year': policy.implementation_year,
                        'relevance_score': latest_assessment.overall_score,
                        'timing_advantage': abs(policy.implementation_year - event_year)
                    })
    
    return temporal_patterns


def identify_policy_interconnections(policies: List[Policy]) -> Dict[str, Any]:
    """
    Nhận diện các mối liên hệ trực tiếp và gián tiếp giữa các chính sách.
    
    Args:
        policies: List of policies to analyze
        
    Returns:
        Dictionary with interconnection analysis
    """
    interconnections = {
        'direct_links': [],  # Liên kết trực tiếp (cùng category, agency)
        'indirect_links': [],  # Liên kết gián tiếp (objectives, target groups)
        'policy_chains': [],  # Chuỗi chính sách phát triển từ nhau
        'synergy_clusters': []  # Cụm chính sách có synergy cao
    }
    
    # Direct links - cùng implementing agency hoặc category
    for i, policy1 in enumerate(policies):
        for j, policy2 in enumerate(policies[i+1:], i+1):
            
            # Same implementing agency
            if (policy1.implementing_agency and policy2.implementing_agency and
                policy1.implementing_agency == policy2.implementing_agency):
                
                interconnections['direct_links'].append({
                    'policy1': policy1,
                    'policy2': policy2,
                    'link_type': 'same_agency',
                    'agency': policy1.implementing_agency
                })
            
            # Same category
            if policy1.category_name == policy2.category_name:
                interconnections['direct_links'].append({
                    'policy1': policy1,
                    'policy2': policy2,
                    'link_type': 'same_category',
                    'category': policy1.category_name
                })
    
    # Indirect links - shared objectives
    for i, policy1 in enumerate(policies):
        for j, policy2 in enumerate(policies[i+1:], i+1):
            if policy1.objectives and policy2.objectives:
                shared_objectives = set(policy1.objectives) & set(policy2.objectives)
                if shared_objectives:
                    interconnections['indirect_links'].append({
                        'policy1': policy1,
                        'policy2': policy2,
                        'link_type': 'shared_objectives',
                        'shared_objectives': list(shared_objectives),
                        'overlap_ratio': len(shared_objectives) / 
                                       len(set(policy1.objectives) | set(policy2.objectives))
                    })
    
    # Policy chains - chính sách phát triển theo thời gian
    category_timelines = {}
    for policy in policies:
        category = policy.category_name
        if category not in category_timelines:
            category_timelines[category] = []
        category_timelines[category].append(policy)
    
    for category, category_policies in category_timelines.items():
        if len(category_policies) >= 2:
            # Sort by implementation year
            sorted_policies = sorted(category_policies, key=lambda p: p.implementation_year)
            
            chains = []
            for i in range(len(sorted_policies) - 1):
                current = sorted_policies[i]
                next_policy = sorted_policies[i + 1]
                
                # Check if there's evolutionary relationship
                time_gap = next_policy.implementation_year - current.implementation_year
                if 1 <= time_gap <= 15:  # Reasonable evolution timeframe
                    chains.append({
                        'predecessor': current,
                        'successor': next_policy,
                        'time_gap': time_gap,
                        'category': category
                    })
            
            if chains:
                interconnections['policy_chains'].append({
                    'category': category,
                    'chain': chains,
                    'evolution_span': sorted_policies[-1].implementation_year - sorted_policies[0].implementation_year
                })
    
    return interconnections


def calculate_policy_maturity_index(policy: Policy) -> Dict[str, Any]:
    """
    Tính chỉ số độ trưởng thành của chính sách dựa trên nhiều yếu tố.
    
    Args:
        policy: Policy to analyze
        
    Returns:
        Dictionary with maturity analysis
    """
    maturity_factors = {
        'temporal_stability': 0,  # Ổn định theo thời gian
        'adaptation_capability': 0,  # Khả năng thích ứng
        'impact_consistency': 0,  # Tính nhất quán của tác động
        'external_validation': 0,  # Xác thực từ bên ngoài
        'longevity_bonus': 0  # Điểm thưởng cho tuổi thọ
    }
    
    if not policy.assessments:
        return {'maturity_index': 0, 'factors': maturity_factors, 'stage': 'unassessed'}
    
    # Temporal stability - ít biến động qua thời gian
    if len(policy.assessments) >= 2:
        scores = [a.overall_score for a in policy.assessments]
        stability = 1.0 - (np.std(scores) / 5.0)  # Normalize by max possible std
        maturity_factors['temporal_stability'] = max(0, stability)
    
    # Adaptation capability - từ adaptability scores
    latest_assessment = policy.get_latest_assessment()
    if latest_assessment:
        maturity_factors['adaptation_capability'] = latest_assessment.criteria.adaptability / 5.0
        maturity_factors['external_validation'] = latest_assessment.criteria.cross_referencing / 5.0
    
    # Impact consistency - durability average
    if policy.assessments:
        durability_scores = [a.criteria.durability for a in policy.assessments]
        maturity_factors['impact_consistency'] = np.mean(durability_scores) / 5.0
    
    # Longevity bonus
    years_active = policy.years_since_implementation
    if years_active >= 20:
        maturity_factors['longevity_bonus'] = 1.0
    elif years_active >= 10:
        maturity_factors['longevity_bonus'] = 0.7
    elif years_active >= 5:
        maturity_factors['longevity_bonus'] = 0.4
    else:
        maturity_factors['longevity_bonus'] = 0.1
    
    # Calculate overall maturity index
    weights = {
        'temporal_stability': 0.25,
        'adaptation_capability': 0.25,
        'impact_consistency': 0.25,
        'external_validation': 0.15,
        'longevity_bonus': 0.10
    }
    
    maturity_index = sum(maturity_factors[factor] * weights[factor] 
                        for factor in maturity_factors)
    
    # Determine maturity stage
    if maturity_index >= 0.8:
        stage = 'Highly Mature'
    elif maturity_index >= 0.6:
        stage = 'Mature'
    elif maturity_index >= 0.4:
        stage = 'Developing'
    elif maturity_index >= 0.2:
        stage = 'Early Stage'
    else:
        stage = 'Nascent'
    
    return {
        'maturity_index': maturity_index,
        'factors': maturity_factors,
        'stage': stage,
        'years_active': years_active,
        'assessment_count': len(policy.assessments)
    }


def detect_contextual_timing_advantage(policies: List[Policy]) -> Dict[str, Any]:
    """
    Phát hiện các chính sách có lợi thế về thời điểm triển khai (kịp thời với bối cảnh).
    
    Args:
        policies: List of policies to analyze
        
    Returns:
        Dictionary with timing advantage analysis
    """
    # Define major contextual periods and their characteristics
    contextual_periods = {
        (1965, 1970): {
            'context': 'Independence & Nation Building',
            'priorities': ['national_identity', 'basic_infrastructure', 'security'],
            'urgency': 'high'
        },
        (1980, 1990): {
            'context': 'Economic Transformation',
            'priorities': ['industrialization', 'education', 'housing'],
            'urgency': 'medium'
        },
        (1997, 1999): {
            'context': 'Asian Financial Crisis',
            'priorities': ['financial_stability', 'economic_resilience'],
            'urgency': 'high'
        },
        (2003, 2004): {
            'context': 'SARS Health Crisis',
            'priorities': ['healthcare', 'crisis_management', 'public_health'],
            'urgency': 'high'
        },
        (2008, 2010): {
            'context': 'Global Financial Crisis',
            'priorities': ['economic_stimulus', 'job_security', 'financial_regulation'],
            'urgency': 'high'
        },
        (2020, 2023): {
            'context': 'COVID-19 Pandemic',
            'priorities': ['healthcare', 'digital_transformation', 'social_support'],
            'urgency': 'high'
        }
    }
    
    timing_analysis = {
        'well_timed_policies': [],
        'missed_opportunities': [],
        'proactive_policies': [],
        'reactive_policies': []
    }
    
    for policy in policies:
        policy_year = policy.implementation_year
        latest_assessment = policy.get_latest_assessment()
        
        if not latest_assessment:
            continue
        
        # Check against contextual periods
        for (start_year, end_year), period_info in contextual_periods.items():
            
            # Policy implemented during crisis period
            if start_year <= policy_year <= end_year:
                timing_score = latest_assessment.overall_score
                
                # Check if policy aligns with period priorities
                policy_relevance = 0
                for priority in period_info['priorities']:
                    if any(priority.lower() in obj.lower() for obj in policy.objectives):
                        policy_relevance += 1
                
                if timing_score >= 3.5 and policy_relevance > 0:
                    timing_analysis['well_timed_policies'].append({
                        'policy': policy,
                        'context': period_info['context'],
                        'timing_score': timing_score,
                        'relevance_score': policy_relevance,
                        'urgency_level': period_info['urgency'],
                        'implementation_year': policy_year
                    })
            
            # Policy implemented just before crisis (proactive)
            elif start_year - 3 <= policy_year < start_year:
                if latest_assessment.overall_score >= 3.5:
                    timing_analysis['proactive_policies'].append({
                        'policy': policy,
                        'upcoming_context': period_info['context'],
                        'preparation_time': start_year - policy_year,
                        'effectiveness': latest_assessment.overall_score
                    })
            
            # Policy implemented after crisis (reactive)
            elif end_year < policy_year <= end_year + 3:
                timing_analysis['reactive_policies'].append({
                    'policy': policy,
                    'past_context': period_info['context'],
                    'response_delay': policy_year - end_year,
                    'effectiveness': latest_assessment.overall_score
                })
    
    return timing_analysis


def validate_data_consistency(policies: List[Policy]) -> Dict[str, List[str]]:
    """
    Validate data consistency across policies and assessments.
    
    Args:
        policies: List of policies to validate
        
    Returns:
        Dictionary with validation results and warnings
    """
    warnings = []
    errors = []
    
    policy_ids = set()
    for policy in policies:
        # Check for duplicate IDs
        if policy.id in policy_ids:
            errors.append(f"Duplicate policy ID found: {policy.id}")
        policy_ids.add(policy.id)
        
        # Check implementation year
        if policy.implementation_year > datetime.now().year:
            warnings.append(f"Policy {policy.name} has future implementation year: {policy.implementation_year}")
        
        # Check assessments
        assessment_dates = []
        for assessment in policy.assessments:
            if assessment.assessment_date in assessment_dates:
                warnings.append(f"Duplicate assessment date for policy {policy.name}: {assessment.assessment_date}")
            assessment_dates.append(assessment.assessment_date)
            
            # Check assessment date vs implementation
            if assessment.assessment_date.year < policy.implementation_year:
                errors.append(f"Assessment date before implementation for policy {policy.name}")
    
    return {
        'errors': errors,
        'warnings': warnings,
        'validation_passed': len(errors) == 0
    }


def analyze_policy_maturity_curve(policy: Policy) -> Dict[str, Any]:
    """
    Phân tích đường cong trưởng thành của chính sách - insight về việc chính sách có thể
    có tác động thấp lúc đầu nhưng tăng mạnh về sau.
    
    Args:
        policy: Policy object to analyze
        
    Returns:
        Dictionary with maturity curve analysis
    """
    if len(policy.assessments) < 2:
        return {
            'error': 'Insufficient data for maturity analysis',
            'required_assessments': 2,
            'available': len(policy.assessments)
        }
    
    assessments = sorted(policy.assessments, key=lambda x: x.assessment_date)
    scores = [a.overall_score for a in assessments]
    dates = [a.assessment_date for a in assessments]
    
    # Calculate growth phases
    phases = []
    for i in range(1, len(scores)):
        growth_rate = (scores[i] - scores[i-1]) / scores[i-1] if scores[i-1] > 0 else 0
        time_diff = (dates[i] - dates[i-1]).days / 365.25  # years
        
        phase = {
            'period': f"{dates[i-1].strftime('%Y-%m')} to {dates[i].strftime('%Y-%m')}",
            'start_score': scores[i-1],
            'end_score': scores[i],
            'growth_rate': growth_rate,
            'duration_years': time_diff,
            'phase_type': 'growth' if growth_rate > 0.1 else 'decline' if growth_rate < -0.1 else 'stable'
        }
        phases.append(phase)
    
    # Identify maturity pattern
    if len(scores) >= 3:
        early_avg = np.mean(scores[:len(scores)//2])
        later_avg = np.mean(scores[len(scores)//2:])
        
        maturity_pattern = {
            'early_performance': early_avg,
            'later_performance': later_avg,
            'improvement_ratio': later_avg / early_avg if early_avg > 0 else 0,
            'pattern_type': 'late_bloomer' if later_avg > early_avg * 1.2 else 
                           'early_peak' if early_avg > later_avg * 1.2 else 'stable'
        }
    else:
        maturity_pattern = {'error': 'Insufficient data for pattern analysis'}
    
    # Calculate stability and consistency
    if len(scores) > 2:
        stability = 1.0 - (np.std(scores) / 5.0)  # Normalize by max possible std
        
        # Trend strength
        x = np.arange(len(scores))
        correlation = np.corrcoef(x, scores)[0, 1] if len(scores) > 1 else 0
        
        maturity_factors = {
            'stability': stability,
            'trend_strength': abs(correlation),
            'consistency': 1.0 - (np.std(np.diff(scores)) / 5.0) if len(scores) > 1 else 0
        }
        
        # Impact consistency over time
        durability_scores = [a.criteria.durability for a in assessments]
        adaptability_scores = [a.criteria.adaptability for a in assessments]
        
        maturity_factors['impact_consistency'] = np.mean(durability_scores) / 5.0
        maturity_factors['adaptation_capability'] = np.mean(adaptability_scores) / 5.0
    else:
        maturity_factors = {'error': 'Insufficient data'}
    
    return {
        'policy_id': policy.id,
        'policy_name': policy.name,
        'maturity_pattern': maturity_pattern,
        'growth_phases': phases,
        'maturity_factors': maturity_factors,
        'assessment_span_years': (dates[-1] - dates[0]).days / 365.25,
        'insights': generate_maturity_insights(maturity_pattern, phases, maturity_factors)
    }


def analyze_contextual_relevance(policy: Policy, context_events: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """
    Phân tích mức độ phù hợp với bối cảnh - insight về chính sách được đánh giá cao
    khi kịp thời combat tình hình thời sự.
    
    Args:
        policy: Policy object to analyze
        context_events: List of contextual events with dates and descriptions
        
    Returns:
        Dictionary with contextual relevance analysis
    """
    if not policy.assessments:
        return {'error': 'No assessments available for contextual analysis'}
    
    assessments = sorted(policy.assessments, key=lambda x: x.assessment_date)
    
    # Analyze timing relevance
    implementation_relevance = {
        'implementation_year': policy.implementation_year,
        'years_since_implementation': policy.years_since_implementation,
        'lifecycle_stage': get_policy_lifecycle_stage(policy)
    }
    
    # Analyze assessment timing patterns
    assessment_patterns = []
    for i, assessment in enumerate(assessments):
        # Check for significant score changes that might indicate contextual response
        if i > 0:
            prev_assessment = assessments[i-1]
            score_change = assessment.overall_score - prev_assessment.overall_score
            time_gap = (assessment.assessment_date - prev_assessment.assessment_date).days
            
            if abs(score_change) > 0.5:  # Significant change threshold
                pattern = {
                    'assessment_date': assessment.assessment_date.isoformat(),
                    'score_change': score_change,
                    'change_type': 'improvement' if score_change > 0 else 'decline',
                    'time_since_previous': time_gap,
                    'magnitude': abs(score_change),
                    'rapid_response': time_gap < 365  # Less than a year
                }
                assessment_patterns.append(pattern)
    
    # Analyze category-specific contextual factors
    category_context = analyze_category_context_factors(policy.category_name, policy.implementation_year)
    
    # Calculate contextual scores
    contextual_scores = {
        'timing_appropriateness': calculate_timing_score(policy),
        'adaptability_response': np.mean([a.criteria.adaptability for a in assessments]),
        'cross_validation_strength': np.mean([a.criteria.cross_referencing for a in assessments]),
        'sustained_relevance': calculate_sustained_relevance(assessments)
    }
    
    return {
        'policy_id': policy.id,
        'policy_name': policy.name,
        'implementation_relevance': implementation_relevance,
        'assessment_patterns': assessment_patterns,
        'category_context': category_context,
        'contextual_scores': contextual_scores,
        'insights': generate_contextual_insights(implementation_relevance, assessment_patterns, contextual_scores)
    }


def identify_policy_interaction_patterns(policies: List[Policy]) -> Dict[str, Any]:
    """
    Nhận diện các pattern tương tác trực tiếp/gián tiếp giữa các chính sách.
    
    Args:
        policies: List of policies to analyze for interactions
        
    Returns:
        Dictionary with interaction pattern analysis
    """
    if len(policies) < 2:
        return {'error': 'At least 2 policies required for interaction analysis'}
    
    # Group policies by category and implementation period
    category_groups = {}
    time_groups = {}
    
    for policy in policies:
        # Category grouping
        category = policy.category_name
        if category not in category_groups:
            category_groups[category] = []
        category_groups[category].append(policy)
        
        # Time period grouping (by decade)
        decade = (policy.implementation_year // 10) * 10
        if decade not in time_groups:
            time_groups[decade] = []
        time_groups[decade].append(policy)
    
    # Analyze interaction patterns
    interactions = {
        'category_interactions': analyze_category_interactions(category_groups),
        'temporal_interactions': analyze_temporal_interactions(time_groups),
        'direct_dependencies': identify_direct_dependencies(policies),
        'indirect_influences': identify_indirect_influences(policies)
    }
    
    # Calculate interaction strength matrix
    interaction_matrix = calculate_policy_interaction_matrix(policies)
    
    # Identify policy clusters and networks
    policy_networks = identify_policy_networks(policies, interaction_matrix)
    
    return {
        'total_policies_analyzed': len(policies),
        'interaction_patterns': interactions,
        'interaction_matrix': interaction_matrix,
        'policy_networks': policy_networks,
        'insights': generate_interaction_insights(interactions, policy_networks)
    }


def calculate_policy_interaction_matrix(policies: List[Policy]) -> Dict[str, Dict[str, float]]:
    """Calculate interaction strength between policies."""
    matrix = {}
    
    for i, policy1 in enumerate(policies):
        matrix[policy1.id] = {}
        
        for j, policy2 in enumerate(policies):
            if i == j:
                matrix[policy1.id][policy2.id] = 1.0  # Self-interaction
                continue
            
            # Calculate interaction strength based on multiple factors
            interaction_strength = 0.0
            
            # Category similarity
            if policy1.category_name == policy2.category_name:
                interaction_strength += 0.3
            
            # Implementation time proximity
            time_diff = abs(policy1.implementation_year - policy2.implementation_year)
            if time_diff <= 5:
                interaction_strength += 0.2 * (1 - time_diff / 5)
            
            # Implementing agency similarity
            if (policy1.implementing_agency and policy2.implementing_agency and 
                policy1.implementing_agency == policy2.implementing_agency):
                interaction_strength += 0.2
            
            # Objective overlap
            if policy1.objectives and policy2.objectives:
                common_keywords = set()
                for obj1 in policy1.objectives:
                    for obj2 in policy2.objectives:
                        words1 = set(obj1.lower().split())
                        words2 = set(obj2.lower().split())
                        common_keywords.update(words1.intersection(words2))
                
                if common_keywords:
                    interaction_strength += min(0.3, len(common_keywords) * 0.1)
            
            matrix[policy1.id][policy2.id] = min(1.0, interaction_strength)
    
    return matrix


def generate_maturity_insights(maturity_pattern: Dict, phases: List[Dict], factors: Dict) -> List[str]:
    """Generate insights about policy maturity patterns."""
    insights = []
    
    if 'pattern_type' in maturity_pattern:
        if maturity_pattern['pattern_type'] == 'late_bloomer':
            insights.append("🌱 Chính sách này thể hiện pattern 'late bloomer' - tác động thấp ban đầu nhưng cải thiện đáng kể theo thời gian")
            insights.append(f"📈 Hiệu quả tăng {maturity_pattern['improvement_ratio']:.1f} lần so với giai đoạn đầu")
        
        elif maturity_pattern['pattern_type'] == 'early_peak':
            insights.append("⚡ Chính sách có tác động mạnh ngay từ đầu nhưng giảm dần theo thời gian")
            insights.append("🔄 Cần xem xét điều chỉnh hoặc cải tiến để duy trì hiệu quả")
        
        elif maturity_pattern['pattern_type'] == 'stable':
            insights.append("📊 Chính sách có hiệu quả ổn định theo thời gian")
    
    # Growth phase insights
    if phases:
        growth_phases = [p for p in phases if p['phase_type'] == 'growth']
        if len(growth_phases) > len(phases) * 0.7:
            insights.append("📈 Chính sách cho thấy xu hướng cải thiện liên tục")
    
    # Stability insights
    if 'stability' in factors and factors['stability'] > 0.8:
        insights.append("🎯 Chính sách có độ ổn định cao, dự đoán được")
    
    return insights


def generate_contextual_insights(implementation: Dict, patterns: List, scores: Dict) -> List[str]:
    """Generate insights about contextual relevance."""
    insights = []
    
    # Timing insights
    if implementation['lifecycle_stage'] == 'Legacy' and scores['sustained_relevance'] > 0.8:
        insights.append("🏛️ Chính sách lâu đời nhưng vẫn duy trì mức độ phù hợp cao với bối cảnh hiện tại")
    
    # Rapid response insights
    rapid_responses = [p for p in patterns if p.get('rapid_response', False)]
    if rapid_responses:
        insights.append(f"⚡ Chính sách được điều chỉnh nhanh chóng {len(rapid_responses)} lần để phù hợp với bối cảnh")
    
    # Adaptability insights
    if scores['adaptability_response'] >= 4.0:
        insights.append("🔄 Chính sách thể hiện khả năng thích ứng xuất sắc với thay đổi bối cảnh")
    
    return insights


def generate_interaction_insights(interactions: Dict, networks: Dict) -> List[str]:
    """Generate insights about policy interactions."""
    insights = []
    
    # Network insights
    if 'clusters' in networks and len(networks['clusters']) > 1:
        insights.append(f"🕸️ Xác định được {len(networks['clusters'])} nhóm chính sách có tương tác chặt chẽ")
    
    # Category interaction insights
    if 'category_interactions' in interactions:
        strong_interactions = [cat for cat, strength in interactions['category_interactions'].items() if strength > 0.7]
        if strong_interactions:
            insights.append(f"🔗 Các danh mục có tương tác mạnh: {', '.join(strong_interactions)}")
    
    return insights


def analyze_category_interactions(category_groups: Dict[str, List[Policy]]) -> Dict[str, float]:
    """Analyze interactions between policy categories."""
    # This is a simplified implementation - could be enhanced with more sophisticated analysis
    interactions = {}
    
    for category, policies in category_groups.items():
        if len(policies) > 1:
            # Categories with multiple policies likely have internal interactions
            interactions[category] = min(1.0, len(policies) * 0.2)
        else:
            interactions[category] = 0.1
    
    return interactions


def analyze_temporal_interactions(time_groups: Dict[int, List[Policy]]) -> Dict[str, Any]:
    """Analyze temporal interaction patterns."""
    temporal_analysis = {}
    
    for decade, policies in time_groups.items():
        if len(policies) > 1:
            # Analyze policy clustering in time periods
            avg_score = np.mean([p.get_latest_assessment().overall_score 
                               for p in policies if p.get_latest_assessment()])
            
            temporal_analysis[f"{decade}s"] = {
                'policy_count': len(policies),
                'average_performance': avg_score if not np.isnan(avg_score) else 0,
                'interaction_density': min(1.0, len(policies) * 0.15)
            }
    
    return temporal_analysis


def identify_direct_dependencies(policies: List[Policy]) -> List[Dict[str, Any]]:
    """Identify direct dependencies between policies."""
    dependencies = []
    
    # Look for policies that reference or build upon others
    for policy in policies:
        if policy.description:
            for other_policy in policies:
                if (other_policy.id != policy.id and 
                    other_policy.name.lower() in policy.description.lower()):
                    
                    dependencies.append({
                        'dependent_policy': policy.id,
                        'dependency': other_policy.id,
                        'dependency_type': 'direct_reference',
                        'strength': 0.8
                    })
    
    return dependencies


def identify_indirect_influences(policies: List[Policy]) -> List[Dict[str, Any]]:
    """Identify indirect influences between policies."""
    influences = []
    
    # Group by implementing agency and look for potential influences
    agency_groups = {}
    for policy in policies:
        if policy.implementing_agency:
            agency = policy.implementing_agency
            if agency not in agency_groups:
                agency_groups[agency] = []
            agency_groups[agency].append(policy)
    
    # Policies from same agency may influence each other
    for agency, agency_policies in agency_groups.items():
        if len(agency_policies) > 1:
            for i, policy1 in enumerate(agency_policies):
                for policy2 in agency_policies[i+1:]:
                    influences.append({
                        'influencer': policy1.id,
                        'influenced': policy2.id,
                        'influence_type': 'institutional',
                        'strength': 0.4,
                        'mechanism': f'Same implementing agency: {agency}'
                    })
    
    return influences


def identify_policy_networks(policies: List[Policy], interaction_matrix: Dict) -> Dict[str, Any]:
    """Identify policy networks and clusters."""
    # Simplified network analysis
    networks = {
        'clusters': [],
        'central_policies': [],
        'isolated_policies': []
    }
    
    # Find highly connected policies (central policies)
    for policy_id, connections in interaction_matrix.items():
        avg_connection_strength = np.mean(list(connections.values()))
        
        if avg_connection_strength > 0.6:
            networks['central_policies'].append({
                'policy_id': policy_id,
                'centrality_score': avg_connection_strength
            })
        elif avg_connection_strength < 0.2:
            networks['isolated_policies'].append(policy_id)
    
    return networks


def analyze_category_context_factors(category: str, implementation_year: int) -> Dict[str, Any]:
    """Analyze category-specific contextual factors."""
    # Historical context mapping for different categories
    context_factors = {
        'Phát triển đô thị': {
            'key_periods': {
                1960: 'Post-independence urban planning',
                1980: 'Economic development phase',
                2000: 'Smart city initiatives',
                2020: 'Sustainable development focus'
            }
        },
        'An sinh xã hội': {
            'key_periods': {
                1950: 'Post-war social reconstruction',
                1970: 'Economic miracle social policies',
                1990: 'Aging society preparation',
                2010: 'Digital transformation of services'
            }
        },
        'Giáo dục': {
            'key_periods': {
                1960: 'Education system establishment',
                1980: 'Technical education emphasis',
                2000: 'Knowledge economy transition',
                2020: 'Digital learning revolution'
            }
        }
        # Add more categories as needed
    }
    
    category_context = context_factors.get(category, {'key_periods': {}})
    
    # Find the most relevant historical period
    relevant_period = None
    for year, context in category_context['key_periods'].items():
        if implementation_year >= year:
            relevant_period = {'year': year, 'context': context}
    
    return {
        'category': category,
        'implementation_context': relevant_period,
        'historical_relevance': len([y for y in category_context['key_periods'].keys() 
                                   if abs(y - implementation_year) <= 10])
    }


def calculate_timing_score(policy: Policy) -> float:
    """Calculate how well-timed a policy implementation was."""
    # This is a simplified scoring - could be enhanced with historical data
    current_year = datetime.now().year
    policy_age = current_year - policy.implementation_year
    
    # Score based on policy lifecycle and continued relevance
    if policy_age < 5:
        return 0.9  # Recent policies generally well-timed
    elif policy_age < 20:
        return 0.8  # Mature policies
    elif policy_age < 40:
        return 0.7  # Established policies
    else:
        # Legacy policies - score based on continued assessment activity
        if policy.assessments and len(policy.assessments) > 0:
            latest_assessment = policy.get_latest_assessment()
            if latest_assessment and (current_year - latest_assessment.assessment_date.year) < 5:
                return 0.8  # Still being assessed = still relevant
        return 0.5  # Old policies without recent assessment


def calculate_sustained_relevance(assessments: List[PolicyAssessment]) -> float:
    """Calculate how well a policy maintains relevance over time."""
    if len(assessments) < 2:
        return 0.5
    
    # Look at trend in cross-referencing scores (external validation)
    cross_ref_scores = [a.criteria.cross_referencing for a in assessments]
    
    # Calculate trend
    x = np.arange(len(cross_ref_scores))
    correlation = np.corrcoef(x, cross_ref_scores)[0, 1] if len(cross_ref_scores) > 1 else 0
    
    # Sustained relevance is high if cross-referencing remains strong or improves
    avg_cross_ref = np.mean(cross_ref_scores)
    trend_factor = max(0, correlation)  # Positive correlation indicates improving relevance
    
    return min(1.0, (avg_cross_ref / 5.0) * 0.7 + trend_factor * 0.3)
