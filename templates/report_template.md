# Policy Impact Assessment Report

**Generated on:** {{ report_metadata.generated_at }}  
**Assessment Period:** {{ report_metadata.assessment_period }}  
**Framework Version:** {{ report_metadata.framework_version }}

## Executive Summary

This report presents the results of a comprehensive policy impact assessment conducted using the Singapore Policy Impact Assessment Framework. The analysis evaluated {{ statistics.total_policies }} policies across {{ statistics.total_categories }} categories using multi-criteria decision analysis (MCDA) techniques.

### Key Findings

- **Total Policies Analyzed:** {{ statistics.total_policies }}
- **Verified Policies:** {{ statistics.verified_policies }} ({{ statistics.verification_rate }}%)
- **Average Impact Score:** {{ "%.2f"|format(statistics.avg_impact_score) }}/5.0
- **Scientific Confidence Level:** {{ "%.1f"|format(statistics.scientific_confidence * 100) }}%

{% if methodology.ahp_consistency_ratio %}
- **AHP Consistency Ratio:** {{ "%.3f"|format(methodology.ahp_consistency_ratio) }} {% if methodology.ahp_consistency_ratio < 0.1 %}✓ Acceptable{% else %}⚠ Review Required{% endif %}
{% endif %}

## Methodology

### Assessment Framework

The assessment framework employs a rigorous multi-criteria decision analysis (MCDA) approach based on internationally recognized standards:

#### Assessment Criteria

1. **Scope (Weight: {{ "%.1f"|format(methodology.weights.scope) }})**: Geographic or demographic reach of the policy
2. **Magnitude (Weight: {{ "%.1f"|format(methodology.weights.magnitude) }})**: Intensity or strength of policy effects  
3. **Durability (Weight: {{ "%.1f"|format(methodology.weights.durability) }})**: Long-term sustainability of policy impacts
4. **Adaptability (Weight: {{ "%.1f"|format(methodology.weights.adaptability) }})**: Policy flexibility and responsiveness
5. **Cross-referencing (Weight: {{ "%.1f"|format(methodology.weights.cross_referencing) }})**: Integration with other policies

#### MCDA Methods Applied

- **Analytic Hierarchy Process (AHP)**: For weight derivation through pairwise comparisons
- **Weighted Sum Model (WSM)**: With normalized criteria scores
{% if methodology.electre_used %}
- **ELECTRE**: For outranking analysis and robust ranking
{% endif %}
- **Sensitivity Analysis**: Monte Carlo simulation with {{ methodology.n_simulations }} iterations

### Data Sources and Validation

#### Primary Data Sources
{% for source in data_sources.primary %}
- **{{ source.name }}**: {{ source.url }}
  - Last accessed: {{ source.last_accessed }}
  - License: {{ source.license }}
  - Coverage: {{ source.coverage }}
{% endfor %}

#### International Validation Sources
{% for source in data_sources.international %}
- **{{ source.organization }}**: {{ source.methodology }}
  - Validation Score: {{ "%.2f"|format(source.average_score) }}/5.0
  - Confidence Level: {{ "%.1f"|format(source.confidence * 100) }}%
{% endfor %}

## Results

### Policy Rankings

The following table presents the top-ranking policies based on the comprehensive MCDA analysis:

| Rank | Policy Name | Category | Impact Score | Confidence Interval |
|------|-------------|----------|--------------|-------------------|
{% for policy in results.top_policies %}
| {{ policy.rank }} | {{ policy.name }} | {{ policy.category }} | {{ "%.2f"|format(policy.score) }} | [{{ "%.2f"|format(policy.ci_lower) }}, {{ "%.2f"|format(policy.ci_upper) }}] |
{% endfor %}

### Category Analysis

#### Policies by Category

{% for category in results.category_analysis %}
**{{ category.name }}** ({{ category.count }} policies)
- Average Impact Score: {{ "%.2f"|format(category.avg_score) }}
- Score Range: {{ "%.2f"|format(category.min_score) }} - {{ "%.2f"|format(category.max_score) }}
- Top Policy: {{ category.top_policy.name }} ({{ "%.2f"|format(category.top_policy.score) }})

{% endfor %}

### Temporal Analysis

#### Implementation Timeline

The analysis reveals the following implementation patterns:

{% for year_data in results.temporal_analysis %}
- **{{ year_data.year }}**: {{ year_data.count }} policies implemented
  - Average score: {{ "%.2f"|format(year_data.avg_score) }}
  - Notable policies: {{ year_data.notable_policies|join(", ") }}
{% endfor %}

## Sensitivity Analysis

### Weight Sensitivity

The sensitivity analysis examined the robustness of rankings to variations in criteria weights (±{{ "%.0f"|format(sensitivity.weight_variation * 100) }}%):

{% for policy in sensitivity.policy_stability %}
- **{{ policy.name }}**: 
  - Ranking stability: {{ "%.1f"|format(policy.stability * 100) }}%
  - Score confidence interval: [{{ "%.2f"|format(policy.score_ci_lower) }}, {{ "%.2f"|format(policy.score_ci_upper) }}]
{% endfor %}

### Monte Carlo Analysis

Monte Carlo simulation with {{ sensitivity.n_simulations }} iterations assessed the impact of measurement uncertainty:

- **Overall ranking stability**: {{ "%.1f"|format(sensitivity.overall_stability * 100) }}%
- **Score uncertainty**: ±{{ "%.1f"|format(sensitivity.avg_score_uncertainty * 100) }}%

## International Validation

### Comparative Analysis

The framework's results were validated against assessments from international organizations:

{% for validation in international_validation %}
#### {{ validation.organization }}

- **Methodology**: {{ validation.methodology }}
- **Correlation with framework**: {{ "%.3f"|format(validation.correlation) }}
- **Statistical significance**: {{ validation.p_value_interpretation }}

Key alignments:
{% for alignment in validation.alignments %}
- {{ alignment.policy }}: Framework score {{ "%.2f"|format(alignment.framework_score) }}, {{ validation.organization }} score {{ "%.2f"|format(alignment.external_score) }}
{% endfor %}

{% endfor %}

## Quality Assurance

### Data Quality Metrics

- **Data completeness**: {{ "%.1f"|format(quality.completeness * 100) }}%
- **Data consistency**: {{ "%.1f"|format(quality.consistency * 100) }}%
- **Validation coverage**: {{ "%.1f"|format(quality.validation_coverage * 100) }}%

### Methodological Rigor

- **Peer review status**: {{ quality.peer_review_status }}
- **Reproducibility**: {{ quality.reproducibility_score }}/10
- **Transparency score**: {{ "%.1f"|format(quality.transparency_score) }}/10

{% if quality.limitations %}
### Limitations and Caveats

{% for limitation in quality.limitations %}
- {{ limitation }}
{% endfor %}
{% endif %}

## Conclusions and Recommendations

### Key Insights

{% for insight in conclusions.key_insights %}
{{ loop.index }}. **{{ insight.title }}**: {{ insight.description }}
{% endfor %}

### Policy Recommendations

#### High-Impact Policies for Replication
{% for policy in conclusions.high_impact_policies %}
- **{{ policy.name }}** (Score: {{ "%.2f"|format(policy.score) }})
  - Success factors: {{ policy.success_factors|join(", ") }}
  - Scalability: {{ policy.scalability }}
  - Implementation timeline: {{ policy.timeline }}
{% endfor %}

#### Areas for Improvement
{% for area in conclusions.improvement_areas %}
- **{{ area.category }}**: {{ area.recommendation }}
  - Priority: {{ area.priority }}
  - Expected impact: {{ area.expected_impact }}
{% endfor %}

### Future Research Directions

{% for direction in conclusions.future_research %}
- {{ direction }}
{% endfor %}

## Appendices

### Appendix A: Detailed Policy Scores

| Policy ID | Name | Category | Scope | Magnitude | Durability | Adaptability | Cross-ref | Overall |
|-----------|------|----------|-------|-----------|------------|--------------|-----------|---------|
{% for policy in appendices.detailed_scores %}
| {{ policy.id }} | {{ policy.name }} | {{ policy.category }} | {{ policy.scope }} | {{ policy.magnitude }} | {{ policy.durability }} | {{ policy.adaptability }} | {{ policy.cross_referencing }} | {{ "%.2f"|format(policy.overall_score) }} |
{% endfor %}

### Appendix B: Statistical Analysis

#### Correlation Matrix

|  | Scope | Magnitude | Durability | Adaptability | Cross-ref |
|--|-------|-----------|------------|--------------|-----------|
{% for row in appendices.correlation_matrix %}
| {{ row.criterion }} | {{ row.scope|round(3) }} | {{ row.magnitude|round(3) }} | {{ row.durability|round(3) }} | {{ row.adaptability|round(3) }} | {{ row.cross_referencing|round(3) }} |
{% endfor %}

#### Distribution Analysis

- **Score distribution**: {{ appendices.distribution.type }} (μ={{ "%.2f"|format(appendices.distribution.mean) }}, σ={{ "%.2f"|format(appendices.distribution.std) }})
- **Normality test**: {{ appendices.distribution.normality_test }} (p={{ "%.3f"|format(appendices.distribution.p_value) }})

### Appendix C: Validation Details

#### Data Provenance
{% for source in appendices.data_provenance %}
- **{{ source.dataset }}**: 
  - Source: {{ source.origin }}
  - Extraction date: {{ source.extraction_date }}
  - Processing steps: {{ source.processing_steps|join(" → ") }}
  - Quality score: {{ source.quality_score }}/10
{% endfor %}

---

**Report Prepared By:** Policy Impact Assessment Framework v{{ report_metadata.framework_version }}  
**Contact:** {{ report_metadata.contact_info }}  
**License:** {{ report_metadata.license }}

*This report was generated automatically using validated data sources and peer-reviewed methodologies. For questions about the methodology or to request the underlying data, please contact the data steward.*
