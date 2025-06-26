"""Test configuration and fixtures for the Policy Impact Assessment Framework."""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import os
import sys

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models import (
    Policy, PolicyAssessment, AssessmentCriteria, WeightingConfig,
    PolicyCategory, PolicyCollection
)


@pytest.fixture
def sample_assessment_criteria():
    """Create sample assessment criteria for testing."""
    return AssessmentCriteria(
        scope=4,
        magnitude=3,
        durability=5,
        adaptability=4,
        cross_referencing=3
    )


@pytest.fixture
def sample_weighting_config():
    """Create sample weighting configuration for testing."""
    return WeightingConfig(
        scope=1.0,
        magnitude=1.5,
        durability=2.0,
        adaptability=1.5,
        cross_referencing=1.0
    )


@pytest.fixture
def sample_policy():
    """Create a sample policy for testing."""
    return Policy(
        id="SGP_2023_001",
        name="Central Provident Fund Enhancement",
        category=PolicyCategory.SOCIAL_WELFARE,
        implementation_year=2023,
        description="Enhancement of CPF retirement savings scheme",
        objectives=["Increase retirement savings", "Improve financial security"],
        target_population="All Singapore citizens and permanent residents",
        budget=1000000000.0,
        implementing_agency="Central Provident Fund Board"
    )


@pytest.fixture
def sample_policy_assessment(sample_assessment_criteria, sample_weighting_config):
    """Create a sample policy assessment for testing."""
    return PolicyAssessment(
        policy_id="SGP_2023_001",
        assessment_date=datetime.now(),
        criteria=sample_assessment_criteria,
        weighted_config=sample_weighting_config,
        assessor="Test Assessor",
        notes="Sample assessment for testing",
        data_sources=["Official government reports", "Statistical data"]
    )


@pytest.fixture
def sample_policy_collection(sample_policy):
    """Create a sample policy collection for testing."""
    collection = PolicyCollection()
    collection.add_policy(sample_policy)
    return collection


@pytest.fixture
def sample_policies_dataframe():
    """Create a sample DataFrame of policies for testing."""
    return pd.DataFrame({
        'id': ['SGP_2023_001', 'SGP_2023_002', 'SGP_2023_003'],
        'name': ['CPF Enhancement', 'Housing Policy', 'Education Reform'],
        'category': ['An sinh xã hội', 'Giữ gìn trật tự đô thị', 'Giáo dục'],
        'implementation_year': [2023, 2022, 2024],
        'description': ['CPF enhancement', 'Housing development', 'Education reform'],
        'implementing_agency': ['CPF Board', 'HDB', 'MOE'],
        'budget': [1000000000.0, 500000000.0, 750000000.0],
        'target_population': ['All citizens', 'Homebuyers', 'Students'],
        'created_at': [datetime.now()] * 3,
        'updated_at': [datetime.now()] * 3,
        'data_source': ['government portal'] * 3,
        'data_extraction_date': [datetime.now()] * 3
    })


@pytest.fixture
def sample_assessments_dataframe():
    """Create a sample DataFrame of assessments for testing."""
    return pd.DataFrame({
        'assessment_id': ['ASS_20240101_120000', 'ASS_20240101_120001', 'ASS_20240101_120002'],
        'policy_id': ['SGP_2023_001', 'SGP_2023_002', 'SGP_2023_003'],
        'assessment_date': [datetime.now()] * 3,
        'scope': [4, 3, 5],
        'magnitude': [3, 4, 3],
        'durability': [5, 4, 4],
        'adaptability': [4, 3, 5],
        'cross_referencing': [3, 4, 4],
        'overall_score': [3.8, 3.6, 4.2],
        'assessor': ['Test Assessor'] * 3,
        'assessment_method': ['manual'] * 3,
        'confidence_level': [0.8, 0.7, 0.9],
        'data_sources': ['["source1", "source2"]'] * 3,
        'notes': ['Test notes'] * 3,
        'created_at': [datetime.now()] * 3,
        'validation_status': ['validated'] * 3
    })


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing file operations."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_data_files(temp_directory, sample_policies_dataframe, sample_assessments_dataframe):
    """Create mock data files for testing."""
    policies_file = temp_directory / "policies.csv"
    assessments_file = temp_directory / "assessments.csv"
    
    sample_policies_dataframe.to_csv(policies_file, index=False)
    sample_assessments_dataframe.to_csv(assessments_file, index=False)
    
    return {
        'policies': policies_file,
        'assessments': assessments_file
    }


# Test markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "external: mark test as requiring external dependencies"
    )
