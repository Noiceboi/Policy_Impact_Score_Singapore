<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Copilot Instructions for Policy Impact Assessment Framework

## Project Context
This is a Python-based framework for assessing the impact of Singaporean government policies. The framework evaluates policies across multiple dimensions and provides time-series analysis capabilities.

## Key Components
- **Policy Categories**: 10 predefined categories in Vietnamese terms (An sinh xã hội, Giữ gìn trật tự đô thị, etc.)
- **Assessment Criteria**: 5-point scale across 5 dimensions (Scope, Magnitude, Durability, Adaptability, Cross-referencing)
- **Weighted Scoring**: Configurable weights for different criteria
- **Time-series Analysis**: Track policy evolution over time
- **Data Visualization**: Interactive charts and reports

## Coding Guidelines
- Use pandas for data manipulation and analysis
- Implement matplotlib/plotly for visualizations
- Follow object-oriented design patterns for policy models
- Include comprehensive docstrings with parameter types
- Use type hints for better code clarity
- Implement error handling for data validation
- Create modular, reusable components

## Data Structures
- Policy objects should include: name, category, implementation_year, scores, metadata
- Assessment results should be stored with timestamps and versioning
- Support for historical data import/export in CSV/JSON formats

## Analysis Focus
- Emphasize long-term impact assessment (higher weight on durability)
- Support comparative analysis between policies
- Enable trend analysis and forecasting
- Provide statistical significance testing for impact claims

## Visualization Requirements
- Interactive dashboards for policy comparison
- Time-series plots for policy evolution
- Heatmaps for category-wise impact analysis
- Export capabilities for reports and presentations
