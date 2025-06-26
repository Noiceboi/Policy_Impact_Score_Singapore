# Data Directory Documentation

This directory contains all data files used in the Policy Impact Assessment Framework.

## Directory Structure

```
data/
├── raw/                    # Original, unmodified data files
├── processed/              # Cleaned and processed data files
├── sample_policies.csv     # Sample policy data for testing
├── sample_assessments.csv  # Sample assessment data for testing
└── README.md              # This file
```

## Data Sources and Provenance

### Government Data Sources

#### Singapore Government Official Sources
- **Ministry of National Development (MND)**
  - URL: https://www.mnd.gov.sg/
  - Last accessed: 2024-12-26
  - License: Singapore Open Data License
  - Data extraction: Automated via API (where available)

- **Housing & Development Board (HDB)**
  - URL: https://www.hdb.gov.sg/
  - Last accessed: 2024-12-26
  - License: Singapore Open Data License
  - Focus: Housing policies and urban development

- **Ministry of Finance (MOF)**
  - URL: https://www.mof.gov.sg/
  - Last accessed: 2024-12-26
  - License: Singapore Open Data License
  - Focus: Economic and fiscal policies

- **Central Provident Fund Board (CPF)**
  - URL: https://www.cpf.gov.sg/
  - Last accessed: 2024-12-26
  - License: Singapore Open Data License
  - Focus: Social security and retirement policies

#### Data.gov.sg Portal
- **Primary Source**: https://data.gov.sg/
- **Last accessed**: 2024-12-26
- **License**: Singapore Open Data License
- **API Endpoints**: RESTful APIs for real-time data access
- **Update Frequency**: Monthly for policy data, weekly for statistics

### International Validation Sources

#### World Bank
- **Source**: World Bank Open Data
- **URL**: https://data.worldbank.org/
- **Last accessed**: 2024-12-26
- **License**: Creative Commons Attribution 4.0
- **Datasets Used**:
  - Government Effectiveness Index
  - Regulatory Quality Index
  - Rule of Law Index

#### OECD
- **Source**: OECD Data Portal
- **URL**: https://data.oecd.org/
- **Last accessed**: 2024-12-26
- **License**: OECD Terms and Conditions
- **Datasets Used**:
  - Better Life Index
  - Government at a Glance
  - Policy Performance Indicators

#### International Monetary Fund (IMF)
- **Source**: IMF Data Portal
- **URL**: https://data.imf.org/
- **Last accessed**: 2024-12-26
- **License**: IMF Data License
- **Focus**: Economic policy effectiveness

#### Asian Development Bank (ADB)
- **Source**: ADB Data Library
- **URL**: https://data.adb.org/
- **Last accessed**: 2024-12-26
- **License**: ADB Open Data License
- **Focus**: Regional development policies

## Data Quality Standards

### Data Validation
- All data files must pass schema validation using pandera
- Missing values are documented and handled explicitly
- Data types are enforced and validated
- Duplicate records are identified and resolved

### Metadata Requirements
Each data file should include:
- **Source attribution**: Original data source and URL
- **Extraction date**: When the data was collected
- **Processing date**: When the data was last processed
- **Version**: Data version number
- **License**: Data usage license
- **Contact**: Data maintainer contact information

### File Naming Conventions
- Raw data: `{source}_{dataset}_{date}.csv`
- Processed data: `{dataset}_processed_{version}.csv`
- Backup data: `{filename}_backup_{timestamp}.csv`

## Data Processing Pipeline

1. **Data Extraction**: Raw data extracted from sources
2. **Data Validation**: Schema validation using pandera
3. **Data Cleaning**: Handle missing values, outliers, duplicates
4. **Data Transformation**: Convert to standard format
5. **Data Integration**: Merge multiple sources
6. **Data Validation**: Final quality checks
7. **Data Storage**: Save processed data with metadata

## Access and Usage Guidelines

### Internal Use
- All data files are for research and analysis purposes
- Maintain data confidentiality where required
- Follow institutional data governance policies

### External Sharing
- Ensure compliance with original data licenses
- Provide proper attribution to data sources
- Document any modifications or processing steps

### Data Retention
- Raw data: Retained indefinitely for reproducibility
- Processed data: Version controlled with git
- Backup data: Monthly snapshots maintained

## Contact Information

**Data Steward**: Policy Impact Assessment Team
**Email**: [data-steward@example.com]
**Last Updated**: 2024-12-26

## Changelog

### Version 1.0 (2024-12-26)
- Initial data directory structure
- Added schema validation
- Implemented data quality standards
- Documented data sources and provenance
