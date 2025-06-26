"""
Main entry point for the Policy Impact Assessment Framework.

This script demonstrates the key features of the framework including
policy creation, assessment, analysis, and visualization.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.framework import PolicyAssessmentFramework
from src.models import Policy, AssessmentCriteria, PolicyAssessment
from src.utils import create_sample_data, setup_logging


def main():
    """Main demonstration of the Policy Impact Assessment Framework."""
    
    # Setup logging
    logger = setup_logging("INFO")
    logger.info("Starting Policy Impact Assessment Framework Demo")
    
    print("🏛️  Policy Impact Assessment Framework for Singapore")
    print("=" * 60)
    
    # Initialize framework
    framework = PolicyAssessmentFramework()
    
    # Create sample data
    print("\n📊 Loading sample policy data...")
    sample_policies = create_sample_data()
    
    for policy in sample_policies:
        framework.add_policy(policy)
    
    print(f"✅ Loaded {len(sample_policies)} sample policies")
    
    # Display policy summary
    print("\n📋 Policy Summary:")
    summary = framework.generate_summary_report()
    
    print(f"Total Policies: {summary['total_policies']}")
    print(f"Assessment Coverage: {summary['assessment_coverage']:.1f}%")
    
    print("\nPolicies by Category:")
    for category, count in summary['categories_summary'].items():
        print(f"  • {category}: {count} policies")
    
    print("\nCategory Performance:")
    for category, data in summary['category_scores'].items():
        print(f"  • {category}: {data['average_score']:.2f} average score ({data['assessed_policies']} assessed)")
    
    # Show top policies
    print("\n🏆 Top Performing Policies:")
    for i, (policy_name, score) in enumerate(summary['top_policies'], 1):
        print(f"  {i}. {policy_name}: {score:.2f}")
    
    # Demonstrate policy assessment
    print("\n📈 Demonstrating New Policy Assessment...")
    
    # Create a new policy
    new_policy = Policy(
        id="DEMO-001",
        name="Digital Government Services Initiative",
        category="Phát triển đô thị",
        implementation_year=2023,
        description="Comprehensive digitalization of government services",
        implementing_agency="Government Technology Agency",
        objectives=["Digital transformation", "Service efficiency", "Citizen convenience"]
    )
    
    framework.add_policy(new_policy)
    
    # Assess the new policy
    assessment_scores = {
        'scope': 4,
        'magnitude': 4,
        'durability': 3,
        'adaptability': 5,
        'cross_referencing': 3
    }
    
    overall_score = framework.assess_policy(
        new_policy,
        assessment_scores,
        assessor="Demo User",
        notes="Initial assessment of digital government initiative"
    )
    
    print(f"✅ New policy assessed: {new_policy.name}")
    print(f"Overall Impact Score: {overall_score:.2f}")
    
    # Demonstrate policy evolution analysis
    print("\n📊 Policy Evolution Analysis Example:")
    
    # Analyze HDB policy evolution
    hdb_policy = framework.policies.get_policy_by_id("HDB-001")
    if hdb_policy:
        evolution_analysis = framework.analyze_policy_evolution("HDB-001")
        
        print(f"Policy: {evolution_analysis['policy_name']}")
        print(f"Assessment Period: {evolution_analysis['assessment_period']['duration_years']:.1f} years")
        print(f"Overall Trend: {evolution_analysis['summary']['overall_trend']}")
        print(f"Strongest Improvement: {evolution_analysis['summary']['strongest_improvement']}")
    
    # Demonstrate policy comparison
    print("\n🔍 Policy Comparison Example:")
    
    policy_ids = ["HDB-001", "CPF-001", "GST-001"]
    comparison = framework.compare_policies(policy_ids)
    
    print(f"Comparing {comparison['comparison_summary']['policies_compared']} policies")
    print(f"Average Overall Score: {comparison['comparison_summary']['average_overall_score']:.2f}")
    
    print("\nTop 3 by Overall Score:")
    for i, policy_data in enumerate(comparison['rankings']['overall_score'][:3], 1):
        print(f"  {i}. {policy_data['policy_name']}: {policy_data['overall_score']:.2f}")
    
    # Export data
    print("\n💾 Exporting framework data...")
    
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    framework.export_data(str(output_dir))
    print(f"✅ Data exported to: {output_dir.absolute()}")
    
    # Create visualizations
    print("\n📊 Creating visualizations...")
    
    try:
        # Create individual charts
        ranking_chart = framework.create_visualization("ranking")
        print("✅ Policy ranking chart created")
        
        # Create dashboard
        dashboard_path = framework.visualizer.create_dashboard(framework.policies, str(output_dir / "dashboard"))
        print(f"✅ Dashboard created: {dashboard_path}")
        
    except Exception as e:
        print(f"⚠️  Visualization creation failed: {e}")
        print("   This is normal if running without display or missing optional dependencies")
    
    # Show next steps
    print("\n🎯 Next Steps:")
    print("1. Review the exported data in the 'output' directory")
    print("2. Open the dashboard HTML file in your browser")
    print("3. Add your own policies using framework.add_policy()")
    print("4. Conduct assessments using framework.assess_policy()")
    print("5. Analyze trends using framework.analyze_category_trends()")
    
    print("\n✨ Demo completed successfully!")
    

def demonstrate_advanced_features():
    """Demonstrate advanced framework features."""
    
    print("\n🔬 Advanced Features Demo")
    print("-" * 40)
    
    framework = PolicyAssessmentFramework()
    
    # Load sample data
    sample_policies = create_sample_data()
    for policy in sample_policies:
        framework.add_policy(policy)
    
    # Category trend analysis
    print("\n📈 Category Trend Analysis:")
    
    urban_policies = framework.policies.get_policies_by_category("Phát triển đô thị")
    if urban_policies:
        trends = framework.analyze_category_trends("Phát triển đô thị")
        print(f"Category: {trends['category']}")
        print(f"Analysis Period: {trends['analysis_period']['start_year']} - {trends['analysis_period']['end_year']}")
        print(f"Total Policies: {trends['analysis_period']['total_policies']}")
        
        if 'category_insights' in trends:
            print("Key Insights:")
            for insight in trends['category_insights']:
                print(f"  • {insight}")
    
    # Policy prediction
    print("\n🔮 Policy Impact Prediction:")
    
    hdb_policy = framework.policies.get_policy_by_id("HDB-001")
    if hdb_policy and len(hdb_policy.assessments) >= 3:
        try:
            prediction = framework.analyzer.predict_policy_impact(hdb_policy, months_ahead=6)
            print(f"Policy: {prediction['policy_name']}")
            print(f"Trend Direction: {prediction['model_performance']['trend_direction']}")
            print(f"Model R²: {prediction['model_performance']['r_squared']:.3f}")
            
            print("6-Month Predictions:")
            for pred in prediction['predictions'][:3]:
                print(f"  {pred['date']}: {pred['predicted_score']:.2f} "
                      f"(CI: {pred['confidence_interval']['lower']:.2f}-{pred['confidence_interval']['upper']:.2f})")
        except Exception as e:
            print(f"Prediction not available: {e}")
    
    print("\n✅ Advanced features demo completed!")


def demonstrate_advanced_temporal_analysis():
    """Demonstrate advanced temporal and contextual analysis features."""
    
    print("\n🕐 Advanced Temporal & Contextual Analysis")
    print("=" * 60)
    
    framework = PolicyAssessmentFramework()
    
    # Load sample data with more historical assessments
    sample_policies = create_sample_data()
    for policy in sample_policies:
        framework.add_policy(policy)
    
    # Add additional historical assessments for better temporal analysis
    hdb_policy = framework.policies.get_policy_by_id("HDB-001")
    if hdb_policy:
        # Add more assessment points to show evolution
        additional_assessments = [
            {
                'date': datetime(2015, 6, 15),
                'scores': {'scope': 5, 'magnitude': 4, 'durability': 5, 'adaptability': 3, 'cross_referencing': 4}
            },
            {
                'date': datetime(2018, 3, 20),
                'scores': {'scope': 5, 'magnitude': 5, 'durability': 5, 'adaptability': 4, 'cross_referencing': 4}
            }
        ]
        
        for assessment_data in additional_assessments:
            framework.assess_policy(
                hdb_policy,
                assessment_data['scores'],
                assessor="Historical Analysis Team",
                notes=f"Historical assessment for temporal analysis - {assessment_data['date'].year}"
            )
    
    print("\n📊 1. Temporal Concatenation Analysis")
    print("-" * 40)
    
    try:
        temporal_analysis = framework.analyze_temporal_concatenation()
        
        # Show slow burn policies
        slow_burn = temporal_analysis['temporal_patterns']['slow_burn_policies']
        if slow_burn:
            print(f"🐌 Slow Burn Policies ({len(slow_burn)} found):")
            for policy_data in slow_burn[:3]:  # Show top 3
                policy = policy_data['policy']
                print(f"  • {policy.name}")
                print(f"    Initial Score: {policy_data['initial_score']:.2f}")
                print(f"    Latest Score: {policy_data['latest_score']:.2f}")
                print(f"    Improvement Rate: {policy_data['improvement_rate']:.3f}/year")
                print(f"    Years to Maturity: {policy_data['years_to_maturity']:.1f}")
        
        # Show immediate response policies
        immediate = temporal_analysis['temporal_patterns']['immediate_response_policies']
        if immediate:
            print(f"\n⚡ Immediate Response Policies ({len(immediate)} found):")
            for policy_data in immediate[:3]:
                policy = policy_data['policy']
                print(f"  • {policy.name} (Score: {policy_data['initial_score']:.2f})")
                print(f"    Implemented: {policy_data['implementation_year']}")
        
        # Show concatenation insights
        if 'concatenation_insights' in temporal_analysis:
            print(f"\n💡 Key Insights:")
            for insight in temporal_analysis['concatenation_insights']:
                print(f"  • {insight}")
    
    except Exception as e:
        print(f"⚠️  Temporal analysis error: {e}")
    
    print("\n📅 2. Contextual Timing Analysis")
    print("-" * 40)
    
    try:
        contextual_analysis = framework.analyze_contextual_timing()
        
        # Show well-timed policies
        well_timed = contextual_analysis['timing_analysis']['well_timed_policies']
        if well_timed:
            print(f"🎯 Well-Timed Policies ({len(well_timed)} found):")
            for policy_data in well_timed[:3]:
                policy = policy_data['policy']
                print(f"  • {policy.name}")
                print(f"    Context: {policy_data['context']}")
                print(f"    Timing Score: {policy_data['timing_score']:.2f}")
                print(f"    Relevance: {policy_data['relevance_score']}/3")
        
        # Show proactive policies
        proactive = contextual_analysis['timing_analysis']['proactive_policies']
        if proactive:
            print(f"\n🔮 Proactive Policies ({len(proactive)} found):")
            for policy_data in proactive[:3]:
                policy = policy_data['policy']
                print(f"  • {policy.name}")
                print(f"    Anticipated: {policy_data['upcoming_context']}")
                print(f"    Preparation Time: {policy_data['preparation_time']} years")
                print(f"    Effectiveness: {policy_data['effectiveness']:.2f}")
        
        # Show contextual insights
        if 'contextual_insights' in contextual_analysis:
            print(f"\n💡 Contextual Insights:")
            for insight in contextual_analysis['contextual_insights']:
                print(f"  • {insight}")
    
    except Exception as e:
        print(f"⚠️  Contextual analysis error: {e}")
    
    print("\n🎯 3. Policy Trajectory Prediction")
    print("-" * 40)
    
    # Predict trajectory for HDB policy
    try:
        trajectory = framework.predict_policy_trajectory("HDB-001", "current_trend")
        
        print(f"Policy: {trajectory['policy_name']}")
        print(f"Scenario: {trajectory['scenario']}")
        print(f"Trend Direction: {trajectory['trajectory_characteristics']['trend_direction']}")
        print(f"Stability: {trajectory['trajectory_characteristics']['stability']}")
        
        # Show next 6 months predictions
        print("\nNext 6 Months Forecast:")
        for pred in trajectory['predictions'][:6]:
            print(f"  Month {pred['month']:2d}: {pred['predicted_score']:.2f} "
                  f"(Confidence: {pred['confidence']:.1%})")
        
        # Show key milestones
        if trajectory['key_milestones']:
            print("\nKey Milestones:")
            for milestone in trajectory['key_milestones'][:3]:
                print(f"  • Month {milestone['month']}: {milestone['milestone']}")
    
    except Exception as e:
        print(f"⚠️  Trajectory prediction error: {e}")
    
    print("\n🏆 4. Policy Maturity Analysis")
    print("-" * 40)
    
    try:
        maturity_analysis = framework.analyze_policy_maturity_distribution()
        
        print("Maturity Distribution:")
        for stage, data in maturity_analysis['stage_distribution'].items():
            print(f"  • {stage}: {data['count']} policies ({data['percentage']:.1f}%)")
        
        # Show most mature policies
        highly_mature = maturity_analysis['stage_distribution'].get('Highly Mature', {}).get('policies', [])
        if highly_mature:
            print(f"\n🥇 Highly Mature Policies:")
            for policy_data in highly_mature[:3]:
                print(f"  • {policy_data['policy_name']} (Index: {policy_data['maturity_index']:.3f})")
    
    except Exception as e:
        print(f"⚠️  Maturity analysis error: {e}")
    
    print("\n📋 5. Advanced Insights Report")
    print("-" * 40)
    
    try:
        insights_report = framework.generate_advanced_insights_report()
        
        if 'strategic_recommendations' in insights_report:
            print("Strategic Recommendations:")
            for i, rec in enumerate(insights_report['strategic_recommendations'][:3], 1):
                print(f"\n{i}. {rec['category']} (Priority: {rec['priority']})")
                print(f"   {rec['recommendation']}")
                print(f"   Rationale: {rec['rationale']}")
    
    except Exception as e:
        print(f"⚠️  Advanced insights error: {e}")
    
    print("\n✨ Advanced temporal analysis completed!")


if __name__ == "__main__":
    try:
        main()
        
        # Ask user if they want to see advanced features
        print("\n" + "=" * 60)
        response = input("Would you like to see advanced features demo? (y/n): ").lower().strip()
        
        if response in ['y', 'yes']:
            demonstrate_advanced_features()
            
            # Ask for temporal analysis demo
            print("\n" + "=" * 60)
            response2 = input("Would you like to see advanced temporal analysis? (y/n): ").lower().strip()
            
            if response2 in ['y', 'yes']:
                demonstrate_advanced_temporal_analysis()
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        print("Please check the logs for more details")
        sys.exit(1)
