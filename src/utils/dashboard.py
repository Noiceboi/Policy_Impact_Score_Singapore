"""
Dashboard generation utilities for the Policy Impact Assessment Framework.

This module provides utilities for generating interactive dashboards
and visualizations for policy impact data.
"""

from typing import Dict, List, Optional, Any, Union
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DashboardGenerator:
    """
    Utility class for generating interactive dashboards.
    
    This class provides methods to create HTML dashboards with interactive
    charts and visualizations for policy impact data.
    """
    
    def __init__(self, template_dir: Optional[Path] = None):
        """
        Initialize the dashboard generator.
        
        Args:
            template_dir: Directory containing dashboard templates
        """
        self.template_dir = template_dir or Path("templates")
        self.charts_config = self._load_default_charts_config()
    
    def _load_default_charts_config(self) -> Dict[str, Any]:
        """Load default configuration for charts."""
        return {
            "category_chart": {
                "type": "doughnut",
                "options": {
                    "responsive": True,
                    "maintainAspectRatio": False,
                    "plugins": {
                        "legend": {
                            "position": "bottom"
                        }
                    }
                }
            },
            "timeline_chart": {
                "type": "line",
                "options": {
                    "responsive": True,
                    "maintainAspectRatio": False,
                    "scales": {
                        "y": {
                            "beginAtZero": True
                        }
                    }
                }
            },
            "dimensions_chart": {
                "type": "radar",
                "options": {
                    "responsive": True,
                    "maintainAspectRatio": False,
                    "scales": {
                        "r": {
                            "beginAtZero": True,
                            "max": 5
                        }
                    }
                }
            }
        }
    
    def generate_dashboard_data(
        self, 
        policies_df: pd.DataFrame, 
        assessments_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Generate dashboard data from policy and assessment dataframes.
        
        Args:
            policies_df: DataFrame containing policy data
            assessments_df: DataFrame containing assessment data
            
        Returns:
            Dictionary containing processed dashboard data
        """
        try:
            # Merge policies and assessments
            merged_df = pd.merge(
                policies_df, 
                assessments_df, 
                left_on='id', 
                right_on='policy_id', 
                how='left'
            )
            
            # Generate statistics
            stats = self._generate_statistics(merged_df)
            
            # Generate chart data
            chart_data = {
                'category_data': self._generate_category_data(merged_df),
                'timeline_data': self._generate_timeline_data(merged_df),
                'dimensions_data': self._generate_dimensions_data(merged_df),
                'verification_data': self._generate_verification_data(merged_df),
                'heatmap_data': self._generate_heatmap_data(merged_df)
            }
            
            # Generate table data
            table_data = self._generate_table_data(merged_df)
            
            return {
                'statistics': stats,
                'charts': chart_data,
                'table': table_data,
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'total_policies': len(policies_df),
                    'total_assessments': len(assessments_df)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating dashboard data: {e}")
            raise
    
    def _generate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate key statistics for the dashboard."""
        verified_count = df[df['validation_status'] == 'validated'].shape[0]
        avg_score = df['overall_score'].mean() if 'overall_score' in df.columns else 0
        
        return {
            'total_policies': df.shape[0],
            'verified_policies': verified_count,
            'avg_impact_score': round(avg_score, 2),
            'verification_rate': round((verified_count / df.shape[0]) * 100, 1) if df.shape[0] > 0 else 0
        }
    
    def _generate_category_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate data for category chart."""
        if 'category' not in df.columns:
            return {'labels': [], 'data': []}
        
        category_counts = df['category'].value_counts()
        return {
            'labels': category_counts.index.tolist(),
            'data': category_counts.values.tolist()
        }
    
    def _generate_timeline_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate data for timeline chart."""
        if 'implementation_year' not in df.columns:
            return {'labels': [], 'data': []}
        
        year_counts = df['implementation_year'].value_counts().sort_index()
        return {
            'labels': year_counts.index.tolist(),
            'data': year_counts.values.tolist()
        }
    
    def _generate_dimensions_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate data for dimensions radar chart."""
        dimensions = ['scope', 'magnitude', 'durability', 'adaptability', 'cross_referencing']
        
        dimension_data = []
        for dim in dimensions:
            if dim in df.columns:
                avg_score = df[dim].mean()
                dimension_data.append(round(avg_score, 2))
            else:
                dimension_data.append(0)
        
        return {
            'labels': ['Scope', 'Magnitude', 'Durability', 'Adaptability', 'Cross-referencing'],
            'data': dimension_data
        }
    
    def _generate_verification_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate data for verification status chart."""
        if 'validation_status' not in df.columns:
            return {'labels': [], 'data': []}
        
        status_counts = df['validation_status'].value_counts()
        return {
            'labels': status_counts.index.tolist(),
            'data': status_counts.values.tolist()
        }
    
    def _generate_heatmap_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate data for international validation heatmap."""
        # This would typically come from international validation data
        # For now, generate sample data structure
        policies = df['name'].head(10).tolist() if 'name' in df.columns else []
        organizations = ['World Bank', 'OECD', 'IMF', 'UN-HABITAT', 'Asian Development Bank']
        
        # Generate sample scores (in practice, this would come from real data)
        import random
        random.seed(42)  # For reproducible sample data
        
        z_data = []
        for _ in policies:
            row = []
            for _ in organizations:
                row.append(round(random.uniform(2.0, 5.0), 1))
            z_data.append(row)
        
        return {
            'policies': policies,
            'organizations': organizations,
            'scores': z_data
        }
    
    def _generate_table_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate data for the policies table."""
        table_columns = ['name', 'category', 'implementation_year', 'overall_score', 'validation_status']
        
        table_data = []
        for _, row in df.iterrows():
            table_row = {}
            for col in table_columns:
                if col in df.columns:
                    value = row[col]
                    # Handle different data types
                    if pd.isna(value):
                        table_row[col] = None
                    elif col == 'overall_score':
                        table_row[col] = round(float(value), 2) if value else None
                    elif col == 'implementation_year':
                        table_row[col] = int(value) if value else None
                    else:
                        table_row[col] = str(value)
                else:
                    table_row[col] = None
            
            table_data.append(table_row)
        
        return table_data
    
    def export_dashboard_data(
        self, 
        dashboard_data: Dict[str, Any], 
        output_path: Path
    ) -> None:
        """
        Export dashboard data to JSON file.
        
        Args:
            dashboard_data: Dashboard data dictionary
            output_path: Path to save the JSON file
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Dashboard data exported to {output_path}")
            
        except Exception as e:
            logger.error(f"Error exporting dashboard data: {e}")
            raise
    
    def validate_dashboard_data(self, dashboard_data: Dict[str, Any]) -> bool:
        """
        Validate dashboard data structure.
        
        Args:
            dashboard_data: Dashboard data to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_keys = ['statistics', 'charts', 'table', 'metadata']
        
        for key in required_keys:
            if key not in dashboard_data:
                logger.error(f"Missing required key: {key}")
                return False
        
        # Validate statistics
        stats = dashboard_data['statistics']
        required_stats = ['total_policies', 'verified_policies', 'avg_impact_score']
        for stat in required_stats:
            if stat not in stats:
                logger.error(f"Missing required statistic: {stat}")
                return False
        
        # Validate charts
        charts = dashboard_data['charts']
        required_charts = ['category_data', 'timeline_data', 'dimensions_data']
        for chart in required_charts:
            if chart not in charts:
                logger.error(f"Missing required chart: {chart}")
                return False
        
        logger.info("Dashboard data validation passed")
        return True


class ChartStyler:
    """Utility class for styling dashboard charts."""
    
    @staticmethod
    def get_color_palette(palette_name: str = "default") -> List[str]:
        """
        Get color palette for charts.
        
        Args:
            palette_name: Name of the color palette
            
        Returns:
            List of color hex codes
        """
        palettes = {
            "default": [
                '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
                '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
            ],
            "singapore": [
                '#ED1C24', '#FFFFFF', '#0072CE', '#00A651',
                '#FFF200', '#FF6900', '#6A1B9A', '#00ACC1'
            ],
            "professional": [
                '#2C5282', '#4299E1', '#68D391', '#F6E05E',
                '#FC8181', '#B794F6', '#63B3ED', '#81C784'
            ]
        }
        
        return palettes.get(palette_name, palettes["default"])
    
    @staticmethod
    def get_chart_options(chart_type: str) -> Dict[str, Any]:
        """
        Get chart options for different chart types.
        
        Args:
            chart_type: Type of chart
            
        Returns:
            Chart options dictionary
        """
        options = {
            "doughnut": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {
                        "position": "bottom",
                        "labels": {
                            "padding": 20,
                            "usePointStyle": True
                        }
                    }
                }
            },
            "line": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {
                        "display": False
                    }
                },
                "scales": {
                    "y": {
                        "beginAtZero": True
                    }
                }
            },
            "radar": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {
                        "display": False
                    }
                },
                "scales": {
                    "r": {
                        "beginAtZero": True,
                        "max": 5
                    }
                }
            },
            "bar": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {
                        "display": False
                    }
                },
                "scales": {
                    "y": {
                        "beginAtZero": True
                    }
                }
            }
        }
        
        return options.get(chart_type, {})


# Utility functions for dashboard creation
def create_dashboard_from_files(
    policies_file: Union[str, Path],
    assessments_file: Union[str, Path],
    output_dir: Union[str, Path]
) -> Dict[str, Any]:
    """
    Create dashboard data from CSV files.
    
    Args:
        policies_file: Path to policies CSV file
        assessments_file: Path to assessments CSV file
        output_dir: Directory to save dashboard data
        
    Returns:
        Dashboard data dictionary
    """
    try:
        # Load data
        policies_df = pd.read_csv(policies_file)
        assessments_df = pd.read_csv(assessments_file)
        
        # Generate dashboard
        generator = DashboardGenerator()
        dashboard_data = generator.generate_dashboard_data(policies_df, assessments_df)
        
        # Validate data
        if not generator.validate_dashboard_data(dashboard_data):
            raise ValueError("Dashboard data validation failed")
        
        # Export data
        output_path = Path(output_dir) / "dashboard_data.json"
        generator.export_dashboard_data(dashboard_data, output_path)
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Error creating dashboard from files: {e}")
        raise


def update_dashboard_html(
    dashboard_data: Dict[str, Any],
    template_path: Union[str, Path],
    output_path: Union[str, Path]
) -> None:
    """
    Update dashboard HTML file with new data.
    
    Args:
        dashboard_data: Dashboard data dictionary
        template_path: Path to HTML template
        output_path: Path to save updated HTML
    """
    try:
        # Read template
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Replace data placeholder
        data_json = json.dumps(dashboard_data, indent=2)
        html_content = html_content.replace(
            '// DASHBOARD_DATA_PLACEHOLDER',
            f'const dashboardData = {data_json};'
        )
        
        # Write updated HTML
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Dashboard HTML updated: {output_path}")
        
    except Exception as e:
        logger.error(f"Error updating dashboard HTML: {e}")
        raise
