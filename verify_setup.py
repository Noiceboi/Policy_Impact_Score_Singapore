#!/usr/bin/env python3
"""
Singapore Policy Impact Assessment Framework - Setup Verification Script
Verifies that all essential components are in place for deployment
"""

import os
import json
from pathlib import Path

def check_file_exists(filepath, description=""):
    """Check if a file exists and return status"""
    exists = Path(filepath).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {filepath}" + (f" ({description})" if description else ""))
    return exists

def check_directory_exists(dirpath, description=""):
    """Check if a directory exists and return status"""
    exists = Path(dirpath).is_dir()
    status = "✅" if exists else "❌"
    print(f"{status} {dirpath}/" + (f" ({description})" if description else ""))
    return exists

def verify_setup():
    """Main verification function"""
    print("🔍 Singapore Policy Impact Assessment Framework - Setup Verification\n")
    print("=" * 70)
    
    # Track overall status
    all_critical_files = True
    
    # 1. Core Framework Files
    print("\n📁 CORE FRAMEWORK FILES")
    print("-" * 30)
    core_files = [
        ("src/models.py", "Policy and assessment models"),
        ("src/framework.py", "Main MCDA framework"),
        ("src/analysis.py", "Statistical analysis"),
        ("src/visualization.py", "Chart generation"),
        ("src/utils.py", "Utility functions"),
        ("src/cross_reference.py", "Cross-validation"),
        ("main.py", "Main analysis script"),
        ("requirements.txt", "Python dependencies")
    ]
    
    for filepath, desc in core_files:
        if not check_file_exists(filepath, desc):
            all_critical_files = False
    
    # 2. GitHub Pages Website Files
    print("\n🌐 GITHUB PAGES WEBSITE")
    print("-" * 30)
    website_files = [
        ("docs/index.html", "Main homepage"),
        ("docs/pages/methodology.html", "Methodology page"),
        ("docs/pages/dashboard.html", "Interactive dashboard"),
        ("docs/pages/findings.html", "Research findings"),
        ("docs/pages/validation.html", "Scientific validation"),
        ("docs/pages/data-sources.html", "Data sources"),
        ("docs/assets/css/main.css", "Main stylesheet"),
        ("docs/assets/js/main.js", "JavaScript functionality"),
        ("docs/_config.yml", "Jekyll configuration"),
        ("docs/README.md", "Documentation README")
    ]
    
    for filepath, desc in website_files:
        if not check_file_exists(filepath, desc):
            all_critical_files = False
    
    # 3. Data and Templates
    print("\n📊 DATA & TEMPLATES")
    print("-" * 30)
    data_files = [
        ("data/sample_policies.csv", "Sample policy data"),
        ("data/sample_assessments.csv", "Sample assessments"),
        ("templates/singapore_policies_template.csv", "Policy template"),
        ("templates/singapore_assessments_template.csv", "Assessment template")
    ]
    
    for filepath, desc in data_files:
        check_file_exists(filepath, desc)
    
    # 4. Analysis Scripts
    print("\n🔬 ANALYSIS SCRIPTS")
    print("-" * 30)
    analysis_files = [
        ("enhanced_international_validation.py", "International validation"),
        ("comprehensive_policy_research.py", "Policy research"),
        ("create_expanded_dashboard.py", "Dashboard generator"),
        ("data_validation_audit.py", "Data validation"),
        ("scientific_validity_check.py", "Scientific rigor check")
    ]
    
    for filepath, desc in analysis_files:
        check_file_exists(filepath, desc)
    
    # 5. Reports and Documentation
    print("\n📋 REPORTS & DOCUMENTATION")
    print("-" * 30)
    report_files = [
        ("ENHANCED_INTERNATIONAL_VALIDATION_REPORT.md", "International validation report"),
        ("FINAL_SCIENTIFIC_VALIDITY_REPORT.md", "Scientific validity report"),
        ("SCIENTIFIC_RIGOR_ASSESSMENT.md", "Rigor assessment"),
        ("GITHUB_PAGES_SETUP.md", "Deployment guide"),
        ("README.md", "Main documentation")
    ]
    
    for filepath, desc in report_files:
        check_file_exists(filepath, desc)
    
    # 6. Output Directory Structure
    print("\n📁 OUTPUT DIRECTORIES")
    print("-" * 30)
    output_dirs = [
        ("output", "Main output directory"),
        ("output/expanded_analysis", "Expanded analysis results"),
        ("output/comprehensive_policy_research", "Policy research results"),
        ("output/cross_study_analysis", "Cross-study analysis")
    ]
    
    for dirpath, desc in output_dirs:
        check_directory_exists(dirpath, desc)
    
    # 7. Check for Key Output Files
    print("\n📄 KEY OUTPUT FILES")
    print("-" * 30)
    output_files = [
        ("output/enhanced_transparency_validation_report.json", "Transparency validation"),
        ("output/scientific_validity_assessment.json", "Scientific validity"),
        ("output/summary_report.json", "Summary report")
    ]
    
    for filepath, desc in output_files:
        check_file_exists(filepath, desc)
    
    # 8. Deployment Files
    print("\n🚀 DEPLOYMENT FILES")
    print("-" * 30)
    deployment_files = [
        ("setup_github_pages.sh", "Automated setup script")
    ]
    
    for filepath, desc in deployment_files:
        check_file_exists(filepath, desc)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SETUP VERIFICATION SUMMARY")
    print("=" * 70)
    
    if all_critical_files:
        print("🎉 SUCCESS: All critical framework files are present!")
        print("✅ Your Singapore Policy Impact Assessment Framework is ready for deployment.")
        print("\n📋 NEXT STEPS:")
        print("1. Update repository URLs in HTML files")
        print("2. Replace 'yourusername' with your GitHub username")
        print("3. Push to GitHub and enable Pages in Settings")
        print("4. Access your site at: https://yourusername.github.io/Policy_Impact_Score_Singapore/")
    else:
        print("⚠️  WARNING: Some critical files are missing!")
        print("❌ Please ensure all core framework files are present before deployment.")
    
    # Additional Statistics
    print(f"\n📈 FRAMEWORK STATISTICS:")
    
    # Count Python files
    python_files = list(Path(".").rglob("*.py"))
    print(f"📝 Python files: {len(python_files)}")
    
    # Count HTML files
    html_files = list(Path("docs").rglob("*.html")) if Path("docs").exists() else []
    print(f"🌐 HTML pages: {len(html_files)}")
    
    # Count Markdown files
    md_files = list(Path(".").rglob("*.md"))
    print(f"📄 Documentation files: {len(md_files)}")
    
    # Count output files
    output_files_count = len(list(Path("output").rglob("*"))) if Path("output").exists() else 0
    print(f"📊 Generated output files: {output_files_count}")
    
    print(f"\n🎯 Framework Status: {'READY FOR DEPLOYMENT' if all_critical_files else 'SETUP INCOMPLETE'}")
    print("=" * 70)
    
    return all_critical_files

if __name__ == "__main__":
    verify_setup()
