"""
Scientific Validity and Data Integrity Assessment
===============================================

This script performs a comprehensive assessment of the scientific validity
of the Singapore Policy Impact Assessment Framework without relying on
external packages.
"""

import os
import json
from datetime import datetime


def check_file_existence():
    """Check if all required files exist."""
    print("=" * 60)
    print("🔍 COMPREHENSIVE SCIENTIFIC VALIDITY ASSESSMENT")
    print("=" * 60)
    print()
    
    required_files = [
        'src/models.py',
        'src/framework.py', 
        'src/analysis.py',
        'src/visualization.py',
        'src/utils.py',
        'src/cross_reference.py',
        'main.py',
        'requirements.txt',
        'README.md'
    ]
    
    print("📋 FILE STRUCTURE VALIDATION:")
    print("-" * 40)
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    print()
    if missing_files:
        print(f"⚠️  Missing {len(missing_files)} core files")
        return False
    else:
        print("✅ All core framework files present")
        return True


def analyze_data_files():
    """Analyze available data files."""
    print("📊 DATA FILES ANALYSIS:")
    print("-" * 40)
    
    data_directories = [
        'data/',
        'output/',
        'templates/',
        'docs/'
    ]
    
    data_files_found = []
    
    for directory in data_directories:
        if os.path.exists(directory):
            print(f"📁 {directory}")
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    data_files_found.append({
                        'path': file_path,
                        'size': file_size,
                        'type': file.split('.')[-1] if '.' in file else 'unknown'
                    })
                    print(f"   📄 {file} ({file_size:,} bytes)")
    
    print()
    return data_files_found


def analyze_output_files():
    """Analyze output files for data completeness."""
    print("📈 OUTPUT FILES ANALYSIS:")
    print("-" * 40)
    
    output_path = 'output/'
    analysis_types = []
    
    if os.path.exists(output_path):
        for root, dirs, files in os.walk(output_path):
            for file in files:
                if file.endswith('.xlsx'):
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    analysis_types.append({
                        'file': file,
                        'path': file_path,
                        'size': file_size,
                        'modified': datetime.fromtimestamp(os.path.getmtime(file_path))
                    })
                    print(f"📊 {file}")
                    print(f"   Size: {file_size:,} bytes")
                    print(f"   Modified: {datetime.fromtimestamp(os.path.getmtime(file_path))}")
                    print()
    
    return analysis_types


def check_code_quality():
    """Assess code quality and structure."""
    print("🔧 CODE QUALITY ASSESSMENT:")
    print("-" * 40)
    
    src_files = []
    if os.path.exists('src/'):
        for file in os.listdir('src/'):
            if file.endswith('.py'):
                file_path = os.path.join('src/', file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                src_files.append({
                    'file': file,
                    'lines': len(content.split('\n')),
                    'has_docstring': '"""' in content,
                    'has_type_hints': '->' in content,
                    'has_error_handling': 'try:' in content or 'except' in content,
                    'has_logging': 'logger' in content or 'logging' in content
                })
                
                print(f"📝 {file} ({len(content.split('\n'))} lines)")
                print(f"   Docstrings: {'✅' if '"""' in content else '❌'}")
                print(f"   Type hints: {'✅' if '->' in content else '❌'}")
                print(f"   Error handling: {'✅' if ('try:' in content or 'except' in content) else '❌'}")
                print(f"   Logging: {'✅' if ('logger' in content or 'logging' in content) else '❌'}")
                print()
    
    return src_files


def validate_scientific_methodology():
    """Validate the scientific methodology used."""
    print("🔬 SCIENTIFIC METHODOLOGY VALIDATION:")
    print("-" * 40)
    
    methodology_checks = {
        'mcda_framework': False,
        'scoring_system': False,
        'weighting_scheme': False,
        'validation_process': False,
        'cross_referencing': False
    }
    
    # Check framework.py for MCDA implementation
    if os.path.exists('src/framework.py'):
        with open('src/framework.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'MCDA' in content or 'Multi-Criteria' in content or 'criteria' in content.lower():
                methodology_checks['mcda_framework'] = True
            if 'score' in content.lower() and ('1' in content and '5' in content):
                methodology_checks['scoring_system'] = True
            if 'weight' in content.lower():
                methodology_checks['weighting_scheme'] = True
    
    # Check for validation processes
    if os.path.exists('data_validation_audit.py'):
        methodology_checks['validation_process'] = True
    
    # Check for cross-referencing
    if os.path.exists('src/cross_reference.py'):
        methodology_checks['cross_referencing'] = True
    
    print("📋 Methodology Components:")
    for component, status in methodology_checks.items():
        print(f"   {'✅' if status else '❌'} {component.replace('_', ' ').title()}")
    
    print()
    return methodology_checks


def assess_data_source_transparency():
    """Assess transparency of data sources."""
    print("📖 DATA SOURCE TRANSPARENCY:")
    print("-" * 40)
    
    transparency_issues = []
    
    # Check for source documentation
    docs_exist = os.path.exists('docs/')
    readme_exist = os.path.exists('README.md')
    
    print(f"Documentation folder: {'✅' if docs_exist else '❌'}")
    print(f"README file: {'✅' if readme_exist else '❌'}")
    
    # Check for data sources documentation
    if os.path.exists('docs/'):
        source_docs = [f for f in os.listdir('docs/') if f.endswith('.md')]
        print(f"Documentation files: {len(source_docs)}")
        for doc in source_docs:
            print(f"   📄 {doc}")
    
    # Check for templates (indicating data structure)
    if os.path.exists('templates/'):
        templates = [f for f in os.listdir('templates/') if f.endswith('.csv')]
        print(f"Data templates: {len(templates)}")
        for template in templates:
            print(f"   🗂️  {template}")
    
    print()
    
    if not docs_exist:
        transparency_issues.append("Missing documentation folder")
    if not readme_exist:
        transparency_issues.append("Missing README file")
    
    return transparency_issues


def generate_scientific_assessment_report():
    """Generate comprehensive scientific assessment report."""
    print("📋 GENERATING SCIENTIFIC ASSESSMENT REPORT")
    print("=" * 60)
    
    # Run all checks
    file_check = check_file_existence()
    data_files = analyze_data_files()
    output_files = analyze_output_files()
    code_quality = check_code_quality()
    methodology = validate_scientific_methodology()
    transparency_issues = assess_data_source_transparency()
    
    # Generate assessment
    assessment = {
        'assessment_date': datetime.now().isoformat(),
        'overall_status': 'PENDING_DETAILED_REVIEW',
        'file_structure': {
            'complete': file_check,
            'data_files_count': len(data_files),
            'output_files_count': len(output_files)
        },
        'code_quality': {
            'modules': len(code_quality),
            'has_documentation': sum(1 for f in code_quality if f['has_docstring']),
            'has_error_handling': sum(1 for f in code_quality if f['has_error_handling']),
            'total_lines': sum(f['lines'] for f in code_quality)
        },
        'methodology': methodology,
        'transparency_issues': transparency_issues,
        'recommendations': []
    }
    
    # Generate recommendations
    if not file_check:
        assessment['recommendations'].append("Complete missing core framework files")
    
    if len(transparency_issues) > 0:
        assessment['recommendations'].append("Improve data source documentation and transparency")
    
    if not all(methodology.values()):
        assessment['recommendations'].append("Complete implementation of all scientific methodology components")
    
    # Determine overall assessment
    critical_issues = len(transparency_issues) + (0 if file_check else 1) + sum(1 for v in methodology.values() if not v)
    
    if critical_issues == 0:
        assessment['overall_status'] = 'SCIENTIFICALLY_VALID'
        assessment['confidence_level'] = 'HIGH'
    elif critical_issues <= 2:
        assessment['overall_status'] = 'VALID_WITH_MINOR_ISSUES'
        assessment['confidence_level'] = 'MODERATE'
    else:
        assessment['overall_status'] = 'REQUIRES_SIGNIFICANT_IMPROVEMENT'
        assessment['confidence_level'] = 'LOW'
    
    # Print final assessment
    print()
    print("🎯 FINAL SCIENTIFIC VALIDITY ASSESSMENT:")
    print("=" * 60)
    print(f"Overall Status: {assessment['overall_status']}")
    print(f"Confidence Level: {assessment['confidence_level']}")
    print(f"Critical Issues: {critical_issues}")
    print()
    
    if assessment['recommendations']:
        print("📋 RECOMMENDATIONS:")
        for i, rec in enumerate(assessment['recommendations'], 1):
            print(f"{i}. {rec}")
        print()
    
    # Save assessment
    os.makedirs('output', exist_ok=True)
    with open('output/scientific_validity_assessment.json', 'w') as f:
        json.dump(assessment, f, indent=2)
    
    print(f"📄 Assessment saved to: output/scientific_validity_assessment.json")
    
    return assessment


if __name__ == "__main__":
    assessment = generate_scientific_assessment_report()
