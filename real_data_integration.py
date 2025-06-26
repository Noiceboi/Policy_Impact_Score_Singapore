"""
Real Data Integration Script for Singapore Policy Impact Assessment

This script loads actual Singapore government policy data and integrates it
with the Policy Impact Assessment Framework for accurate analysis.
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append('src')

from src.framework import PolicyAssessmentFramework
from src.models import Policy, AssessmentCriteria, PolicyAssessment, PolicyCategory
from src.utils import setup_logging, validate_data_consistency


class RealDataIntegrator:
    """
    Class to handle integration of real Singapore policy data.
    """
    
    def __init__(self):
        """Initialize the data integrator."""
        self.logger = setup_logging("INFO")
        self.framework = PolicyAssessmentFramework()
        
    def load_singapore_policies(self, policies_file: str, assessments_file: str):
        """
        Load comprehensive Singapore policy data.
        
        Args:
            policies_file: Path to Singapore policies CSV
            assessments_file: Path to assessments CSV
        """
        self.logger.info("🏛️  Loading Real Singapore Policy Data...")
        
        # Load policies with enhanced data
        df_policies = pd.read_csv(policies_file)
        
        for _, row in df_policies.iterrows():
            # Parse objectives
            objectives = [obj.strip() for obj in str(row['policy_objectives']).split(';')] if pd.notna(row['policy_objectives']) else []
            
            policy = Policy(
                id=row['policy_id'],
                name=row['policy_name'],
                category=row['category'],
                implementation_year=pd.to_datetime(row['implementation_date']).year,
                description=f"Background: {row.get('background_crisis', 'N/A')}. Legal Framework: {row.get('legal_framework', 'N/A')}",
                implementing_agency=row['implementing_agency'],
                budget=row['budget_allocated_sgd'] if pd.notna(row['budget_allocated_sgd']) else None,
                objectives=objectives,
                target_population=row.get('target_population'),
                metadata={
                    'implementation_date': row['implementation_date'],
                    'urgency_level': row.get('urgency_level', 0),
                    'background_crisis': row.get('background_crisis'),
                    'legal_framework': row.get('legal_framework'),
                    'economic_context_gdp_growth': row.get('economic_context_gdp_growth'),
                    'social_context_population': row.get('social_context_population'),
                    'political_context': row.get('political_context')
                }
            )
            
            self.framework.add_policy(policy)
            
        self.logger.info(f"✅ Loaded {len(df_policies)} Singapore policies")
        
        # Load detailed assessments
        df_assessments = pd.read_csv(assessments_file)
        
        assessment_count = 0
        for _, row in df_assessments.iterrows():
            policy = self.framework.policies.get_policy_by_id(row['policy_id'])
            if not policy:
                continue
                
            criteria = AssessmentCriteria(
                scope=int(row['scope']),
                magnitude=int(row['magnitude']),
                durability=int(row['durability']),
                adaptability=int(row['adaptability']),
                cross_referencing=int(row['cross_referencing'])
            )
            
            # Parse data sources
            data_sources = [source.strip() for source in str(row['data_sources']).split(';')] if pd.notna(row['data_sources']) else []
            
            assessment = PolicyAssessment(
                policy_id=policy.id,
                assessment_date=pd.to_datetime(row['assessment_date']),
                criteria=criteria,
                assessor=row['assessor_organization'],
                notes=row.get('notes'),
                data_sources=data_sources
            )
            
            # Add enhanced metadata
            assessment.metadata = {
                'methodology_used': row.get('methodology_used'),
                'confidence_level': row.get('confidence_level', 0),
                'beneficiaries_count': row.get('beneficiaries_count'),
                'budget_utilization_percent': row.get('budget_utilization_percent'),
                'public_satisfaction_score': row.get('public_satisfaction_score'),
                'media_coverage_sentiment': row.get('media_coverage_sentiment'),
                'amendments_count': row.get('amendments_count'),
                'gdp_contribution_percent': row.get('gdp_contribution_percent'),
                'employment_impact': row.get('employment_impact'),
                'cost_benefit_ratio': row.get('cost_benefit_ratio')
            }
            
            policy.add_assessment(assessment)
            assessment_count += 1
            
        self.logger.info(f"✅ Loaded {assessment_count} detailed assessments")
        
    def validate_data_quality(self):
        """Validate the quality and consistency of loaded data."""
        self.logger.info("🔍 Validating data quality...")
        
        validation_results = validate_data_consistency(self.framework.policies.policies)
        
        if validation_results['validation_passed']:
            self.logger.info("✅ Data validation passed")
        else:
            self.logger.warning(f"⚠️  Found {len(validation_results['errors'])} errors")
            for error in validation_results['errors']:
                self.logger.error(f"   • {error}")
                
        if validation_results['warnings']:
            self.logger.info(f"📝 Found {len(validation_results['warnings'])} warnings")
            for warning in validation_results['warnings']:
                self.logger.warning(f"   • {warning}")
        
        return validation_results
    
    def generate_enhanced_analysis(self):
        """Generate comprehensive analysis with real data."""
        self.logger.info("📊 Generating enhanced analysis with real data...")
        
        # Basic summary
        summary = self.framework.generate_summary_report()
        
        print("\n🏛️  SINGAPORE POLICY IMPACT ANALYSIS")
        print("=" * 60)
        print(f"Total Policies Analyzed: {summary['total_policies']}")
        print(f"Assessment Coverage: {summary['assessment_coverage']:.1f}%")
        
        print(f"\n🏆 TOP 5 HIGHEST IMPACT POLICIES:")
        for i, (name, score) in enumerate(summary['top_policies'][:5], 1):
            print(f"  {i}. {name}: {score:.2f}")
        
        print(f"\n📊 CATEGORY PERFORMANCE ANALYSIS:")
        for category, data in summary['category_scores'].items():
            print(f"  • {category}")
            print(f"    Average Score: {data['average_score']:.2f}")
            print(f"    Policies: {data['policy_count']} ({data['assessed_policies']} assessed)")
        
        # Enhanced analysis for key policies
        print(f"\n🔍 DETAILED POLICY EVOLUTION ANALYSIS:")
        
        # Analyze HDB (longest running policy)
        try:
            hdb_evolution = self.framework.analyze_policy_evolution('HDB-1960-001')
            print(f"\n📈 Housing Development Act Evolution:")
            print(f"  • Active for: {hdb_evolution['assessment_period']['duration_years']:.1f} years")
            print(f"  • Overall trend: {hdb_evolution['summary']['overall_trend']}")
            print(f"  • Strongest improvement: {hdb_evolution['summary']['strongest_improvement']}")
            print(f"  • Assessment count: {hdb_evolution['summary']['total_assessments']}")
        except Exception as e:
            self.logger.warning(f"Could not analyze HDB evolution: {e}")
        
        # Policy comparison by era
        print(f"\n🕐 POLICY PERFORMANCE BY ERA:")
        
        policies_by_decade = {}
        for policy in self.framework.policies.policies:
            decade = (policy.implementation_year // 10) * 10
            if decade not in policies_by_decade:
                policies_by_decade[decade] = []
            policies_by_decade[decade].append(policy)
        
        for decade in sorted(policies_by_decade.keys()):
            policies = policies_by_decade[decade]
            scores = []
            for policy in policies:
                latest = policy.get_latest_assessment()
                if latest:
                    scores.append(latest.overall_score)
            
            if scores:
                avg_score = sum(scores) / len(scores)
                print(f"  • {decade}s: {len(policies)} policies, Average Score: {avg_score:.2f}")
        
        # Economic impact analysis
        print(f"\n💰 ECONOMIC IMPACT ANALYSIS:")
        total_budget = 0
        policies_with_budget = 0
        
        for policy in self.framework.policies.policies:
            if policy.budget:
                total_budget += policy.budget
                policies_with_budget += 1
        
        if policies_with_budget > 0:
            print(f"  • Total Budget Tracked: SGD ${total_budget:,.0f}")
            print(f"  • Average Budget per Policy: SGD ${total_budget/policies_with_budget:,.0f}")
            print(f"  • Policies with Budget Data: {policies_with_budget}/{summary['total_policies']}")
        
        return summary
    
    def export_analysis_results(self, output_dir: str = "output/real_data_analysis"):
        """Export comprehensive analysis results."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"💾 Exporting analysis results to {output_path}...")
        
        # Export enhanced data
        self.framework.export_data(str(output_path))
        
        # Create enhanced reports
        summary = self.framework.generate_summary_report()
        
        # Policy timeline analysis
        timeline_data = []
        for policy in self.framework.policies.policies:
            latest = policy.get_latest_assessment()
            timeline_data.append({
                'policy_name': policy.name,
                'implementation_year': policy.implementation_year,
                'years_active': policy.years_since_implementation,
                'category': policy.category_name,
                'budget': policy.budget or 0,
                'latest_score': latest.overall_score if latest else None,
                'assessment_count': len(policy.assessments),
                'urgency_level': policy.metadata.get('urgency_level', 0),
                'gdp_context': policy.metadata.get('economic_context_gdp_growth', 0)
            })
        
        timeline_df = pd.DataFrame(timeline_data)
        timeline_df.to_csv(output_path / "policy_timeline_analysis.csv", index=False)
        
        self.logger.info("✅ Analysis results exported successfully")
        
        return str(output_path)


def main():
    """Main function to run real data integration."""
    print("🇸🇬 Singapore Policy Impact Assessment - Real Data Integration")
    print("=" * 70)
    
    integrator = RealDataIntegrator()
    
    # Load real Singapore data
    integrator.load_singapore_policies(
        'templates/singapore_policies_template.csv',
        'templates/singapore_assessments_template.csv'
    )
    
    # Validate data quality
    validation_results = integrator.validate_data_quality()
    
    # Generate comprehensive analysis
    summary = integrator.generate_enhanced_analysis()
    
    # Export results
    output_path = integrator.export_analysis_results()
    
    print(f"\n✨ REAL DATA INTEGRATION COMPLETED!")
    print(f"📁 Results exported to: {output_path}")
    print(f"🎯 Ready for production policy analysis!")
    
    # Show next steps
    print(f"\n📋 NEXT STEPS FOR ACCURATE MODEL FEEDING:")
    print("1. Review exported analysis in output directory")
    print("2. Add more historical assessment points for better trends")
    print("3. Include stakeholder feedback data")
    print("4. Connect to real-time government data APIs")
    print("5. Implement predictive modeling for future impact")


if __name__ == "__main__":
    main()
