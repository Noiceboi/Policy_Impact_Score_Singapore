"""
Advanced MCDA (Multi-Criteria Decision Analysis) methods for policy assessment.

This module implements advanced MCDA techniques including AHP (Analytic Hierarchy Process),
ELECTRE, and sensitivity analysis methods for robust policy impact assessment.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import logging
from scipy import stats
from scipy.optimize import minimize

logger = logging.getLogger(__name__)


@dataclass
class MCDAResult:
    """
    Result of MCDA analysis.
    
    Attributes:
        scores: Final normalized scores for each alternative
        rankings: Ranking of alternatives (1 = best)
        weights: Normalized criteria weights used
        method: MCDA method used
        consistency_ratio: Consistency ratio (for AHP)
        sensitivity_analysis: Results of sensitivity analysis
    """
    scores: Dict[str, float]
    rankings: Dict[str, int]
    weights: Dict[str, float]
    method: str
    consistency_ratio: Optional[float] = None
    sensitivity_analysis: Optional[Dict[str, Any]] = None


class AHPProcessor:
    """
    Analytic Hierarchy Process (AHP) implementation for policy assessment.
    
    AHP provides a structured way to determine criterion weights through
    pairwise comparisons and consistency checking.
    """
    
    def __init__(self):
        """Initialize AHP processor."""
        self.consistency_threshold = 0.1  # Standard AHP consistency threshold
        self.random_index = {
            1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12,
            6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49
        }
    
    def create_pairwise_matrix(
        self, 
        criteria: List[str], 
        comparisons: Dict[Tuple[str, str], float]
    ) -> np.ndarray:
        """
        Create pairwise comparison matrix from comparisons.
        
        Args:
            criteria: List of criteria names
            comparisons: Dictionary of pairwise comparisons {(criterion1, criterion2): value}
                        Values follow AHP scale: 1=equal, 3=moderate, 5=strong, 7=very strong, 9=extreme
        
        Returns:
            Pairwise comparison matrix
        """
        n = len(criteria)
        matrix = np.ones((n, n))
        
        for i, criterion1 in enumerate(criteria):
            for j, criterion2 in enumerate(criteria):
                if i != j:
                    key = (criterion1, criterion2)
                    reverse_key = (criterion2, criterion1)
                    
                    if key in comparisons:
                        matrix[i, j] = comparisons[key]
                        matrix[j, i] = 1.0 / comparisons[key]
                    elif reverse_key in comparisons:
                        matrix[i, j] = 1.0 / comparisons[reverse_key]
                        matrix[j, i] = comparisons[reverse_key]
        
        return matrix
    
    def calculate_weights(self, pairwise_matrix: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Calculate criteria weights from pairwise comparison matrix.
        
        Args:
            pairwise_matrix: Pairwise comparison matrix
            
        Returns:
            Tuple of (weights, consistency_ratio)
        """
        n = len(pairwise_matrix)
        
        # Calculate eigenvalues and eigenvectors
        eigenvalues, eigenvectors = np.linalg.eig(pairwise_matrix)
        
        # Find principal eigenvalue and corresponding eigenvector
        max_eigenvalue_idx = np.argmax(eigenvalues.real)
        max_eigenvalue = eigenvalues[max_eigenvalue_idx].real
        principal_eigenvector = eigenvectors[:, max_eigenvalue_idx].real
        
        # Normalize weights
        weights = principal_eigenvector / np.sum(principal_eigenvector)
        weights = np.abs(weights)  # Ensure positive weights
        
        # Calculate consistency ratio
        consistency_index = (max_eigenvalue - n) / (n - 1)
        consistency_ratio = consistency_index / self.random_index.get(n, 1.0)
        
        return weights, consistency_ratio
    
    def assess_consistency(self, consistency_ratio: float) -> bool:
        """
        Assess if pairwise comparisons are consistent.
        
        Args:
            consistency_ratio: Calculated consistency ratio
            
        Returns:
            True if consistent (CR < 0.1), False otherwise
        """
        return consistency_ratio < self.consistency_threshold
    
    def calculate_policy_scores(
        self, 
        criteria_scores: pd.DataFrame, 
        weights: np.ndarray
    ) -> np.ndarray:
        """
        Calculate final policy scores using normalized criteria scores and weights.
        
        Args:
            criteria_scores: DataFrame with policies as rows and criteria as columns
            weights: Array of normalized criteria weights
            
        Returns:
            Array of final policy scores
        """
        # Normalize criteria scores to 0-1 scale
        normalized_scores = (criteria_scores - criteria_scores.min()) / (
            criteria_scores.max() - criteria_scores.min()
        )
        
        # Calculate weighted scores
        final_scores = np.dot(normalized_scores.values, weights)
        
        return final_scores


class ELECTREProcessor:
    """
    ELECTRE (Elimination and Choice Expressing Reality) implementation.
    
    ELECTRE is an outranking method that builds preference relations
    between alternatives based on concordance and discordance analysis.
    """
    
    def __init__(self, concordance_threshold: float = 0.75, discordance_threshold: float = 0.25):
        """
        Initialize ELECTRE processor.
        
        Args:
            concordance_threshold: Threshold for concordance index
            discordance_threshold: Threshold for discordance index
        """
        self.concordance_threshold = concordance_threshold
        self.discordance_threshold = discordance_threshold
    
    def calculate_concordance_matrix(
        self, 
        criteria_scores: pd.DataFrame, 
        weights: np.ndarray
    ) -> np.ndarray:
        """
        Calculate concordance matrix.
        
        Args:
            criteria_scores: DataFrame with policies as rows and criteria as columns
            weights: Array of criteria weights
            
        Returns:
            Concordance matrix
        """
        n_alternatives = len(criteria_scores)
        concordance_matrix = np.zeros((n_alternatives, n_alternatives))
        
        for i in range(n_alternatives):
            for j in range(n_alternatives):
                if i != j:
                    # Find criteria where alternative i outperforms j
                    outperform_criteria = criteria_scores.iloc[i] >= criteria_scores.iloc[j]
                    concordance_matrix[i, j] = np.sum(weights[outperform_criteria])
        
        return concordance_matrix
    
    def calculate_discordance_matrix(self, criteria_scores: pd.DataFrame) -> np.ndarray:
        """
        Calculate discordance matrix.
        
        Args:
            criteria_scores: DataFrame with policies as rows and criteria as columns
            
        Returns:
            Discordance matrix
        """
        n_alternatives = len(criteria_scores)
        discordance_matrix = np.zeros((n_alternatives, n_alternatives))
        
        # Normalize criteria scores
        normalized_scores = (criteria_scores - criteria_scores.min()) / (
            criteria_scores.max() - criteria_scores.min()
        )
        
        for i in range(n_alternatives):
            for j in range(n_alternatives):
                if i != j:
                    # Calculate maximum difference where j outperforms i
                    differences = normalized_scores.iloc[j] - normalized_scores.iloc[i]
                    max_negative_diff = np.max(differences[differences > 0])
                    
                    # Discordance is relative to maximum range
                    max_range = np.max(normalized_scores.max() - normalized_scores.min())
                    discordance_matrix[i, j] = max_negative_diff / max_range if max_range > 0 else 0
        
        return discordance_matrix
    
    def build_outranking_relation(
        self, 
        concordance_matrix: np.ndarray, 
        discordance_matrix: np.ndarray
    ) -> np.ndarray:
        """
        Build outranking relation matrix.
        
        Args:
            concordance_matrix: Concordance matrix
            discordance_matrix: Discordance matrix
            
        Returns:
            Outranking relation matrix (1 = outranks, 0 = does not outrank)
        """
        outranking_matrix = np.zeros_like(concordance_matrix)
        
        for i in range(len(concordance_matrix)):
            for j in range(len(concordance_matrix)):
                if i != j:
                    concordance_condition = concordance_matrix[i, j] >= self.concordance_threshold
                    discordance_condition = discordance_matrix[i, j] <= self.discordance_threshold
                    
                    if concordance_condition and discordance_condition:
                        outranking_matrix[i, j] = 1
        
        return outranking_matrix
    
    def calculate_net_flow(self, outranking_matrix: np.ndarray) -> np.ndarray:
        """
        Calculate net outranking flow for ranking.
        
        Args:
            outranking_matrix: Outranking relation matrix
            
        Returns:
            Net flow values for each alternative
        """
        positive_flow = np.sum(outranking_matrix, axis=1)
        negative_flow = np.sum(outranking_matrix, axis=0)
        net_flow = positive_flow - negative_flow
        
        return net_flow


class SensitivityAnalyzer:
    """
    Sensitivity analysis for MCDA results.
    
    This class provides methods to analyze how sensitive the MCDA results
    are to changes in criteria weights and scores.
    """
    
    def __init__(self):
        """Initialize sensitivity analyzer."""
        self.n_simulations = 1000
    
    def weight_sensitivity_analysis(
        self,
        criteria_scores: pd.DataFrame,
        base_weights: np.ndarray,
        weight_variation: float = 0.2
    ) -> Dict[str, Any]:
        """
        Perform sensitivity analysis on criteria weights.
        
        Args:
            criteria_scores: DataFrame with policies as rows and criteria as columns
            base_weights: Base weights for criteria
            weight_variation: Maximum relative variation in weights (0.2 = ±20%)
            
        Returns:
            Dictionary containing sensitivity analysis results
        """
        n_criteria = len(base_weights)
        n_policies = len(criteria_scores)
        
        # Store results for each simulation
        rankings_history = []
        scores_history = []
        
        for _ in range(self.n_simulations):
            # Generate perturbed weights
            perturbation = np.random.uniform(
                -weight_variation, weight_variation, n_criteria
            )
            perturbed_weights = base_weights * (1 + perturbation)
            
            # Normalize weights
            perturbed_weights = perturbed_weights / np.sum(perturbed_weights)
            
            # Calculate scores and rankings
            scores = self._calculate_weighted_scores(criteria_scores, perturbed_weights)
            rankings = stats.rankdata(-scores, method='ordinal')
            
            rankings_history.append(rankings)
            scores_history.append(scores)
        
        # Analyze results
        rankings_array = np.array(rankings_history)
        scores_array = np.array(scores_history)
        
        # Calculate ranking stability
        ranking_stability = self._calculate_ranking_stability(rankings_array)
        
        # Calculate score confidence intervals
        score_confidence_intervals = {
            f"policy_{i}": {
                "mean": np.mean(scores_array[:, i]),
                "std": np.std(scores_array[:, i]),
                "ci_lower": np.percentile(scores_array[:, i], 2.5),
                "ci_upper": np.percentile(scores_array[:, i], 97.5)
            }
            for i in range(n_policies)
        }
        
        return {
            "ranking_stability": ranking_stability,
            "score_confidence_intervals": score_confidence_intervals,
            "weight_variation_tested": weight_variation,
            "n_simulations": self.n_simulations
        }
    
    def monte_carlo_analysis(
        self,
        criteria_scores: pd.DataFrame,
        weights: np.ndarray,
        score_uncertainty: float = 0.1
    ) -> Dict[str, Any]:
        """
        Perform Monte Carlo analysis on criteria scores.
        
        Args:
            criteria_scores: DataFrame with policies as rows and criteria as columns
            weights: Criteria weights
            score_uncertainty: Relative uncertainty in scores (0.1 = ±10%)
            
        Returns:
            Dictionary containing Monte Carlo analysis results
        """
        rankings_history = []
        scores_history = []
        
        for _ in range(self.n_simulations):
            # Add noise to criteria scores
            noise = np.random.normal(0, score_uncertainty, criteria_scores.shape)
            perturbed_scores = criteria_scores * (1 + noise)
            
            # Ensure scores remain within bounds
            perturbed_scores = np.clip(perturbed_scores, 1, 5)
            
            # Calculate final scores and rankings
            final_scores = self._calculate_weighted_scores(perturbed_scores, weights)
            rankings = stats.rankdata(-final_scores, method='ordinal')
            
            rankings_history.append(rankings)
            scores_history.append(final_scores)
        
        # Analyze results
        rankings_array = np.array(rankings_history)
        scores_array = np.array(scores_history)
        
        ranking_stability = self._calculate_ranking_stability(rankings_array)
        
        return {
            "ranking_stability": ranking_stability,  
            "score_robustness": np.std(scores_array, axis=0).tolist(),
            "score_uncertainty_tested": score_uncertainty,
            "n_simulations": self.n_simulations
        }
    
    def _calculate_weighted_scores(
        self, 
        criteria_scores: pd.DataFrame, 
        weights: np.ndarray
    ) -> np.ndarray:
        """Calculate weighted scores from criteria scores and weights."""
        # Normalize scores
        normalized_scores = (criteria_scores - criteria_scores.min()) / (
            criteria_scores.max() - criteria_scores.min()
        )
        
        return np.dot(normalized_scores.values, weights)
    
    def _calculate_ranking_stability(self, rankings_array: np.ndarray) -> Dict[str, float]:
        """
        Calculate ranking stability metrics.
        
        Args:
            rankings_array: Array of rankings from multiple simulations
            
        Returns:
            Dictionary with stability metrics
        """
        n_policies = rankings_array.shape[1]
        
        # Calculate how often each policy appears in each rank position
        rank_frequencies = {}
        for policy_idx in range(n_policies):
            policy_rankings = rankings_array[:, policy_idx]
            rank_frequencies[f"policy_{policy_idx}"] = {
                f"rank_{rank}": np.sum(policy_rankings == rank) / len(policy_rankings)
                for rank in range(1, n_policies + 1)
            }
        
        # Calculate overall ranking stability (percentage of times top ranking doesn't change)
        top_policy_stability = []
        first_top_policy = np.argmin(rankings_array[0])  # Policy with rank 1 in first simulation
        
        for sim_rankings in rankings_array:
            current_top_policy = np.argmin(sim_rankings)
            top_policy_stability.append(current_top_policy == first_top_policy)
        
        overall_stability = np.mean(top_policy_stability)
        
        return {
            "overall_top_rank_stability": overall_stability,
            "rank_frequencies": rank_frequencies
        }


class AdvancedMCDAFramework:
    """
    Advanced MCDA framework combining multiple methods and sensitivity analysis.
    """
    
    def __init__(self):
        """Initialize advanced MCDA framework."""
        self.ahp = AHPProcessor()
        self.electre = ELECTREProcessor()
        self.sensitivity = SensitivityAnalyzer()
    
    def comprehensive_analysis(
        self,
        criteria_scores: pd.DataFrame,
        pairwise_comparisons: Dict[Tuple[str, str], float],
        policy_names: Optional[List[str]] = None
    ) -> MCDAResult:
        """
        Perform comprehensive MCDA analysis.
        
        Args:
            criteria_scores: DataFrame with policies as rows and criteria as columns
            pairwise_comparisons: Pairwise comparisons for AHP weight calculation
            policy_names: Names of policies (optional)
            
        Returns:
            Comprehensive MCDA results
        """
        criteria = criteria_scores.columns.tolist()
        policy_names = policy_names or [f"Policy_{i}" for i in range(len(criteria_scores))]
        
        # Step 1: Calculate weights using AHP
        pairwise_matrix = self.ahp.create_pairwise_matrix(criteria, pairwise_comparisons)
        weights, consistency_ratio = self.ahp.calculate_weights(pairwise_matrix)
        
        # Check consistency
        is_consistent = self.ahp.assess_consistency(consistency_ratio)
        if not is_consistent:
            logger.warning(f"AHP consistency ratio {consistency_ratio:.3f} exceeds threshold")
        
        # Step 2: Calculate final scores
        final_scores = self.ahp.calculate_policy_scores(criteria_scores, weights)
        
        # Step 3: Generate rankings
        rankings = stats.rankdata(-final_scores, method='ordinal')
        
        # Step 4: Perform sensitivity analysis
        sensitivity_results = self.sensitivity.weight_sensitivity_analysis(
            criteria_scores, weights
        )
        
        # Create results dictionary
        scores_dict = {policy_names[i]: final_scores[i] for i in range(len(policy_names))}
        rankings_dict = {policy_names[i]: rankings[i] for i in range(len(policy_names))}
        weights_dict = {criteria[i]: weights[i] for i in range(len(criteria))}
        
        return MCDAResult(
            scores=scores_dict,
            rankings=rankings_dict,
            weights=weights_dict,
            method="AHP with Sensitivity Analysis",
            consistency_ratio=consistency_ratio,
            sensitivity_analysis=sensitivity_results
        )
    
    def compare_methods(
        self,
        criteria_scores: pd.DataFrame,
        weights: np.ndarray,
        policy_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compare results from different MCDA methods.
        
        Args:
            criteria_scores: DataFrame with policies as rows and criteria as columns
            weights: Criteria weights
            policy_names: Names of policies (optional)
            
        Returns:
            Dictionary comparing different methods
        """
        policy_names = policy_names or [f"Policy_{i}" for i in range(len(criteria_scores))]
        
        # AHP scores
        ahp_scores = self.ahp.calculate_policy_scores(criteria_scores, weights)
        ahp_rankings = stats.rankdata(-ahp_scores, method='ordinal')
        
        # ELECTRE analysis
        concordance_matrix = self.electre.calculate_concordance_matrix(criteria_scores, weights)
        discordance_matrix = self.electre.calculate_discordance_matrix(criteria_scores)
        outranking_matrix = self.electre.build_outranking_relation(
            concordance_matrix, discordance_matrix
        )
        electre_net_flow = self.electre.calculate_net_flow(outranking_matrix)
        electre_rankings = stats.rankdata(-electre_net_flow, method='ordinal')
        
        # Simple weighted sum
        normalized_scores = (criteria_scores - criteria_scores.min()) / (
            criteria_scores.max() - criteria_scores.min()
        )
        simple_scores = np.dot(normalized_scores.values, weights)
        simple_rankings = stats.rankdata(-simple_scores, method='ordinal')
        
        # Calculate rank correlation between methods
        ahp_electre_correlation = stats.spearmanr(ahp_rankings, electre_rankings)[0]
        ahp_simple_correlation = stats.spearmanr(ahp_rankings, simple_rankings)[0]
        electre_simple_correlation = stats.spearmanr(electre_rankings, simple_rankings)[0]
        
        return {
            "methods_comparison": {
                "AHP": {
                    "scores": {policy_names[i]: ahp_scores[i] for i in range(len(policy_names))},
                    "rankings": {policy_names[i]: ahp_rankings[i] for i in range(len(policy_names))}
                },
                "ELECTRE": {
                    "net_flow": {policy_names[i]: electre_net_flow[i] for i in range(len(policy_names))},
                    "rankings": {policy_names[i]: electre_rankings[i] for i in range(len(policy_names))}
                },
                "Simple_Weighted": {
                    "scores": {policy_names[i]: simple_scores[i] for i in range(len(policy_names))},
                    "rankings": {policy_names[i]: simple_rankings[i] for i in range(len(policy_names))}
                }
            },
            "rank_correlations": {
                "AHP_vs_ELECTRE": ahp_electre_correlation,
                "AHP_vs_Simple": ahp_simple_correlation,
                "ELECTRE_vs_Simple": electre_simple_correlation
            }
        }
