"""
Data models for the Policy Impact Assessment Framework.

This module contains the core data structures for representing policies,
assessments, and related entities in the framework.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Union
from enum import Enum


class PolicyCategory(Enum):
    """Enumeration of policy categories in Vietnamese terms."""
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
    """Assessment criteria with scores and descriptions."""
    scope: int = 0  # 0-5 scale
    magnitude: int = 0  # 0-5 scale
    durability: int = 0  # 0-5 scale
    adaptability: int = 0  # 0-5 scale
    cross_referencing: int = 0  # 0-5 scale
    
    def __post_init__(self):
        """Validate that all scores are within the valid range."""
        for field_name, value in self.__dict__.items():
            if not 0 <= value <= 5:
                raise ValueError(f"{field_name} must be between 0 and 5, got {value}")


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
