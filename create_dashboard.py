"""
Interactive Cross-Study Dashboard Generator
==========================================

This script creates an interactive HTML dashboard showing all cross-study
comparison tables and validation results for Singapore policy assessment.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
from pathlib import Path
import json
from datetime import datetime

def create_interactive_dashboard():
    """Create comprehensive interactive dashboard for cross-study analysis."""
    
    print("🎨 Creating Interactive Cross-Study Dashboard...")
    
    # Load latest analysis data
    output_dir = Path('output/cross_study_analysis')
    
    # Find most recent files (with timestamp)
    files = list(output_dir.glob('*_20250626_003826.*'))
    if not files:
        print("❌ No recent analysis files found. Please run simple_cross_study_analysis.py first.")
        return
    
    # Load data
    category_matrix = pd.read_csv(output_dir / 'policy_category_matrix_20250626_003826.csv')
    integrity_report = pd.read_csv(output_dir / 'data_integrity_report_20250626_003826.csv')
    time_series = pd.read_csv(output_dir / 'time_series_analysis_20250626_003826.csv')
    benchmarks = pd.read_csv(output_dir / 'international_benchmarks_20250626_003826.csv')
    success_factors = pd.read_csv(output_dir / 'success_factor_analysis_20250626_003826.csv')
    economic_impact = pd.read_csv(output_dir / 'economic_impact_analysis_20250626_003826.csv')
    
    with open(output_dir / 'comprehensive_summary_20250626_003826.json', 'r', encoding='utf-8') as f:
        summary = json.load(f)
    
    # Create dashboard with multiple subplots
    fig = make_subplots(
        rows=4, cols=2,
        subplot_titles=(
            '🏛️ Policy Category Performance Matrix',
            '🔍 Data Integrity by Policy',
            '📈 Time Series: Policy Effectiveness Over Time',
            '🌍 International Benchmarks Comparison',
            '🎯 Success Factor Distribution',
            '💰 Economic Impact vs Policy Score',
            '📊 Category-wise Performance Summary',
            '⭐ Top Performing Policies'
        ),
        specs=[
            [{"type": "bar"}, {"type": "scatter"}],
            [{"type": "scatter"}, {"type": "bar"}],
            [{"type": "pie"}, {"type": "scatter"}],
            [{"type": "bar"}, {"type": "table"}]
        ],
        vertical_spacing=0.08,
        horizontal_spacing=0.1
    )
    
    # 1. Policy Category Performance Matrix
    fig.add_trace(
        go.Bar(
            x=category_matrix['policy_name'],
            y=category_matrix['Overall Impact Score'],
            text=category_matrix['category'],
            textposition='auto',
            name='Impact Score',
            marker=dict(
                color=category_matrix['Overall Impact Score'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Impact Score", x=0.45)
            ),
            hovertemplate='<b>%{x}</b><br>Category: %{text}<br>Impact Score: %{y}<br><extra></extra>'
        ),
        row=1, col=1
    )
    
    # 2. Data Integrity Scatter Plot
    integrity_colors = {'High': 'green', 'Medium': 'orange', 'Low': 'red'}
    fig.add_trace(
        go.Scatter(
            x=integrity_report['Assessment Count'],
            y=integrity_report['Overall Integrity Score'],
            mode='markers+text',
            text=integrity_report['Policy Name'],
            textposition='top center',
            marker=dict(
                size=12,
                color=[integrity_colors[level] for level in integrity_report['Data Quality Level']],
                line=dict(width=2, color='white')
            ),
            name='Data Integrity',
            hovertemplate='<b>%{text}</b><br>Assessments: %{x}<br>Integrity Score: %{y}<br><extra></extra>'
        ),
        row=1, col=2
    )
    
    # 3. Time Series Analysis
    time_series['Assessment Date'] = pd.to_datetime(time_series['Assessment Date'])
    categories = time_series['Category'].unique()
    
    for i, category in enumerate(categories):
        cat_data = time_series[time_series['Category'] == category]
        fig.add_trace(
            go.Scatter(
                x=cat_data['Assessment Date'],
                y=cat_data['Overall Score'],
                mode='lines+markers',
                name=f'{category}',
                line=dict(width=2),
                marker=dict(size=8),
                hovertemplate='<b>%{text}</b><br>Date: %{x}<br>Score: %{y}<br><extra></extra>',
                text=cat_data['Policy Name']
            ),
            row=2, col=1
        )
    
    # 4. International Benchmarks
    fig.add_trace(
        go.Bar(
            x=benchmarks['Category'],
            y=benchmarks['Singapore Average Score'],
            name='Singapore',
            marker_color='red',
            yaxis='y4',
            offsetgroup=1
        ),
        row=2, col=2
    )
    
    fig.add_trace(
        go.Bar(
            x=benchmarks['Category'],
            y=benchmarks['OECD Average'],
            name='OECD Average',
            marker_color='blue',
            yaxis='y4',
            offsetgroup=2
        ),
        row=2, col=2
    )
    
    fig.add_trace(
        go.Bar(
            x=benchmarks['Category'],
            y=benchmarks['Global Best Practice'],
            name='Global Best',
            marker_color='green',
            yaxis='y4',
            offsetgroup=3
        ),
        row=2, col=2
    )
    
    # 5. Success Factor Distribution
    success_counts = success_factors['Success Level'].value_counts()
    fig.add_trace(
        go.Pie(
            labels=success_counts.index,
            values=success_counts.values,
            name="Success Distribution",
            marker=dict(colors=['#ff9999', '#66b3ff', '#99ff99']),
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<br><extra></extra>'
        ),
        row=3, col=1
    )
    
    # 6. Economic Impact vs Policy Score
    fig.add_trace(
        go.Scatter(
            x=economic_impact['Policy Impact Score'],
            y=economic_impact['Economic Efficiency Score'],
            mode='markers+text',
            text=economic_impact['Policy Name'],
            textposition='top center',
            marker=dict(
                size=12,
                color=economic_impact['GDP Impact (%)'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="GDP Impact (%)", x=1.02)
            ),
            name='Economic Correlation',
            hovertemplate='<b>%{text}</b><br>Policy Score: %{x}<br>Economic Efficiency: %{y}<br><extra></extra>'
        ),
        row=3, col=2
    )
    
    # 7. Category Performance Summary
    category_summary = category_matrix.groupby('category')['Overall Impact Score'].mean().sort_values(ascending=True)
    fig.add_trace(
        go.Bar(
            y=category_summary.index,
            x=category_summary.values,
            orientation='h',
            name='Category Average',
            marker=dict(color='lightblue'),
            text=category_summary.values.round(2),
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Average Score: %{x}<br><extra></extra>'
        ),
        row=4, col=1
    )
    
    # 8. Top Performing Policies Table
    top_policies = category_matrix.nlargest(5, 'Overall Impact Score')
    
    fig.add_trace(
        go.Table(
            header=dict(
                values=['Policy Name', 'Category', 'Impact Score', 'Data Quality'],
                fill_color='lightblue',
                align='left',
                font=dict(size=12)
            ),
            cells=dict(
                values=[
                    top_policies['policy_name'],
                    top_policies['category'],
                    top_policies['Overall Impact Score'],
                    top_policies['Data Quality']
                ],
                fill_color='white',
                align='left',
                font=dict(size=11)
            )
        ),
        row=4, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=1600,
        title=dict(
            text="🏛️ Singapore Policy Impact Assessment - Cross-Study Analysis Dashboard<br>" +
                 f"<sub>Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')} | " +
                 f"Policies: {summary['total_policies']} | Assessments: {summary['total_assessments']} | " +
                 f"Avg Impact: {summary['average_impact_score']}/5.0</sub>",
            x=0.5,
            font=dict(size=16)
        ),
        showlegend=True,
        legend=dict(x=1.05, y=1),
        font=dict(size=10)
    )
    
    # Update x-axis labels for better readability
    fig.update_xaxes(tickangle=45, row=1, col=1)
    fig.update_xaxes(tickangle=45, row=2, col=2)
    
    # Save dashboard
    dashboard_file = output_dir / f'interactive_cross_study_dashboard_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    
    # Add custom HTML content
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Singapore Policy Impact Assessment - Cross-Study Analysis</title>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 20px;
                text-align: center;
            }}
            .summary-stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 20px;
            }}
            .stat-card {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
            }}
            .stat-value {{
                font-size: 2em;
                font-weight: bold;
                color: #667eea;
            }}
            .stat-label {{
                font-size: 0.9em;
                color: #666;
                margin-top: 5px;
            }}
            .dashboard-container {{
                background: white;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .key-findings {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin-top: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .finding-item {{
                padding: 8px 0;
                border-left: 4px solid #667eea;
                padding-left: 15px;
                margin: 10px 0;
                background: #f8f9ff;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏛️ Singapore Policy Impact Assessment</h1>
            <h2>Cross-Study Analysis & Data Integrity Dashboard</h2>
            <p>Comprehensive analysis of {summary['total_policies']} Singapore government policies across {summary['data_coverage']['categories_covered']} categories</p>
        </div>
        
        <div class="summary-stats">
            <div class="stat-card">
                <div class="stat-value">{summary['total_policies']}</div>
                <div class="stat-label">Total Policies</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{summary['total_assessments']}</div>
                <div class="stat-label">Total Assessments</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{summary['high_integrity_policies']}</div>
                <div class="stat-label">High Integrity Policies</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{summary['average_impact_score']}/5.0</div>
                <div class="stat-label">Average Impact Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{round(summary['high_integrity_policies']/summary['total_policies']*100, 1)}%</div>
                <div class="stat-label">Data Integrity Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{summary['data_coverage']['assessor_organizations']}</div>
                <div class="stat-label">Independent Assessor Organizations</div>
            </div>
        </div>
        
        <div class="dashboard-container">
            {{plot_div}}
        </div>
        
        <div class="key-findings">
            <h3>🔍 Key Findings & Data Integrity Analysis</h3>
            {"".join([f'<div class="finding-item">• {finding}</div>' for finding in summary['key_findings']])}
            
            <h4>🏆 Top Performing Policies:</h4>
            {"".join([f'<div class="finding-item">• <strong>{policy["policy_name"]}</strong> ({policy["category"]}) - Score: {policy["Overall Impact Score"]}</div>' for policy in summary['top_performing_policies']])}
            
            <h4>📊 Data Sources & Validation:</h4>
            <div class="finding-item">• Official Singapore government data from multiple independent sources</div>
            <div class="finding-item">• Cross-validation with international benchmarks (OECD, Asian countries)</div>
            <div class="finding-item">• Time-series analysis spanning multiple decades of policy implementation</div>
            <div class="finding-item">• Multi-stakeholder assessment approach with diverse evaluator organizations</div>
            <div class="finding-item">• Comprehensive data integrity scoring based on consistency, coverage, and completeness</div>
        </div>
    </body>
    </html>
    """
    
    # Generate the plot HTML
    plot_html = pyo.plot(fig, output_type='div', include_plotlyjs=True)
    
    # Replace the plot div placeholder
    final_html = html_template.replace('{plot_div}', plot_html)
    
    # Save the complete dashboard
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print(f"🎯 Interactive dashboard created: {dashboard_file}")
    print(f"📊 Dashboard includes:")
    print(f"   • Policy Category Performance Matrix")
    print(f"   • Data Integrity Analysis")
    print(f"   • Time-series Effectiveness Tracking")
    print(f"   • International Benchmarks Comparison")
    print(f"   • Success Factor Distribution")
    print(f"   • Economic Impact Correlation")
    print(f"   • Category Performance Summary")
    print(f"   • Top Performing Policies Table")
    
    return dashboard_file

if __name__ == "__main__":
    dashboard_file = create_interactive_dashboard()
    print(f"\n✅ Cross-study dashboard ready!")
    print(f"🌐 Open the following file in your browser:")
    print(f"    {dashboard_file}")
    print("\n🎯 Dashboard Features:")
    print("    • Interactive charts and graphs")
    print("    • Cross-validation data integrity reports")
    print("    • International benchmark comparisons")
    print("    • Time-series policy effectiveness analysis")
    print("    • Multi-dimensional scoring matrices")
    print("    • Economic impact correlations")
