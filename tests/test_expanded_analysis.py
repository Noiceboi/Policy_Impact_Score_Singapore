"""
Quick test script for expanded policy analysis
"""

import sys
from pathlib import Path
from datetime import datetime

# Add our framework
sys.path.append('src')
from framework import PolicyAssessmentFramework
from models import Policy

def test_expanded_analysis():
    """Test the expanded analysis functionality."""
    print("🧪 Testing expanded policy analysis...")
    
    # Initialize framework
    framework = PolicyAssessmentFramework()
    
    # Create test policies
    test_policies = [
        {
            'id': 'test_001',
            'name': 'Housing Development Board (HDB)',
            'category': 'An sinh xã hội',
            'implementation_year': 1960,
            'description': 'National public housing program'
        },
        {
            'id': 'test_002',
            'name': 'Central Provident Fund (CPF)',
            'category': 'An sinh xã hội',
            'implementation_year': 1955,
            'description': 'Social security savings system'
        }
    ]
    
    # Add policies to framework
    for policy_data in test_policies:
        policy = Policy(
            id=policy_data['id'],
            name=policy_data['name'],
            category=policy_data['category'],
            implementation_year=policy_data['implementation_year']
        )
        policy.description = policy_data['description']
        framework.add_policy(policy)
    
    print(f"✅ Added {len(test_policies)} test policies")
    
    # Test assessments
    test_scores = {
        'test_001': {'scope': 5, 'magnitude': 5, 'durability': 5, 'adaptability': 4, 'cross_referencing': 5},
        'test_002': {'scope': 5, 'magnitude': 5, 'durability': 5, 'adaptability': 4, 'cross_referencing': 5}
    }
    
    for policy_id, scores in test_scores.items():
        try:
            overall_score = framework.assess_policy(
                policy=policy_id,
                criteria_scores=scores,
                assessor="Test System"
            )
            print(f"✅ {policy_id}: {overall_score:.2f}")
        except Exception as e:
            print(f"❌ Failed to assess {policy_id}: {str(e)}")
    
    # Test data collection
    print(f"\n📊 Framework Summary:")
    print(f"   Policies: {len(framework.policies.policies)}")
    
    total_assessments = 0
    for policy in framework.policies.policies:
        total_assessments += len(policy.assessments)
    print(f"   Total Assessments: {total_assessments}")
    
    # Create simple report
    output_dir = Path('output/expanded_analysis')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_dir / f'test_report_{timestamp}.txt'
    
    with open(report_file, 'w') as f:
        f.write("Quick Test Report\n")
        f.write("=================\n\n")
        f.write(f"Test run: {datetime.now()}\n")
        f.write(f"Policies: {len(framework.policies.policies)}\n")
        f.write(f"Assessments: {total_assessments}\n\n")
        
        f.write("Policy Details:\n")
        for policy in framework.policies.policies:
            f.write(f"- {policy.name} ({policy.implementation_year})\n")
            f.write(f"  Category: {policy.category}\n")
            f.write(f"  Assessments: {len(policy.assessments)}\n")
            for assessment in policy.assessments:
                f.write(f"    Score: {assessment.overall_score:.2f}\n")
            f.write("\n")
    
    print(f"📄 Test report saved: {report_file}")
    print("🎉 Test completed successfully!")

if __name__ == "__main__":
    test_expanded_analysis()
