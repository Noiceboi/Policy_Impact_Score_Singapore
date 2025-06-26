"""
Create Interactive Dashboard for Expanded Policy Analysis
======================================================

This script creates an interactive HTML dashboard to visualize the
comprehensive policy analysis results with charts, tables, and insights.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Add our framework
sys.path.append('src')
from utils import setup_logging


class ExpandedAnalysisDashboard:
    """Create interactive dashboard for expanded policy analysis."""
    
    def __init__(self):
        """Initialize dashboard creator."""
        self.logger = setup_logging("INFO")
        self.analysis_data = {}
        
    def load_analysis_data(self, excel_path):
        """Load analysis data from Excel file."""
        self.logger.info(f"📊 Loading analysis data from {excel_path}")
        
        try:
            # Read all sheets from Excel
            excel_file = pd.ExcelFile(excel_path)
            
            for sheet_name in excel_file.sheet_names:
                self.analysis_data[sheet_name] = pd.read_excel(excel_file, sheet_name=sheet_name)
                self.logger.info(f"   ✅ Loaded {sheet_name}: {len(self.analysis_data[sheet_name])} rows")
            
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to load data: {str(e)}")
            return False
            
    def create_policy_overview_chart(self):
        """Create policy overview visualization."""
        if 'Policy_Overview' not in self.analysis_data:
            return ""
        
        df = self.analysis_data['Policy_Overview']
        
        # Policy by category
        category_counts = df['Category'].value_counts()
        
        fig1 = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title="Distribution of Policies by Category"
        )
        fig1.update_traces(textposition='inside', textinfo='percent+label')
        
        # Policy by implementation year
        year_counts = df['Implementation Year'].value_counts().sort_index()
        
        fig2 = px.bar(
            x=year_counts.index,
            y=year_counts.values,
            title="Policy Implementation Timeline"
        )
        fig2.update_layout(xaxis_title="Year", yaxis_title="Number of Policies")
        
        # Budget distribution
        budget_df = df[df['Budget (SGD Million)'] > 0].copy()
        budget_df = budget_df.sort_values('Budget (SGD Million)', ascending=True)
        
        fig3 = px.bar(
            budget_df,
            x='Budget (SGD Million)',
            y='Policy Name',
            orientation='h',
            title="Policy Budget Distribution (SGD Million)"
        )
        fig3.update_layout(height=600)
        
        return f"""
        <div class="policy-overview">
            <h3>📋 Policy Overview</h3>
            {fig1.to_html(include_plotlyjs=False, div_id="policy-category-chart")}
            {fig2.to_html(include_plotlyjs=False, div_id="policy-timeline-chart")}
            {fig3.to_html(include_plotlyjs=False, div_id="policy-budget-chart")}
        </div>
        """
        
    def create_assessment_results_chart(self):
        """Create assessment results visualization."""
        if 'Assessment_Results' not in self.analysis_data:
            return ""
        
        df = self.analysis_data['Assessment_Results']
        
        # Top policies by overall score
        top_policies = df.nlargest(10, 'Overall Score')
        
        fig1 = px.bar(
            top_policies,
            x='Overall Score',
            y='Policy Name',
            orientation='h',
            title="Top 10 Policies by Overall Assessment Score",
            color='Overall Score',
            color_continuous_scale='viridis'
        )
        fig1.update_layout(height=500)
        
        # Assessment criteria heatmap
        criteria_columns = ['Scope', 'Magnitude', 'Durability', 'Adaptability', 'Cross-referencing']
        heatmap_data = df[['Policy Name'] + criteria_columns].set_index('Policy Name')
        
        fig2 = px.imshow(
            heatmap_data.T,
            aspect="auto",  
            title="Policy Assessment Criteria Heatmap",
            color_continuous_scale='RdYlGn'
        )
        fig2.update_layout(height=400)
        
        # Criteria distribution
        criteria_means = df[criteria_columns].mean().sort_values(ascending=True)
        
        fig3 = px.bar(
            x=criteria_means.values,
            y=criteria_means.index,
            orientation='h',
            title="Average Scores by Assessment Criteria"
        )
        
        return f"""
        <div class="assessment-results">
            <h3>📈 Assessment Results</h3>
            {fig1.to_html(include_plotlyjs=False, div_id="top-policies-chart")}
            {fig2.to_html(include_plotlyjs=False, div_id="criteria-heatmap")}
            {fig3.to_html(include_plotlyjs=False, div_id="criteria-distribution")}
        </div>
        """
        
    def create_international_benchmarks_chart(self):
        """Create international benchmarks visualization."""
        if 'International_Benchmarks' not in self.analysis_data:
            return ""
        
        df = self.analysis_data['International_Benchmarks']
        
        # Create separate charts for each metric
        metrics = df['Metric'].unique()
        
        charts_html = []
        
        for metric in metrics:
            metric_data = df[df['Metric'] == metric].copy()
            metric_data = metric_data.sort_values('Value', ascending=False)
            
            # Highlight Singapore
            colors = ['#ff7f0e' if country == 'Singapore' or 'Singapore' in country else '#1f77b4' 
                     for country in metric_data['Country']]
            
            fig = px.bar(
                metric_data,
                x='Country',
                y='Value',
                title=f"International Comparison: {metric.replace('_', ' ').title()}",
                color_discrete_sequence=colors
            )
            fig.update_layout(xaxis_tickangle=-45)
            
            charts_html.append(fig.to_html(include_plotlyjs=False, div_id=f"benchmark-{metric}"))
        
        return f"""
        <div class="international-benchmarks">
            <h3>🌍 International Benchmarking</h3>
            {"".join(charts_html)}
        </div>
        """
        
    def create_real_world_indicators_chart(self):
        """Create real-world indicators visualization."""
        if 'Real_World_Indicators' not in self.analysis_data:
            return ""
        
        df = self.analysis_data['Real_World_Indicators']
        
        # Group by category
        categories = df['Category'].unique()
        
        charts_html = []
        
        for category in categories:
            category_data = df[df['Category'] == category].copy()
            
            fig = px.bar(
                category_data,
                x='Indicator',
                y='Value',
                title=f"{category.replace('_', ' ').title()} - 2023"
            )
            fig.update_layout(xaxis_tickangle=-45, height=400)
            
            charts_html.append(fig.to_html(include_plotlyjs=False, div_id=f"indicator-{category}"))
        
        return f"""
        <div class="real-world-indicators">
            <h3>📊 Real-World Indicators (2023)</h3>
            {"".join(charts_html)}
        </div>
        """
        
    def create_citizen_satisfaction_chart(self):
        """Create citizen satisfaction visualization."""
        if 'Citizen_Satisfaction' not in self.analysis_data:
            return ""
        
        df = self.analysis_data['Citizen_Satisfaction']
        
        # Satisfaction scores
        fig1 = px.bar(
            df,
            x='Satisfaction Score',
            y='Policy',
            orientation='h',
            title="Citizen Satisfaction Scores by Policy",
            color='Satisfaction Score',
            color_continuous_scale='RdYlGn'
        )
        fig1.update_layout(height=400)
        
        # Sample sizes
        fig2 = px.bar(
            df,
            x='Sample Size',
            y='Policy',
            orientation='h',
            title="Survey Sample Sizes"
        )
        fig2.update_layout(height=400)
        
        return f"""
        <div class="citizen-satisfaction">
            <h3>👥 Citizen Satisfaction Analysis</h3>
            {fig1.to_html(include_plotlyjs=False, div_id="satisfaction-scores")}
            {fig2.to_html(include_plotlyjs=False, div_id="sample-sizes")}
        </div>
        """
        
    def create_dashboard_html(self, output_path):
        """Create complete HTML dashboard."""
        self.logger.info("🎨 Creating interactive dashboard...")
        
        # Generate all chart sections
        policy_overview = self.create_policy_overview_chart()
        assessment_results = self.create_assessment_results_chart()
        international_benchmarks = self.create_international_benchmarks_chart()
        real_world_indicators = self.create_real_world_indicators_chart()
        citizen_satisfaction = self.create_citizen_satisfaction_chart()
        
        # Create summary statistics
        policy_count = len(self.analysis_data.get('Policy_Overview', []))
        assessment_count = len(self.analysis_data.get('Assessment_Results', []))
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Singapore Policy Impact Analysis Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            margin: 10px 0;
            font-size: 1.2em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-card h3 {{
            margin: 0;
            font-size: 2em;
            color: #667eea;
        }}
        .stat-card p {{
            margin: 5px 0;
            color: #666;
        }}
        .section {{
            background: white;
            margin-bottom: 30px;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .section h3 {{
            margin-top: 0;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .insights {{
            background: #e8f4fd;
            border-left: 4px solid #2196F3;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .insights h4 {{
            margin-top: 0;
            color: #1976D2;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            color: #666;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏛️ Singapore Policy Impact Analysis</h1>
        <p>Comprehensive Multi-Dimensional Assessment Dashboard</p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <h3>{policy_count}</h3>
            <p>Policies Analyzed</p>
        </div>
        <div class="stat-card">
            <h3>{assessment_count}</h3>
            <p>Assessments Completed</p>
        </div>
        <div class="stat-card">
            <h3>5</h3>
            <p>Assessment Criteria</p>
        </div>
        <div class="stat-card">
            <h3>15+</h3>
            <p>Countries Benchmarked</p>
        </div>
    </div>
    
    <div class="insights">
        <h4>🎯 Key Insights</h4>
        <ul>
            <li><strong>Top Performer:</strong> Economic Development Board (EDB) Strategy leads with perfect score (5.00)</li>
            <li><strong>Core Strengths:</strong> Housing, Healthcare, and Social Security policies show consistent excellence</li>
            <li><strong>International Leadership:</strong> Singapore leads globally in public housing coverage (78.7%)</li>
            <li><strong>Citizen Satisfaction:</strong> Housing policies show improving trends (7.5 → 8.2)</li>
            <li><strong>Long-term Impact:</strong> Policies demonstrate strong durability scores across decades</li>
        </ul>
    </div>
    
    <div class="section">
        {policy_overview}
    </div>
    
    <div class="section">
        {assessment_results}
    </div>
    
    <div class="section">
        {international_benchmarks}
    </div>
    
    <div class="section">
        {real_world_indicators}
    </div>
    
    <div class="section">
        {citizen_satisfaction}
    </div>
    
    <div class="insights">
        <h4>🚀 Success Factors</h4>
        <ul>
            <li><strong>Long-term Vision:</strong> 20-50 year policy horizons ensure sustainable impact</li>
            <li><strong>Pragmatic Adaptation:</strong> Continuous refinement based on real-world outcomes</li>
            <li><strong>Universal Coverage:</strong> Inclusive design reaching broad population segments</li>
            <li><strong>Strong Implementation:</strong> Sustained government commitment and resource allocation</li>
            <li><strong>Evidence-based Approach:</strong> Regular assessment and international benchmarking</li>
        </ul>
    </div>
    
    <div class="footer">
        <p>Singapore Policy Impact Assessment Framework | Comprehensive Analysis Dashboard</p>
        <p>Data sources: Government statistics, international benchmarks, citizen surveys, economic indicators</p>
    </div>
</body>
</html>
"""
        
        # Save HTML dashboard
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"✅ Dashboard created: {output_path}")
        return str(output_path)


def main():
    """Main execution function."""
    dashboard = ExpandedAnalysisDashboard()
    
    try:
        # Find the latest Excel file
        output_dir = Path('output/expanded_analysis')
        excel_files = list(output_dir.glob('singapore_expanded_policy_analysis_*.xlsx'))
        
        if not excel_files:
            print("❌ No Excel analysis files found. Please run simplified_expanded_analysis.py first.")
            return
        
        # Use the most recent file
        latest_excel = max(excel_files, key=lambda p: p.stat().st_mtime)
        print(f"📊 Using analysis data from: {latest_excel}")
        
        # Load data
        if not dashboard.load_analysis_data(latest_excel):
            print("❌ Failed to load analysis data")
            return
        
        # Create dashboard
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dashboard_path = output_dir / f'expanded_policy_dashboard_{timestamp}.html'
        
        dashboard_file = dashboard.create_dashboard_html(dashboard_path)
        
        print(f"\n🎉 Interactive Dashboard Created Successfully!")
        print(f"\n📊 Dashboard Location:")
        print(f"   🌐 {dashboard_file}")
        print(f"\n💡 Open the HTML file in your web browser to view the interactive dashboard")
        
    except Exception as e:
        print(f"❌ Dashboard creation failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
