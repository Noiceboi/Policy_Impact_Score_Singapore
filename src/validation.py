"""
Data validation schemas for the Policy Impact Assessment Framework.

This module defines pandas DataFrame schemas using pandera for data validation,
ensuring data integrity and consistency throughout the analysis pipeline.
"""

import pandera as pa
from pandera import Column, DataFrameSchema, Check
from pandera.typing import DateTime, String, Float, Int
from typing import Optional
import pandas as pd


class PolicyDataSchema:
    """Schema definitions for policy data validation."""
    
    # Policy master data schema
    POLICY_SCHEMA = DataFrameSchema(
        {
            "id": Column(String, checks=[
                Check.str_matches(r'^[A-Z]{3}_\d{4}_\d{3}$'),  # Format: SGP_2023_001
                Check(lambda x: x.notna().all(), error="Policy ID cannot be null")
            ], nullable=False, unique=True),
            
            "name": Column(String, checks=[
                Check.str_length(min_value=5, max_value=200),
                Check(lambda x: x.str.strip().str.len() > 0, error="Policy name cannot be empty")
            ], nullable=False),
            
            "category": Column(String, checks=[
                Check.isin([
                    "An sinh xã hội", "Giữ gìn trật tự đô thị", "Kinh tế tài chính",
                    "Phúc lợi xã hội", "Thuế", "An ninh quốc phòng", "Văn hóa xã hội",
                    "Giáo dục", "Phát triển đô thị", "Chăm sóc sức khỏe"
                ])
            ], nullable=False),
            
            "implementation_year": Column(Int, checks=[
                Check.greater_than_or_equal_to(1965),  # Singapore independence
                Check.less_than_or_equal_to(2030),     # Future limit
            ], nullable=False),
            
            "description": Column(String, checks=[
                Check.str_length(min_value=10, max_value=2000)
            ], nullable=True),
            
            "implementing_agency": Column(String, nullable=True),
            "budget": Column(Float, checks=[Check.greater_than(0)], nullable=True),
            "target_population": Column(String, nullable=True),
            
            "created_at": Column(DateTime, nullable=False),
            "updated_at": Column(DateTime, nullable=False),
            "data_source": Column(String, nullable=False),
            "data_extraction_date": Column(DateTime, nullable=False),
        },
        checks=[
            Check(lambda df: df['updated_at'] >= df['created_at'], 
                  error="Updated date must be after created date"),
            Check(lambda df: df.groupby('name').size().max() == 1,
                  error="Policy names must be unique")
        ],
        strict=True,
        coerce=True
    )
    
    # Assessment data schema
    ASSESSMENT_SCHEMA = DataFrameSchema(
        {
            "assessment_id": Column(String, checks=[
                Check.str_matches(r'^ASS_\d{8}_\d{6}$')  # Format: ASS_20240101_123456
            ], nullable=False, unique=True),
            
            "policy_id": Column(String, checks=[
                Check.str_matches(r'^[A-Z]{3}_\d{4}_\d{3}$')
            ], nullable=False),
            
            "assessment_date": Column(DateTime, nullable=False),
            
            "scope": Column(Int, checks=[
                Check.greater_than_or_equal_to(1),
                Check.less_than_or_equal_to(5)
            ], nullable=False),
            
            "magnitude": Column(Int, checks=[
                Check.greater_than_or_equal_to(1),
                Check.less_than_or_equal_to(5)
            ], nullable=False),
            
            "durability": Column(Int, checks=[
                Check.greater_than_or_equal_to(1),
                Check.less_than_or_equal_to(5)
            ], nullable=False),
            
            "adaptability": Column(Int, checks=[
                Check.greater_than_or_equal_to(1),
                Check.less_than_or_equal_to(5)
            ], nullable=False),
            
            "cross_referencing": Column(Int, checks=[
                Check.greater_than_or_equal_to(1),
                Check.less_than_or_equal_to(5)
            ], nullable=False),
            
            "overall_score": Column(Float, checks=[
                Check.greater_than_or_equal_to(1.0),
                Check.less_than_or_equal_to(5.0)
            ], nullable=False),
            
            "assessor": Column(String, nullable=True),
            "assessment_method": Column(String, checks=[
                Check.isin(["manual", "automated", "hybrid"])
            ], nullable=False),
            
            "confidence_level": Column(Float, checks=[
                Check.greater_than_or_equal_to(0.0),
                Check.less_than_or_equal_to(1.0)
            ], nullable=True),
            
            "data_sources": Column(String, nullable=True),  # JSON string
            "notes": Column(String, nullable=True),
            
            "created_at": Column(DateTime, nullable=False),
            "validation_status": Column(String, checks=[
                Check.isin(["pending", "validated", "rejected", "under_review"])
            ], nullable=False),
        },
        checks=[
            Check(lambda df: df['assessment_date'] <= df['created_at'],
                  error="Assessment date cannot be in the future relative to creation")
        ],
        strict=True,
        coerce=True
    )
    
    # International validation data schema
    INTERNATIONAL_VALIDATION_SCHEMA = DataFrameSchema(
        {
            "validation_id": Column(String, unique=True, nullable=False),
            "policy_id": Column(String, nullable=False),
            "organization": Column(String, checks=[
                Check.isin(["World Bank", "OECD", "IMF", "UN-HABITAT", 
                           "Asian Development Bank", "WHO", "UNESCO"])
            ], nullable=False),
            "score": Column(Float, checks=[
                Check.greater_than_or_equal_to(1.0),
                Check.less_than_or_equal_to(5.0)
            ], nullable=False),
            "methodology": Column(String, nullable=True),
            "report_url": Column(String, nullable=True),
            "validation_date": Column(DateTime, nullable=False),
            "confidence": Column(Float, checks=[
                Check.greater_than_or_equal_to(0.0),
                Check.less_than_or_equal_to(1.0)
            ], nullable=True),
        },
        strict=True,
        coerce=True
    )


class DataValidator:
    """Data validation utilities for the framework."""
    
    def __init__(self):
        self.schemas = PolicyDataSchema()
    
    def validate_policy_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate policy data against schema.
        
        Args:
            df: DataFrame containing policy data
            
        Returns:
            Validated DataFrame
            
        Raises:
            pa.errors.SchemaError: If validation fails
        """
        try:
            return self.schemas.POLICY_SCHEMA.validate(df)
        except pa.errors.SchemaError as e:
            raise ValueError(f"Policy data validation failed: {e}")
    
    def validate_assessment_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate assessment data against schema.
        
        Args:
            df: DataFrame containing assessment data
            
        Returns:
            Validated DataFrame
            
        Raises:
            pa.errors.SchemaError: If validation fails
        """
        try:
            return self.schemas.ASSESSMENT_SCHEMA.validate(df)
        except pa.errors.SchemaError as e:
            raise ValueError(f"Assessment data validation failed: {e}")
    
    def validate_international_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate international validation data against schema.
        
        Args:
            df: DataFrame containing international validation data
            
        Returns:
            Validated DataFrame
            
        Raises:
            pa.errors.SchemaError: If validation fails
        """
        try:
            return self.schemas.INTERNATIONAL_VALIDATION_SCHEMA.validate(df)
        except pa.errors.SchemaError as e:
            raise ValueError(f"International validation data validation failed: {e}")
    
    def generate_data_quality_report(self, df: pd.DataFrame, schema_type: str) -> dict:
        """
        Generate a data quality report for the given DataFrame.
        
        Args:
            df: DataFrame to analyze
            schema_type: Type of schema to validate against
            
        Returns:
            Dictionary containing quality metrics
        """
        report = {
            "timestamp": pd.Timestamp.now(),
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "missing_values": df.isnull().sum().to_dict(),
            "duplicate_rows": df.duplicated().sum(),
            "data_types": df.dtypes.to_dict(),
        }
        
        # Add schema-specific validation
        try:
            if schema_type == "policy":
                self.validate_policy_data(df)
                report["validation_status"] = "PASSED"
            elif schema_type == "assessment":
                self.validate_assessment_data(df)
                report["validation_status"] = "PASSED"
            elif schema_type == "international":
                self.validate_international_data(df)
                report["validation_status"] = "PASSED"
            else:
                report["validation_status"] = "UNKNOWN_SCHEMA"
        except Exception as e:
            report["validation_status"] = "FAILED"
            report["validation_errors"] = str(e)
        
        return report


# Example usage and testing functions
def validate_sample_data():
    """Validate sample data files if they exist."""
    import os
    
    validator = DataValidator()
    
    # Check if sample files exist
    policy_file = "data/sample_policies.csv"
    assessment_file = "data/sample_assessments.csv"
    
    if os.path.exists(policy_file):
        try:
            df = pd.read_csv(policy_file)
            validated_df = validator.validate_policy_data(df)
            print(f"✓ Policy data validation passed: {len(validated_df)} records")
        except Exception as e:
            print(f"✗ Policy data validation failed: {e}")
    
    if os.path.exists(assessment_file):
        try:
            df = pd.read_csv(assessment_file)
            validated_df = validator.validate_assessment_data(df)
            print(f"✓ Assessment data validation passed: {len(validated_df)} records")
        except Exception as e:
            print(f"✗ Assessment data validation failed: {e}")


if __name__ == "__main__":
    validate_sample_data()
