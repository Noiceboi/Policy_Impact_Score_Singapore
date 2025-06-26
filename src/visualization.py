"""
Data visualization module for policy impact assessment.

This module provides comprehensive visualization capabilities including
interactive charts, dashboards, and report generation for policy analysis.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from models import Policy, PolicyCollection, PolicyCategory


class PolicyVisualizer:
    """
    Visualization engine for policy impact assessment data.
    
    Provides various chart types and visualization options for policy
    analysis results, trends, and comparisons.
    """
    
    def __init__(self):
        """Initialize the visualizer with default styling."""
        # Set matplotlib style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Color schemes
        self.category_colors = {
            "An sinh xã hội": "#FF6B6B",
            "Giữ gìn trật tự đô thị": "#4ECDC4", 
            "Kinh tế tài chính": "#45B7D1",
            "Phúc lợi xã hội": "#96CEB4",
            "Thuế": "#FFEAA7",
            "An ninh quốc phòng": "#DDA0DD",
            "Văn hóa xã hội": "#98D8C8",
            "Giáo dục": "#F7DC6F",
            "Phát triển đô thị": "#BB8FCE",
            "Chăm sóc sức khỏe": "#85C1E9"
        }
    
    def create_policy_ranking_chart(
        self, 
        policies: PolicyCollection, 
        category: Optional[str] = None,
        top_n: int = 10,
        save_path: Optional[str] = None
    ) -> go.Figure:
        """
        Create a horizontal bar chart of policy rankings.
        
        Args:
            policies: PolicyCollection object
            category: Filter by category (optional)
            top_n: Number of top policies to show
            save_path: Path to save the chart (optional)
            
        Returns:
            Plotly figure object
        """
        # Get policy scores
        policy_scores = []
        
        policies_to_rank = policies.policies
        if category:
            policies_to_rank = policies.get_policies_by_category(category)
        
        for policy in policies_to_rank:
            latest_assessment = policy.get_latest_assessment()
            if latest_assessment:
                policy_scores.append({
                    'name': policy.name,
                    'score': latest_assessment.overall_score,
                    'category': policy.category_name
                })
        
        # Sort and limit
        policy_scores.sort(key=lambda x: x['score'], reverse=True)
        policy_scores = policy_scores[:top_n]
        
        if not policy_scores:
            raise ValueError("No policies with assessments found")
        
        # Create chart
        fig = go.Figure(data=go.Bar(
            y=[p['name'] for p in policy_scores],
            x=[p['score'] for p in policy_scores],
            orientation='h',
            marker_color=[self.category_colors.get(p['category'], '#636EFA') for p in policy_scores],
            text=[f"{p['score']:.2f}" for p in policy_scores],
            textposition='auto'
        ))
        
        title = f"Top {top_n} Policy Rankings"
        if category:
            title += f" - {category}"
        
        fig.update_layout(
            title=title,
            xaxis_title="Impact Score",
            yaxis_title="Policy",
            height=max(400, len(policy_scores) * 30),
            showlegend=False
        )
        
        if save_path:
            fig.write_html(save_path)
        
        return fig
    
    def create_category_heatmap(
        self, 
        policies: PolicyCollection,
        save_path: Optional[str] = None
    ) -> go.Figure:
        """
        Create a heatmap showing average scores by category and criteria.
        
        Args:
            policies: PolicyCollection object
            save_path: Path to save the chart (optional)
            
        Returns:
            Plotly figure object
        """
        # Prepare data
        category_data = {}
        
        for policy in policies.policies:
            latest_assessment = policy.get_latest_assessment()
            if not latest_assessment:
                continue
            
            category = policy.category_name
            if category not in category_data:
                category_data[category] = {
                    'scope': [],
                    'magnitude': [],
                    'durability': [],
                    'adaptability': [],
                    'cross_referencing': [],
                    'overall': []
                }
            
            criteria = latest_assessment.criteria
            category_data[category]['scope'].append(criteria.scope)
            category_data[category]['magnitude'].append(criteria.magnitude)
            category_data[category]['durability'].append(criteria.durability)
            category_data[category]['adaptability'].append(criteria.adaptability)
            category_data[category]['cross_referencing'].append(criteria.cross_referencing)
            category_data[category]['overall'].append(latest_assessment.overall_score)
        
        # Calculate averages
        heatmap_data = []
        categories = []
        criteria_names = ['Scope', 'Magnitude', 'Durability', 'Adaptability', 'Cross-referencing', 'Overall']
        
        for category, data in category_data.items():
            if not data['scope']:  # Skip empty categories
                continue
            
            categories.append(category)
            row = [
                np.mean(data['scope']),
                np.mean(data['magnitude']),
                np.mean(data['durability']),
                np.mean(data['adaptability']),
                np.mean(data['cross_referencing']),
                np.mean(data['overall'])
            ]
            heatmap_data.append(row)
        
        if not heatmap_data:
            raise ValueError("No assessment data found for heatmap")
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=criteria_names,
            y=categories,
            colorscale='RdYlBu_r',
            text=[[f"{val:.2f}" for val in row] for row in heatmap_data],
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title="Policy Impact Heatmap by Category and Criteria",
            xaxis_title="Assessment Criteria",
            yaxis_title="Policy Category",
            height=max(400, len(categories) * 50)
        )
        
        if save_path:
            fig.write_html(save_path)
        
        return fig
    
    def create_time_series_chart(
        self, 
        policy: Policy,
        save_path: Optional[str] = None
    ) -> go.Figure:
        """
        Create a time series chart for policy evolution.
        
        Args:
            policy: Policy object to visualize
            save_path: Path to save the chart (optional)
            
        Returns:
            Plotly figure object
        """
        if len(policy.assessments) < 2:
            raise ValueError("At least 2 assessments required for time series")
        
        # Sort assessments by date
        assessments = sorted(policy.assessments, key=lambda x: x.assessment_date)
        
        dates = [a.assessment_date for a in assessments]
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Overall Impact Score', 'Individual Criteria Scores'),
            vertical_spacing=0.1
        )
        
        # Overall score
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=[a.overall_score for a in assessments],
                mode='lines+markers',
                name='Overall Score',
                line=dict(width=3),
                marker=dict(size=8)
            ),
            row=1, col=1
        )
        
        # Individual criteria
        criteria_data = {
            'Scope': [a.criteria.scope for a in assessments],
            'Magnitude': [a.criteria.magnitude for a in assessments],
            'Durability': [a.criteria.durability for a in assessments],
            'Adaptability': [a.criteria.adaptability for a in assessments],
            'Cross-referencing': [a.criteria.cross_referencing for a in assessments]
        }
        
        for criterion, scores in criteria_data.items():
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=scores,
                    mode='lines+markers',
                    name=criterion,
                    opacity=0.7
                ),
                row=2, col=1
            )
        
        fig.update_layout(
            title=f"Policy Evolution: {policy.name}",
            height=600,
            showlegend=True
        )
        
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Score", range=[0, 5])
        
        if save_path:
            fig.write_html(save_path)
        
        return fig
    
    def create_radar_chart(
        self, 
        policies: List[Policy],
        save_path: Optional[str] = None
    ) -> go.Figure:
        """
        Create a radar chart comparing policies across criteria.
        
        Args:
            policies: List of policies to compare
            save_path: Path to save the chart (optional)
            
        Returns:
            Plotly figure object
        """
        if not policies:
            raise ValueError("No policies provided for radar chart")
        
        criteria_names = ['Scope', 'Magnitude', 'Durability', 'Adaptability', 'Cross-referencing']
        
        fig = go.Figure()
        
        for policy in policies:
            latest_assessment = policy.get_latest_assessment()
            if not latest_assessment:
                continue
            
            criteria = latest_assessment.criteria
            values = [
                criteria.scope,
                criteria.magnitude,
                criteria.durability,
                criteria.adaptability,
                criteria.cross_referencing
            ]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=criteria_names,
                fill='toself',
                name=policy.name,
                opacity=0.6
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5]
                )
            ),
            title="Policy Comparison - Radar Chart",
            showlegend=True
        )
        
        if save_path:
            fig.write_html(save_path)
        
        return fig
    
    def create_distribution_plot(
        self, 
        policies: PolicyCollection,
        criterion: str = 'overall',
        save_path: Optional[str] = None
    ) -> go.Figure:
        """
        Create a distribution plot for policy scores.
        
        Args:
            policies: PolicyCollection object
            criterion: Criterion to plot ('overall', 'scope', 'magnitude', etc.)
            save_path: Path to save the chart (optional)
            
        Returns:
            Plotly figure object
        """
        scores = []
        categories = []
        
        for policy in policies.policies:
            latest_assessment = policy.get_latest_assessment()
            if not latest_assessment:
                continue
            
            if criterion == 'overall':
                score = latest_assessment.overall_score
            else:
                score = getattr(latest_assessment.criteria, criterion, None)
                if score is None:
                    continue
            
            scores.append(score)
            categories.append(policy.category_name)
        
        if not scores:
            raise ValueError(f"No data found for criterion: {criterion}")
        
        # Create box plot by category
        fig = go.Figure()
        
        unique_categories = list(set(categories))
        for category in unique_categories:
            category_scores = [s for s, c in zip(scores, categories) if c == category]
            
            fig.add_trace(go.Box(
                y=category_scores,
                name=category,
                marker_color=self.category_colors.get(category, '#636EFA')
            ))
        
        fig.update_layout(
            title=f"Score Distribution by Category - {criterion.title()}",
            yaxis_title="Score",
            xaxis_title="Policy Category",
            showlegend=False
        )
        
        if save_path:
            fig.write_html(save_path)
        
        return fig
    
    def create_correlation_matrix(
        self, 
        policies: PolicyCollection,
        save_path: Optional[str] = None
    ) -> go.Figure:
        """
        Create a correlation matrix for assessment criteria.
        
        Args:
            policies: PolicyCollection object
            save_path: Path to save the chart (optional)
            
        Returns:
            Plotly figure object
        """
        # Prepare data
        data = []
        for policy in policies.policies:
            latest_assessment = policy.get_latest_assessment()
            if not latest_assessment:
                continue
            
            criteria = latest_assessment.criteria
            data.append({
                'scope': criteria.scope,
                'magnitude': criteria.magnitude,
                'durability': criteria.durability,
                'adaptability': criteria.adaptability,
                'cross_referencing': criteria.cross_referencing,
                'overall': latest_assessment.overall_score
            })
        
        if not data:
            raise ValueError("No assessment data found for correlation matrix")
        
        df = pd.DataFrame(data)
        correlation_matrix = df.corr()
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=correlation_matrix.round(2).values,
            texttemplate="%{text}",
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            title="Correlation Matrix - Assessment Criteria",
            width=600,
            height=600
        )
        
        if save_path:
            fig.write_html(save_path)
        
        return fig
    
    def create_dashboard(
        self, 
        policies: PolicyCollection,
        output_dir: str = "dashboard"
    ) -> str:
        """
        Create a comprehensive dashboard with multiple visualizations.
        
        Args:
            policies: PolicyCollection object
            output_dir: Directory to save dashboard files
            
        Returns:
            Path to main dashboard HTML file
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Create individual charts
        charts = {}
        
        try:
            charts['ranking'] = self.create_policy_ranking_chart(policies)
            charts['ranking'].write_html(str(output_path / "ranking.html"))
        except Exception as e:
            print(f"Warning: Could not create ranking chart: {e}")
        
        try:
            charts['heatmap'] = self.create_category_heatmap(policies)
            charts['heatmap'].write_html(str(output_path / "heatmap.html"))
        except Exception as e:
            print(f"Warning: Could not create heatmap: {e}")
        
        try:
            charts['distribution'] = self.create_distribution_plot(policies)
            charts['distribution'].write_html(str(output_path / "distribution.html"))
        except Exception as e:
            print(f"Warning: Could not create distribution plot: {e}")
        
        try:
            charts['correlation'] = self.create_correlation_matrix(policies)
            charts['correlation'].write_html(str(output_path / "correlation.html"))
        except Exception as e:
            print(f"Warning: Could not create correlation matrix: {e}")
        
        # Create main dashboard HTML
        dashboard_html = self._create_dashboard_html(charts, policies)
        
        dashboard_path = output_path / "dashboard.html"
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(dashboard_html)
        
        return str(dashboard_path)
    
    def _create_dashboard_html(self, charts: Dict, policies: PolicyCollection) -> str:
        """Create main dashboard HTML with embedded charts."""
        # Get summary statistics
        total_policies = policies.total_policies
        categories_summary = policies.categories_summary
        
        assessed_policies = sum(1 for p in policies.policies if p.get_latest_assessment())
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Policy Impact Assessment Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 10px; }}
                .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .stat-box {{ background-color: #e8f4fd; padding: 15px; border-radius: 5px; text-align: center; }}
                .chart-container {{ margin: 30px 0; }}
                iframe {{ width: 100%; height: 600px; border: none; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Policy Impact Assessment Dashboard</h1>
                <p>Comprehensive analysis of Singaporean government policies across multiple dimensions.</p>
            </div>
            
            <div class="stats">
                <div class="stat-box">
                    <h3>{total_policies}</h3>
                    <p>Total Policies</p>
                </div>
                <div class="stat-box">
                    <h3>{assessed_policies}</h3>
                    <p>Assessed Policies</p>
                </div>
                <div class="stat-box">
                    <h3>{len(categories_summary)}</h3>
                    <p>Policy Categories</p>
                </div>
                <div class="stat-box">
                    <h3>{assessed_policies/total_policies*100:.1f}%</h3>
                    <p>Assessment Coverage</p>
                </div>
            </div>
        """
        
        # Add chart sections
        if 'ranking' in charts:
            html += """
            <div class="chart-container">
                <h2>Policy Rankings</h2>
                <iframe src="ranking.html"></iframe>
            </div>
            """
        
        if 'heatmap' in charts:
            html += """
            <div class="chart-container">
                <h2>Category Performance Heatmap</h2>
                <iframe src="heatmap.html"></iframe>
            </div>
            """
        
        if 'distribution' in charts:
            html += """
            <div class="chart-container">
                <h2>Score Distribution</h2>
                <iframe src="distribution.html"></iframe>
            </div>
            """
        
        if 'correlation' in charts:
            html += """
            <div class="chart-container">
                <h2>Criteria Correlation Matrix</h2>
                <iframe src="correlation.html"></iframe>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html
