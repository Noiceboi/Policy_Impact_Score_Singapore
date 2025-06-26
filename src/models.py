"""
Data models for the Policy Impact Assessment Framework.

This module contains the core data structures for representing policies,
assessments, and related entities in the framework. All models follow
PEP 257 docstring conventions and include comprehensive type hints.

Classes:
    PolicyCategory: Enumeration of policy categories in Vietnamese terms
    AssessmentCriteria: Assessment criteria with validation
    WeightingConfig: Configuration for criterion weights
    PolicyAssessment: Assessment result for a policy
    Policy: Represents a government policy
    PolicyCollection: Collection of policies for analysis

Example:
    >>> from models import Policy, PolicyCategory, AssessmentCriteria
    >>> policy = Policy(
    ...     id="SGP_2023_001",
    ...     name="Central Provident Fund",
    ...     category=PolicyCategory.SOCIAL_WELFARE,
    ...     implementation_year=2023
    ... )
    >>> criteria = AssessmentCriteria(scope=4, magnitude=5, durability=5)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from enum import Enum
import logging

# Configure logging
logger = logging.getLogger(__name__)


class PolicyCategory(Enum):
    """
    Enumeration of policy categories in Vietnamese terms.
    
    This enum defines the standard policy categories used in the Singapore
    policy impact assessment framework. Each category represents a major
    area of government policy intervention.
    
    Attributes:
        SOCIAL_WELFARE: Social welfare and security policies
        URBAN_ORDER: Urban planning and order maintenance
        ECONOMIC_FINANCIAL: Economic and financial policies
        SOCIAL_WELLBEING: Social wellbeing and community policies
        TAXATION: Tax policies and revenue generation
        NATIONAL_SECURITY: National security and defense
        CULTURE_SOCIETY: Cultural and social development
        EDUCATION: Education and training policies
        URBAN_DEVELOPMENT: Urban development and infrastructure
        HEALTHCARE: Healthcare and public health policies
    """
    SOCIAL_WELFARE = "An sinh xã hội"
    URBAN_ORDER = "Giữ gìn trật tự đô thị"
    ECONOMIC_FINANCIAL = "Kinh tế tài chính"
    SOCIAL_WELLBEING = "Phúc lợi xã hội"
    TAXATION = "Thuế"
    NATIONAL_SECURITY = "An ninh quốc phòng"
    CULTURE_SOCIETY = "Văn hóa xã hội"
    EDUCATION = "Giáo dục"
    URBAN_DEVELOPMENT = "Phát triển đô thị"
    HEALTHCARE = "Chăm sóc sức khỏe"


@dataclass
class AssessmentCriteria:
    """
    Assessment criteria with scores and validation.
    
    This class represents the core assessment dimensions used to evaluate
    policy impact. Each criterion is scored on a 1-5 scale where:
    - 1: Very Low Impact
    - 2: Low Impact  
    - 3: Moderate Impact
    - 4: High Impact
    - 5: Very High Impact
    
    Attributes:
        scope (int): Geographic or demographic reach of the policy (1-5)
        magnitude (int): Intensity or strength of policy effects (1-5)
        durability (int): Long-term sustainability of policy impacts (1-5)
        adaptability (int): Policy flexibility and responsiveness (1-5)
        cross_referencing (int): Integration with other policies (1-5)
    
    Raises:
        ValueError: If any score is outside the valid range [1-5]
    
    Example:
        >>> criteria = AssessmentCriteria(
        ...     scope=4, magnitude=5, durability=4, 
        ...     adaptability=3, cross_referencing=4
        ... )
        >>> print(criteria.scope)
        4
    """
    scope: int = 1
    magnitude: int = 1
    durability: int = 1
    adaptability: int = 1
    cross_referencing: int = 1
    
    def __post_init__(self) -> None:
        """
        Validate that all scores are within the valid range.
        
        Raises:
            ValueError: If any criterion score is not between 1 and 5
        """
        for field_name, value in self.__dict__.items():
            if not isinstance(value, int) or not 1 <= value <= 5:
                raise ValueError(
                    f"{field_name} must be an integer between 1 and 5, got {value}"
                )
                
    def to_dict(self) -> Dict[str, int]:
        """
        Convert assessment criteria to dictionary.
        
        Returns:
            Dict[str, int]: Dictionary with criterion names as keys and scores as values
        """
        return {
            'scope': self.scope,
            'magnitude': self.magnitude,
            'durability': self.durability,
            'adaptability': self.adaptability,
            'cross_referencing': self.cross_referencing
        }
    
    def average_score(self) -> float:
        """
        Calculate the arithmetic mean of all criteria scores.
        
        Returns:
            float: Average score across all criteria
        """
        scores = list(self.to_dict().values())
        return sum(scores) / len(scores)


@dataclass
class WeightingConfig:
    """Configuration for criterion weights in impact calculation."""
    scope: float = 1.0
    magnitude: float = 1.5
    durability: float = 2.0  # Higher weight for long-term effects
    adaptability: float = 1.5
    cross_referencing: float = 1.0
    
    @property
    def total_weight(self) -> float:
        """Calculate total weight for normalization."""
        return (self.scope + self.magnitude + self.durability + 
                self.adaptability + self.cross_referencing)


@dataclass
class PolicyAssessment:
    """Assessment result for a policy at a specific point in time."""
    policy_id: str
    assessment_date: datetime
    criteria: AssessmentCriteria
    overall_score: float = field(init=False)
    weighted_config: WeightingConfig = field(default_factory=WeightingConfig)
    assessor: Optional[str] = None
    notes: Optional[str] = None
    data_sources: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Calculate overall score after initialization."""
        self.overall_score = self.calculate_overall_score()
    
    def calculate_overall_score(self) -> float:
        """
        Calculate weighted overall impact score.
        
        Returns:
            float: Weighted average score (0-5 scale)
        """
        weights = self.weighted_config
        criteria = self.criteria
        
        weighted_sum = (
            criteria.scope * weights.scope +
            criteria.magnitude * weights.magnitude +
            criteria.durability * weights.durability +
            criteria.adaptability * weights.adaptability +
            criteria.cross_referencing * weights.cross_referencing
        )
        
        return weighted_sum / weights.total_weight


@dataclass
class Policy:
    """
    Represents a government policy for impact assessment.
    
    Attributes:
        id: Unique identifier for the policy
        name: Policy name
        category: Policy category from PolicyCategory enum
        implementation_year: Year the policy was implemented
        description: Detailed description of the policy
        objectives: List of policy objectives
        target_population: Description of target population
        budget: Policy budget if available
        implementing_agency: Government agency responsible
        assessments: List of historical assessments
        metadata: Additional metadata
    """
    id: str
    name: str
    category: Union[PolicyCategory, str]
    implementation_year: int
    description: Optional[str] = None
    objectives: List[str] = field(default_factory=list)
    target_population: Optional[str] = None
    budget: Optional[float] = None
    implementing_agency: Optional[str] = None
    assessments: List[PolicyAssessment] = field(default_factory=list)
    metadata: Dict[str, Union[str, int, float]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Convert string category to PolicyCategory enum if needed."""
        if isinstance(self.category, str):
            # Try to find matching category by value
            for cat in PolicyCategory:
                if cat.value == self.category:
                    self.category = cat
                    break
            else:
                # If no match found, keep as string
                pass
    
    def add_assessment(self, assessment: PolicyAssessment) -> None:
        """Add a new assessment to this policy."""
        assessment.policy_id = self.id
        self.assessments.append(assessment)
        # Sort assessments by date
        self.assessments.sort(key=lambda x: x.assessment_date)
    
    def get_latest_assessment(self) -> Optional[PolicyAssessment]:
        """Get the most recent assessment for this policy."""
        if not self.assessments:
            return None
        return max(self.assessments, key=lambda x: x.assessment_date)
    
    def get_assessment_by_date(self, target_date: datetime) -> Optional[PolicyAssessment]:
        """Get assessment closest to the target date."""
        if not self.assessments:
            return None
        
        return min(self.assessments, 
                  key=lambda x: abs((x.assessment_date - target_date).days))
    
    @property
    def years_since_implementation(self) -> int:
        """Calculate years since policy implementation."""
        current_year = datetime.now().year
        return current_year - self.implementation_year
    
    @property
    def category_name(self) -> str:
        """Get category name as string."""
        if isinstance(self.category, PolicyCategory):
            return self.category.value
        return str(self.category)


@dataclass
class PolicyCollection:
    """Collection of policies for analysis."""
    policies: List[Policy] = field(default_factory=list)
    metadata: Dict[str, Union[str, int, float]] = field(default_factory=dict)
    
    def add_policy(self, policy: Policy) -> None:
        """Add a policy to the collection."""
        self.policies.append(policy)
    
    def get_policy_by_id(self, policy_id: str) -> Optional[Policy]:
        """Get policy by ID."""
        for policy in self.policies:
            if policy.id == policy_id:
                return policy
        return None
    
    def get_policies_by_category(self, category: Union[PolicyCategory, str]) -> List[Policy]:
        """Get all policies in a specific category."""
        if isinstance(category, str):
            return [p for p in self.policies if p.category_name == category]
        else:
            return [p for p in self.policies if p.category == category]
    
    def get_policies_by_year_range(self, start_year: int, end_year: int) -> List[Policy]:
        """Get policies implemented within a year range."""
        return [p for p in self.policies 
                if start_year <= p.implementation_year <= end_year]
    
    @property
    def total_policies(self) -> int:
        """Get total number of policies."""
        return len(self.policies)
    
    @property
    def categories_summary(self) -> Dict[str, int]:
        """Get summary of policies by category."""
        summary = {}
        for policy in self.policies:
            category = policy.category_name
            summary[category] = summary.get(category, 0) + 1
        return summary
