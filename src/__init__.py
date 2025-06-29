"""
Policy Impact Assessment Framework for Singapore.

A comprehensive framework for evaluating the impact of Singaporean government policies
across multiple dimensions with advanced MCDA methods and statistical validation.
"""

__version__ = "2.0.0"
__author__ = "Policy Impact Assessment Team"
__email__ = "policy-assessment@example.com"

from .models import Policy, PolicyAssessment, PolicyCollection
from .framework import PolicyAssessmentFramework
from .mcda import AHPProcessor, ELECTREProcessor, SensitivityAnalyzer, AdvancedMCDAFramework
from .validation import DataValidator

__all__ = [
    "Policy",
    "PolicyAssessment", 
    "PolicyCollection",
    "PolicyAssessmentFramework",
    "AHPProcessor",
    "ELECTREProcessor",
    "SensitivityAnalyzer",
    "AdvancedMCDAFramework",
    "DataValidator",
]
