"""
Data Content Analysis - Manual Review of Excel Files
===================================================

This script performs manual analysis of Excel file structure and content
to assess data quality and scientific validity.
"""

import os
import json
from datetime import datetime


def analyze_excel_file_structure():
    """Analyze Excel file structure and content quality."""
    print("=" * 60)
    print("📊 EXCEL DATA STRUCTURE ANALYSIS")
    print("=" * 60)
    
    excel_files = [
        'output/expanded_analysis/singapore_expanded_policy_analysis_20250626_112947.xlsx',
        'output/cross_study_analysis/singapore_policy_comprehensive_analysis_20250626_003826.xlsx',
        'output/comprehensive_policy_research/singapore_policy_comprehensive_research_20250626_105450.xlsx'
    ]
    
    analysis_results = []
    
    for excel_file in excel_files:
        if os.path.exists(excel_file):
            file_size = os.path.getsize(excel_file)
            modified_time = datetime.fromtimestamp(os.path.getmtime(excel_file))
            
            print(f"📄 {os.path.basename(excel_file)}")
            print(f"   Size: {file_size:,} bytes")
            print(f"   Modified: {modified_time}")
            print(f"   Path: {excel_file}")
            
            # Assess data completeness based on file size
            if file_size > 10000:
                data_completeness = "HIGH"
            elif file_size > 5000:
                data_completeness = "MEDIUM"
            else:
                data_completeness = "LOW"
            
            analysis_results.append({
                'file': excel_file,
                'size': file_size,
                'modified': modified_time.isoformat(),
                'data_completeness': data_completeness
            })
            print(f"   Data Completeness: {data_completeness}")
            print()
    
    return analysis_results


def analyze_markdown_reports():
    """Analyze generated markdown reports for completeness."""
    print("📝 MARKDOWN REPORTS ANALYSIS:")
    print("-" * 40)
    
    report_files = [
        'SCIENTIFIC_RIGOR_ASSESSMENT.md',
        'EXPANDED_ANALYSIS_COMPLETION_REPORT.md',
        'output/expanded_analysis/EXPANDED_POLICY_ANALYSIS_20250626_112947.md',
        'output/expanded_analysis/DATA_VALIDATION_REPORT_20250626_120701.md'
    ]
    
    report_analysis = []
    
    for report_file in report_files:
        if os.path.exists(report_file):
            with open(report_file, 'r', encoding='utf-8') as f:
                content = f.read()
                word_count = len(content.split())
                line_count = len(content.split('\n'))
                
            print(f"📋 {os.path.basename(report_file)}")
            print(f"   Words: {word_count:,}")
            print(f"   Lines: {line_count:,}")
            
            # Assess report quality
            if word_count > 1000:
                report_quality = "COMPREHENSIVE"
            elif word_count > 500:
                report_quality = "DETAILED"
            elif word_count > 100:
                report_quality = "BASIC"
            else:
                report_quality = "MINIMAL"
            
            print(f"   Quality: {report_quality}")
            
            # Check for key scientific terms
            scientific_indicators = [
                'methodology', 'validation', 'assessment', 'analysis',
                'data', 'source', 'benchmark', 'indicator', 'criteria'
            ]
            
            scientific_score = sum(1 for term in scientific_indicators if term.lower() in content.lower())
            print(f"   Scientific Terms: {scientific_score}/{len(scientific_indicators)}")
            
            report_analysis.append({
                'file': report_file,
                'word_count': word_count,
                'line_count': line_count,
                'quality': report_quality,
                'scientific_score': scientific_score
            })
            print()
    
    return report_analysis


def assess_framework_completeness():
    """Assess the completeness of the framework implementation."""
    print("🏗️  FRAMEWORK COMPLETENESS ASSESSMENT:")
    print("-" * 40)
    
    framework_components = {
        'Policy Data Model': 'src/models.py',
        'Assessment Framework': 'src/framework.py',
        'Analysis Engine': 'src/analysis.py',
        'Visualization Tools': 'src/visualization.py',
        'Cross-Reference System': 'src/cross_reference.py',
        'Utility Functions': 'src/utils.py',
        'Main Application': 'main.py',
        'Data Templates': 'templates/',
        'Documentation': 'docs/',
        'Test Cases': ['test_framework.py', 'test_expanded_analysis.py']
    }
    
    completeness_score = 0
    total_components = len(framework_components)
    
    for component, path in framework_components.items():
        if isinstance(path, list):
            # Multiple files - check if any exist
            exists = any(os.path.exists(p) for p in path)
        else:
            exists = os.path.exists(path)
        
        print(f"{'✅' if exists else '❌'} {component}")
        if exists:
            completeness_score += 1
    
    completeness_percentage = (completeness_score / total_components) * 100
    print(f"\n📊 Framework Completeness: {completeness_percentage:.1f}% ({completeness_score}/{total_components})")
    
    return completeness_percentage


def validate_scientific_citations():
    """Check for scientific citations and source references."""
    print("📚 CITATION AND SOURCE VALIDATION:")
    print("-" * 40)
    
    files_to_check = [
        'SCIENTIFIC_RIGOR_ASSESSMENT.md',
        'README.md',
        'docs/DATA_REQUIREMENTS.md'
    ]
    
    citation_patterns = [
        'source:', 'Source:', 'reference:', 'Reference:',
        'http://', 'https://', 'www.',
        'gov.sg', 'oecd', 'worldbank', 'un.org',
        'singapore', 'official', 'government'
    ]
    
    citation_analysis = []
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            citations_found = sum(1 for pattern in citation_patterns 
                                if pattern.lower() in content.lower())
            
            print(f"📄 {file_path}")
            print(f"   Citation indicators: {citations_found}")
            
            # Check for specific data sources
            gov_sources = content.lower().count('.gov') + content.lower().count('government')
            intl_sources = content.lower().count('oecd') + content.lower().count('world bank') + content.lower().count('un ')
            
            print(f"   Government sources: {gov_sources}")
            print(f"   International sources: {intl_sources}")
            print()
            
            citation_analysis.append({
                'file': file_path,
                'citation_indicators': citations_found,
                'government_sources': gov_sources,
                'international_sources': intl_sources
            })
    
    return citation_analysis


def generate_comprehensive_validity_report():
    """Generate comprehensive validity assessment report."""
    print("📋 COMPREHENSIVE VALIDITY ASSESSMENT")
    print("=" * 60)
    
    # Run all analyses
    excel_analysis = analyze_excel_file_structure()
    report_analysis = analyze_markdown_reports()
    completeness = assess_framework_completeness()
    citations = validate_scientific_citations()
    
    # Calculate overall validity scores
    structure_score = 100 if completeness >= 90 else (80 if completeness >= 70 else 60)
    
    data_score = 0
    for excel in excel_analysis:
        if excel['data_completeness'] == 'HIGH':
            data_score += 40
        elif excel['data_completeness'] == 'MEDIUM':
            data_score += 25
        else:
            data_score += 10
    data_score = min(100, data_score)
    
    documentation_score = 0
    for report in report_analysis:
        if report['quality'] == 'COMPREHENSIVE':
            documentation_score += 30
        elif report['quality'] == 'DETAILED':
            documentation_score += 20
        elif report['quality'] == 'BASIC':
            documentation_score += 10
        else:
            documentation_score += 5
    documentation_score = min(100, documentation_score)
    
    citation_score = 0
    for citation in citations:
        citation_score += min(25, citation['citation_indicators'] * 5)
        citation_score += min(25, citation['government_sources'] * 10)
        citation_score += min(25, citation['international_sources'] * 10)
    citation_score = min(100, citation_score // len(citations) if citations else 0)
    
    overall_score = (structure_score + data_score + documentation_score + citation_score) / 4
    
    # Generate final assessment
    assessment = {
        'assessment_timestamp': datetime.now().isoformat(),
        'validity_scores': {
            'framework_structure': structure_score,
            'data_completeness': data_score,
            'documentation_quality': documentation_score,
            'citation_transparency': citation_score,
            'overall_validity': overall_score
        },
        'excel_files_analyzed': len(excel_analysis),
        'reports_analyzed': len(report_analysis),
        'framework_completeness_percent': completeness,
        'detailed_analysis': {
            'excel_analysis': excel_analysis,
            'report_analysis': report_analysis,
            'citation_analysis': citations
        }
    }
    
    # Determine validity level
    if overall_score >= 85:
        validity_level = "HIGH_SCIENTIFIC_VALIDITY"
        confidence = "STRONG"
    elif overall_score >= 70:
        validity_level = "MODERATE_SCIENTIFIC_VALIDITY"
        confidence = "GOOD"
    elif overall_score >= 55:
        validity_level = "BASIC_SCIENTIFIC_VALIDITY"
        confidence = "ACCEPTABLE"
    else:
        validity_level = "INSUFFICIENT_SCIENTIFIC_VALIDITY"
        confidence = "WEAK"
    
    assessment['validity_level'] = validity_level
    assessment['confidence_level'] = confidence
    
    # Print final results
    print()
    print("🎯 COMPREHENSIVE VALIDITY ASSESSMENT RESULTS:")
    print("=" * 60)
    print(f"Framework Structure:    {structure_score:.1f}/100")
    print(f"Data Completeness:      {data_score:.1f}/100")
    print(f"Documentation Quality:  {documentation_score:.1f}/100")
    print(f"Citation Transparency:  {citation_score:.1f}/100")
    print()
    print(f"OVERALL VALIDITY SCORE: {overall_score:.1f}/100")
    print(f"VALIDITY LEVEL:         {validity_level}")
    print(f"CONFIDENCE LEVEL:       {confidence}")
    print()
    
    # Generate recommendations
    recommendations = []
    if structure_score < 90:
        recommendations.append("Complete all framework components")
    if data_score < 80:
        recommendations.append("Enhance data completeness and quality")
    if documentation_score < 80:
        recommendations.append("Improve documentation comprehensiveness")
    if citation_score < 70:
        recommendations.append("Add explicit citations and data sources")
    
    if recommendations:
        print("📋 RECOMMENDATIONS FOR IMPROVEMENT:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        print()
    
    assessment['recommendations'] = recommendations
    
    # Save comprehensive assessment
    with open('output/comprehensive_validity_assessment.json', 'w') as f:
        json.dump(assessment, f, indent=2)
    
    print(f"📄 Comprehensive assessment saved to: output/comprehensive_validity_assessment.json")
    
    return assessment


if __name__ == "__main__":
    assessment = generate_comprehensive_validity_report()
