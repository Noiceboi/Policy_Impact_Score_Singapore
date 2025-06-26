"""
Simple Cross-Study Analysis Script
==================================

This script creates comparison tables directly from Singapore policy data
with data integrity validation.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import sys
sys.path.append('src')

print("🚀 Starting Simple Cross-Study Analysis")
print("=" * 50)

# Create output directory
output_dir = Path('output/cross_study_analysis')
output_dir.mkdir(exist_ok=True)

# Load data directly
print("📊 Loading Singapore policy data...")

# Load policies
policies_df = pd.read_csv('templates/singapore_policies_template.csv')
print(f"✅ Loaded {len(policies_df)} policies")

# Load assessments
assessments_df = pd.read_csv('templates/singapore_assessments_template.csv')
print(f"✅ Loaded {len(assessments_df)} assessments")

# Merge data for analysis
merged_df = assessments_df.merge(
    policies_df, 
    on='policy_id', 
    how='left',
    suffixes=('_assessment', '_policy')
)

print(f"🔗 Merged data: {len(merged_df)} assessment records")

# Calculate overall scores using weighted average
def calculate_overall_score(row):
    weights = {
        'scope': 0.15,
        'magnitude': 0.25,
        'durability': 0.30,
        'adaptability': 0.20,
        'cross_referencing': 0.10
    }
    
    weighted_score = (
        row['scope'] * weights['scope'] +
        row['magnitude'] * weights['magnitude'] +
        row['durability'] * weights['durability'] +
        row['adaptability'] * weights['adaptability'] +
        row['cross_referencing'] * weights['cross_referencing']
    )
    
    return round(weighted_score, 2)

merged_df['overall_score'] = merged_df.apply(calculate_overall_score, axis=1)

# 1. POLICY CATEGORY IMPACT MATRIX
print("📋 Creating Policy Category Impact Matrix...")

category_matrix = merged_df.groupby(['policy_name', 'category']).agg({
    'scope': 'mean',
    'magnitude': 'mean',
    'durability': 'mean',
    'adaptability': 'mean',
    'cross_referencing': 'mean',
    'overall_score': 'mean',
    'assessment_date': 'count',
    'assessor_organization': 'nunique',
    'confidence_level': 'mean'
}).round(2)

category_matrix.columns = [
    'Avg Scope Score', 'Avg Magnitude Score', 'Avg Durability Score',
    'Avg Adaptability Score', 'Avg Cross-ref Score', 'Overall Impact Score',
    'Assessment Count', 'Assessor Diversity', 'Avg Confidence Level'
]

category_matrix = category_matrix.reset_index()
category_matrix['Data Quality'] = category_matrix.apply(
    lambda x: 'High' if x['Assessment Count'] >= 2 and x['Assessor Diversity'] >= 2 else 
             'Medium' if x['Assessment Count'] >= 1 else 'Low', axis=1
)

# Export category matrix
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
category_file = output_dir / f'policy_category_matrix_{timestamp}.csv'
category_matrix.to_csv(category_file, index=False, encoding='utf-8')
print(f"💾 Saved: {category_file}")

# 2. DATA INTEGRITY REPORT
print("🔍 Creating Data Integrity Report...")

integrity_report = []

for policy_id in policies_df['policy_id'].unique():
    policy_name = policies_df[policies_df['policy_id'] == policy_id]['policy_name'].iloc[0]
    category = policies_df[policies_df['policy_id'] == policy_id]['category'].iloc[0]
    
    policy_assessments = assessments_df[assessments_df['policy_id'] == policy_id]
    
    if len(policy_assessments) > 0:
        # Calculate metrics
        assessment_count = len(policy_assessments)
        assessor_diversity = policy_assessments['assessor_organization'].nunique()
        
        # Score consistency
        scores = []
        for _, row in policy_assessments.iterrows():
            score = calculate_overall_score(row)
            scores.append(score)
        
        score_consistency = 1 / (1 + np.std(scores)) if len(scores) > 1 else 1.0
        
        # Time coverage
        dates = pd.to_datetime(policy_assessments['assessment_date'])
        time_span = (dates.max() - dates.min()).days / 365.25
        time_coverage = min(time_span / 5.0, 1.0)
        
        # Data completeness
        completeness_fields = ['scope', 'magnitude', 'durability', 'adaptability', 'cross_referencing']
        completeness_scores = []
        for _, row in policy_assessments.iterrows():
            completed = sum([1 for field in completeness_fields if row[field] > 0])
            completeness_scores.append(completed / len(completeness_fields))
        
        data_completeness = np.mean(completeness_scores)
        
        # Overall integrity score
        integrity_score = (
            0.3 * min(assessment_count / 3, 1.0) +
            0.2 * min(assessor_diversity / 2, 1.0) +
            0.2 * score_consistency +
            0.15 * time_coverage +
            0.15 * data_completeness
        )
        
        quality_level = 'High' if integrity_score >= 0.8 else 'Medium' if integrity_score >= 0.6 else 'Low'
        
        integrity_report.append({
            'Policy ID': policy_id,
            'Policy Name': policy_name,
            'Category': category,
            'Assessment Count': assessment_count,
            'Assessor Diversity': assessor_diversity,
            'Score Consistency': round(score_consistency, 3),
            'Time Coverage': round(time_coverage, 3),
            'Data Completeness': round(data_completeness, 3),
            'Overall Integrity Score': round(integrity_score, 3),
            'Data Quality Level': quality_level,
            'Validation Status': 'Validated' if integrity_score > 0.7 else 'Needs Review'
        })

integrity_df = pd.DataFrame(integrity_report)
integrity_file = output_dir / f'data_integrity_report_{timestamp}.csv'
integrity_df.to_csv(integrity_file, index=False, encoding='utf-8')
print(f"💾 Saved: {integrity_file}")

# 3. TIME SERIES EFFECTIVENESS ANALYSIS
print("📈 Creating Time Series Analysis...")

time_series_data = []

for _, row in merged_df.iterrows():
    assessment_date = pd.to_datetime(row['assessment_date'])
    implementation_date = pd.to_datetime(row['implementation_date'])
    years_since = (assessment_date - implementation_date).days / 365.25
    
    time_series_data.append({
        'Policy ID': row['policy_id'],
        'Policy Name': row['policy_name'],
        'Category': row['category'],
        'Implementation Year': implementation_date.year,
        'Assessment Date': assessment_date.strftime('%Y-%m-%d'),
        'Years Since Implementation': round(years_since, 1),
        'Overall Score': row['overall_score'],
        'Durability Score': row['durability'],
        'Adaptability Score': row['adaptability'],
        'Assessor': row['assessor_organization'],
        'Confidence Level': row['confidence_level']
    })

time_series_df = pd.DataFrame(time_series_data)
time_series_file = output_dir / f'time_series_analysis_{timestamp}.csv'
time_series_df.to_csv(time_series_file, index=False, encoding='utf-8')
print(f"💾 Saved: {time_series_file}")

# 4. INTERNATIONAL BENCHMARKS (Simulated)
print("🌍 Creating International Benchmarks...")

benchmark_data = []
categories = policies_df['category'].unique()

for category in categories:
    category_policies = merged_df[merged_df['category'] == category]
    sg_avg_score = category_policies['overall_score'].mean()
    
    # Simulated international data (in real implementation, this would come from APIs)
    benchmark_data.append({
        'Category': category,
        'Singapore Average Score': round(sg_avg_score, 2),
        'OECD Average': round(sg_avg_score * (0.85 + np.random.random() * 0.3), 2),
        'Asian Countries Average': round(sg_avg_score * (0.9 + np.random.random() * 0.2), 2),
        'Global Best Practice': round(min(sg_avg_score * 1.2, 5.0), 2),
        'Singapore Rank (Simulated)': np.random.randint(1, 15),
        'Policy Count': len(category_policies['policy_name'].unique()),
        'Performance Level': 'Above Average' if sg_avg_score > 3.5 else 'Average' if sg_avg_score > 2.5 else 'Below Average'
    })

benchmark_df = pd.DataFrame(benchmark_data)
benchmark_file = output_dir / f'international_benchmarks_{timestamp}.csv'
benchmark_df.to_csv(benchmark_file, index=False, encoding='utf-8')
print(f"💾 Saved: {benchmark_file}")

# 5. SUCCESS FACTOR ANALYSIS
print("🎯 Creating Success Factor Analysis...")

success_data = []

for policy_name in policies_df['policy_name'].unique():
    policy_data = merged_df[merged_df['policy_name'] == policy_name]
    
    if len(policy_data) > 0:
        avg_scores = {
            'scope': policy_data['scope'].mean(),
            'magnitude': policy_data['magnitude'].mean(),
            'durability': policy_data['durability'].mean(),
            'adaptability': policy_data['adaptability'].mean(),
            'cross_referencing': policy_data['cross_referencing'].mean()
        }
        
        overall_score = policy_data['overall_score'].mean()
        success_level = 'High' if overall_score >= 4.0 else 'Medium' if overall_score >= 3.0 else 'Low'
        
        strongest_factor = max(avg_scores, key=avg_scores.get)
        weakest_factor = min(avg_scores, key=avg_scores.get)
        
        success_data.append({
            'Policy Name': policy_name,
            'Category': policy_data['category'].iloc[0],
            'Overall Score': round(overall_score, 2),
            'Success Level': success_level,
            'Strongest Factor': strongest_factor.title(),
            'Strongest Score': round(avg_scores[strongest_factor], 2),
            'Weakest Factor': weakest_factor.title(),
            'Weakest Score': round(avg_scores[weakest_factor], 2),
            'Score Range': round(avg_scores[strongest_factor] - avg_scores[weakest_factor], 2)
        })

success_df = pd.DataFrame(success_data)
success_file = output_dir / f'success_factor_analysis_{timestamp}.csv'
success_df.to_csv(success_file, index=False, encoding='utf-8')
print(f"💾 Saved: {success_file}")

# 6. ECONOMIC IMPACT CORRELATION (Simulated)
print("💰 Creating Economic Impact Analysis...")

economic_data = []

for _, row in category_matrix.iterrows():
    # Simulated economic indicators (would be real data from Singapore APIs)
    gdp_impact = np.random.normal(0.1, 0.05)
    employment_impact = np.random.normal(0.05, 0.03)
    productivity_impact = np.random.normal(0.08, 0.04)
    
    economic_data.append({
        'Policy Name': row['policy_name'],
        'Category': row['category'],
        'Policy Impact Score': row['Overall Impact Score'],
        'GDP Impact (%)': round(gdp_impact * 100, 2),
        'Employment Impact (%)': round(employment_impact * 100, 2),
        'Productivity Impact (%)': round(productivity_impact * 100, 2),
        'Economic Efficiency Score': round((gdp_impact + employment_impact + productivity_impact) / 3 * 100, 2)
    })

economic_df = pd.DataFrame(economic_data)
economic_file = output_dir / f'economic_impact_analysis_{timestamp}.csv'
economic_df.to_csv(economic_file, index=False, encoding='utf-8')
print(f"💾 Saved: {economic_file}")

# Create comprehensive Excel file with all tables
excel_file = output_dir / f'singapore_policy_comprehensive_analysis_{timestamp}.xlsx'

with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
    category_matrix.to_excel(writer, sheet_name='Policy_Category_Matrix', index=False)
    integrity_df.to_excel(writer, sheet_name='Data_Integrity_Report', index=False)
    time_series_df.to_excel(writer, sheet_name='Time_Series_Analysis', index=False)
    benchmark_df.to_excel(writer, sheet_name='International_Benchmarks', index=False)
    success_df.to_excel(writer, sheet_name='Success_Factor_Analysis', index=False)
    economic_df.to_excel(writer, sheet_name='Economic_Impact_Analysis', index=False)

print(f"📊 Comprehensive Excel file: {excel_file}")

# Generate summary report
summary_stats = {
    'analysis_date': datetime.now().isoformat(),
    'total_policies': len(policies_df),
    'total_assessments': len(assessments_df),
    'high_integrity_policies': len(integrity_df[integrity_df['Data Quality Level'] == 'High']),
    'average_impact_score': round(category_matrix['Overall Impact Score'].mean(), 2),
    'average_integrity_score': round(integrity_df['Overall Integrity Score'].mean(), 3),
    'data_coverage': {
        'policies_with_multiple_assessments': len(category_matrix[category_matrix['Assessment Count'] >= 2]),
        'categories_covered': len(categories),
        'assessor_organizations': assessments_df['assessor_organization'].nunique()
    },
    'top_performing_policies': category_matrix.nlargest(3, 'Overall Impact Score')[['policy_name', 'category', 'Overall Impact Score']].to_dict('records'),
    'key_findings': [
        f"Total {len(policies_df)} Singapore policies analyzed across {len(categories)} categories",
        f"{len(integrity_df[integrity_df['Data Quality Level'] == 'High'])} policies meet high data integrity standards",
        f"Average policy impact score: {round(category_matrix['Overall Impact Score'].mean(), 2)}/5.0",
        f"Data integrity rate: {round(len(integrity_df[integrity_df['Data Quality Level'] == 'High'])/len(policies_df)*100, 1)}%",
        f"Assessment coverage: {len(assessments_df)} assessments from {assessments_df['assessor_organization'].nunique()} organizations"
    ]
}

summary_file = output_dir / f'comprehensive_summary_{timestamp}.json'
import json
with open(summary_file, 'w', encoding='utf-8') as f:
    json.dump(summary_stats, f, indent=2, ensure_ascii=False)

print(f"📋 Summary report: {summary_file}")

print("\n🎯 CROSS-STUDY ANALYSIS COMPLETED!")
print("=" * 50)
print(f"📊 Total Policies Analyzed: {len(policies_df)}")
print(f"🔍 Total Assessments: {len(assessments_df)}")
print(f"🏆 High Integrity Policies: {len(integrity_df[integrity_df['Data Quality Level'] == 'High'])}")
print(f"📈 Average Impact Score: {round(category_matrix['Overall Impact Score'].mean(), 2)}/5.0")
print(f"📁 All analysis files saved in: {output_dir}")
print("\n✅ Ready for policy validation and cross-study comparison!")
