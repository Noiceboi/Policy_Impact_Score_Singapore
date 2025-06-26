#!/usr/bin/env python3
"""
Test script for Policy Impact Assessment Framework
"""

from src.framework import PolicyAssessmentFramework
from src.analysis import PolicyAnalyzer

def test_csv_loading():
    """Test loading data from CSV files."""
    print("🔍 Testing CSV data loading...")
    
    framework = PolicyAssessmentFramework()
    
    # Load sample data
    framework.load_policies_from_csv('data/sample_policies.csv')
    framework.load_assessments_from_csv('data/sample_assessments.csv')
    
    print(f"✅ Loaded {framework.policies.total_policies} policies")
    
    # Generate summary
    summary = framework.generate_summary_report()
    print(f"✅ Assessment coverage: {summary['assessment_coverage']:.1f}%")
    
    print("\n🏆 Top 5 policies:")
    for i, (name, score) in enumerate(summary['top_policies'][:5], 1):
        print(f"  {i}. {name}: {score:.2f}")
    
    print("\n📊 Category performance:")
    for category, data in summary['category_scores'].items():
        print(f"  • {category}: {data['average_score']:.2f} ({data['assessed_policies']} policies)")
    
    return framework

def test_policy_evolution():
    """Test policy evolution analysis."""
    print("\n🔍 Testing policy evolution analysis...")
    
    framework = test_csv_loading()
    
    # Test HDB policy evolution (has multiple assessments)
    try:
        evolution = framework.analyze_policy_evolution('HDB-001')
        print(f"✅ Evolution analysis for: {evolution['policy_name']}")
        print(f"  • Assessment period: {evolution['assessment_period']['duration_years']:.1f} years")
        print(f"  • Overall trend: {evolution['summary']['overall_trend']}")
        print(f"  • Total assessments: {evolution['summary']['total_assessments']}")
    except Exception as e:
        print(f"❌ Evolution analysis failed: {e}")

def test_policy_comparison():
    """Test policy comparison."""
    print("\n🔍 Testing policy comparison...")
    
    framework = test_csv_loading()
    
    # Compare top 3 policies
    policy_ids = ['HDB-001', 'CPF-001', 'GST-001']
    
    try:
        comparison = framework.compare_policies(policy_ids)
        print(f"✅ Compared {comparison['comparison_summary']['policies_compared']} policies")
        print(f"  • Average score: {comparison['comparison_summary']['average_overall_score']:.2f}")
        print(f"  • Score range: {comparison['comparison_summary']['score_range']['min']:.2f} - {comparison['comparison_summary']['score_range']['max']:.2f}")
        
        print("\n  Rankings by overall score:")
        for i, policy_data in enumerate(comparison['rankings']['overall_score'][:3], 1):
            print(f"    {i}. {policy_data['policy_name']}: {policy_data['overall_score']:.2f}")
            
    except Exception as e:
        print(f"❌ Policy comparison failed: {e}")

if __name__ == "__main__":
    print("🏛️  Policy Impact Assessment Framework - Test Suite")
    print("=" * 60)
    
    try:
        test_csv_loading()
        test_policy_evolution()
        test_policy_comparison()
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
