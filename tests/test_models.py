"""
Unit tests for the models module.

This module contains comprehensive unit tests for all data models
in the Policy Impact Assessment Framework.
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models import (
    PolicyCategory, AssessmentCriteria, WeightingConfig,
    PolicyAssessment, Policy, PolicyCollection
)


class TestPolicyCategory:
    """Test cases for PolicyCategory enum."""
    
    def test_category_values(self):
        """Test that all category values are correct."""
        assert PolicyCategory.SOCIAL_WELFARE.value == "An sinh xã hội"
        assert PolicyCategory.URBAN_ORDER.value == "Giữ gìn trật tự đô thị"
        assert PolicyCategory.ECONOMIC_FINANCIAL.value == "Kinh tế tài chính"
        assert PolicyCategory.EDUCATION.value == "Giáo dục"
        assert PolicyCategory.HEALTHCARE.value == "Chăm sóc sức khỏe"
    
    def test_category_membership(self):
        """Test category membership."""
        assert PolicyCategory.SOCIAL_WELFARE in PolicyCategory
        assert "Invalid Category" not in [cat.value for cat in PolicyCategory]


class TestAssessmentCriteria:
    """Test cases for AssessmentCriteria class."""
    
    def test_valid_criteria_creation(self):
        """Test creating valid assessment criteria."""
        criteria = AssessmentCriteria(
            scope=4, magnitude=3, durability=5, 
            adaptability=4, cross_referencing=3
        )
        assert criteria.scope == 4
        assert criteria.magnitude == 3
        assert criteria.durability == 5
        assert criteria.adaptability == 4
        assert criteria.cross_referencing == 3
    
    def test_invalid_criteria_validation(self):
        """Test validation of invalid criteria scores."""
        with pytest.raises(ValueError, match="scope must be an integer between 1 and 5"):
            AssessmentCriteria(scope=0)
        
        with pytest.raises(ValueError, match="magnitude must be an integer between 1 and 5"):
            AssessmentCriteria(magnitude=6)
        
        with pytest.raises(ValueError, match="durability must be an integer between 1 and 5"):
            AssessmentCriteria(durability=-1)
    
    def test_criteria_to_dict(self):
        """Test converting criteria to dictionary."""
        criteria = AssessmentCriteria(
            scope=4, magnitude=3, durability=5, 
            adaptability=4, cross_referencing=3
        )
        expected = {
            'scope': 4,
            'magnitude': 3,
            'durability': 5,
            'adaptability': 4,
            'cross_referencing': 3
        }
        assert criteria.to_dict() == expected
    
    def test_average_score(self):
        """Test calculating average score."""
        criteria = AssessmentCriteria(
            scope=4, magnitude=3, durability=5, 
            adaptability=4, cross_referencing=3
        )
        expected_avg = (4 + 3 + 5 + 4 + 3) / 5
        assert criteria.average_score() == expected_avg


class TestWeightingConfig:
    """Test cases for WeightingConfig class."""
    
    def test_default_weights(self):
        """Test default weight configuration."""
        config = WeightingConfig()
        assert config.scope == 1.0
        assert config.magnitude == 1.5
        assert config.durability == 2.0
        assert config.adaptability == 1.5
        assert config.cross_referencing == 1.0
    
    def test_custom_weights(self):
        """Test custom weight configuration."""
        config = WeightingConfig(
            scope=2.0, magnitude=1.0, durability=3.0,
            adaptability=1.5, cross_referencing=0.5
        )
        assert config.scope == 2.0
        assert config.magnitude == 1.0
        assert config.durability == 3.0
        assert config.adaptability == 1.5
        assert config.cross_referencing == 0.5
    
    def test_total_weight_calculation(self):
        """Test total weight calculation."""
        config = WeightingConfig()
        expected_total = 1.0 + 1.5 + 2.0 + 1.5 + 1.0
        assert config.total_weight == expected_total


class TestPolicyAssessment:
    """Test cases for PolicyAssessment class."""
    
    def test_assessment_creation(self):
        """Test creating a policy assessment."""
        criteria = AssessmentCriteria(
            scope=4, magnitude=3, durability=5, 
            adaptability=4, cross_referencing=3
        )
        config = WeightingConfig()
        
        assessment = PolicyAssessment(
            policy_id="SGP_2023_001",
            assessment_date=datetime.now(),
            criteria=criteria,
            weighted_config=config
        )
        
        assert assessment.policy_id == "SGP_2023_001"
        assert assessment.criteria == criteria
        assert assessment.weighted_config == config
        assert assessment.overall_score > 0
    
    def test_overall_score_calculation(self):
        """Test overall score calculation."""
        criteria = AssessmentCriteria(
            scope=4, magnitude=3, durability=5, 
            adaptability=4, cross_referencing=3
        )
        config = WeightingConfig()
        
        assessment = PolicyAssessment(
            policy_id="SGP_2023_001",
            assessment_date=datetime.now(),
            criteria=criteria,
            weighted_config=config
        )
        
        # Manual calculation
        expected_score = (
            4 * 1.0 +    # scope
            3 * 1.5 +    # magnitude
            5 * 2.0 +    # durability
            4 * 1.5 +    # adaptability
            3 * 1.0      # cross_referencing
        ) / config.total_weight
        
        assert abs(assessment.overall_score - expected_score) < 0.001


class TestPolicy:
    """Test cases for Policy class."""
    
    def test_policy_creation(self):
        """Test creating a policy."""
        policy = Policy(
            id="SGP_2023_001",
            name="Test Policy",
            category=PolicyCategory.SOCIAL_WELFARE,
            implementation_year=2023,
            description="Test policy description"
        )
        
        assert policy.id == "SGP_2023_001"
        assert policy.name == "Test Policy"
        assert policy.category == PolicyCategory.SOCIAL_WELFARE
        assert policy.implementation_year == 2023
        assert policy.description == "Test policy description"
    
    def test_policy_with_string_category(self):
        """Test creating policy with string category."""
        policy = Policy(
            id="SGP_2023_001",
            name="Test Policy",
            category="An sinh xã hội",
            implementation_year=2023
        )
        
        assert policy.category == PolicyCategory.SOCIAL_WELFARE
    
    def test_years_since_implementation(self):
        """Test years since implementation calculation."""
        current_year = datetime.now().year
        policy = Policy(
            id="SGP_2020_001",
            name="Test Policy",
            category=PolicyCategory.SOCIAL_WELFARE,
            implementation_year=2020
        )
        
        expected_years = current_year - 2020
        assert policy.years_since_implementation == expected_years
    
    def test_add_assessment(self):
        """Test adding assessment to policy."""
        policy = Policy(
            id="SGP_2023_001",
            name="Test Policy",
            category=PolicyCategory.SOCIAL_WELFARE,
            implementation_year=2023
        )
        
        criteria = AssessmentCriteria(scope=4, magnitude=3, durability=5)
        assessment = PolicyAssessment(
            policy_id="SGP_2023_001",
            assessment_date=datetime.now(),
            criteria=criteria
        )
        
        policy.add_assessment(assessment)
        assert len(policy.assessments) == 1
        assert policy.assessments[0] == assessment
    
    def test_get_latest_assessment(self):
        """Test getting latest assessment."""
        policy = Policy(
            id="SGP_2023_001",
            name="Test Policy",
            category=PolicyCategory.SOCIAL_WELFARE,
            implementation_year=2023
        )
        
        # Add assessments with different dates
        criteria = AssessmentCriteria(scope=4, magnitude=3, durability=5)
        
        old_assessment = PolicyAssessment(
            policy_id="SGP_2023_001",
            assessment_date=datetime.now() - timedelta(days=30),
            criteria=criteria
        )
        
        new_assessment = PolicyAssessment(
            policy_id="SGP_2023_001",
            assessment_date=datetime.now(),
            criteria=criteria
        )
        
        policy.add_assessment(old_assessment)
        policy.add_assessment(new_assessment)
        
        latest = policy.get_latest_assessment()
        assert latest == new_assessment


class TestPolicyCollection:
    """Test cases for PolicyCollection class."""
    
    def test_empty_collection(self):
        """Test empty policy collection."""
        collection = PolicyCollection()
        assert collection.total_policies == 0
        assert len(collection.policies) == 0
    
    def test_add_policy(self):
        """Test adding policy to collection."""
        collection = PolicyCollection()
        policy = Policy(
            id="SGP_2023_001",
            name="Test Policy",
            category=PolicyCategory.SOCIAL_WELFARE,
            implementation_year=2023
        )
        
        collection.add_policy(policy)
        assert collection.total_policies == 1
        assert policy in collection.policies
    
    def test_get_policy_by_id(self):
        """Test getting policy by ID."""
        collection = PolicyCollection()
        policy = Policy(
            id="SGP_2023_001",
            name="Test Policy",
            category=PolicyCategory.SOCIAL_WELFARE,
            implementation_year=2023
        )
        
        collection.add_policy(policy)
        found_policy = collection.get_policy_by_id("SGP_2023_001")
        assert found_policy == policy
        
        not_found = collection.get_policy_by_id("INVALID_ID")
        assert not_found is None
    
    def test_get_policies_by_category(self):
        """Test getting policies by category."""
        collection = PolicyCollection()
        
        policy1 = Policy(
            id="SGP_2023_001",
            name="Social Policy",
            category=PolicyCategory.SOCIAL_WELFARE,
            implementation_year=2023
        )
        
        policy2 = Policy(
            id="SGP_2023_002",
            name="Education Policy",
            category=PolicyCategory.EDUCATION,
            implementation_year=2023
        )
        
        policy3 = Policy(
            id="SGP_2023_003",
            name="Another Social Policy",
            category=PolicyCategory.SOCIAL_WELFARE,
            implementation_year=2023
        )
        
        collection.add_policy(policy1)
        collection.add_policy(policy2)
        collection.add_policy(policy3)
        
        social_policies = collection.get_policies_by_category(PolicyCategory.SOCIAL_WELFARE)
        assert len(social_policies) == 2
        assert policy1 in social_policies
        assert policy3 in social_policies
        assert policy2 not in social_policies
    
    def test_categories_summary(self):
        """Test categories summary."""
        collection = PolicyCollection()
        
        # Add policies with different categories
        policies = [
            Policy(
                id=f"SGP_2023_{i:03d}",
                name=f"Policy {i}",
                category=PolicyCategory.SOCIAL_WELFARE,
                implementation_year=2023
            ) for i in range(1, 4)
        ]
        
        policies.extend([
            Policy(
                id="SGP_2023_004",
                name="Education Policy",
                category=PolicyCategory.EDUCATION,
                implementation_year=2023
            ),
            Policy(
                id="SGP_2023_005",
                name="Healthcare Policy",
                category=PolicyCategory.HEALTHCARE,
                implementation_year=2023
            )
        ])
        
        for policy in policies:
            collection.add_policy(policy)
        
        summary = collection.categories_summary
        assert summary["An sinh xã hội"] == 3
        assert summary["Giáo dục"] == 1
        assert summary["Chăm sóc sức khỏe"] == 1
