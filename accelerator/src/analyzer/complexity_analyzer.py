"""Complexity analyzer for assessing migration effort."""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class ComplexityAnalyzer:
    """Analyze workflow complexity to estimate migration effort."""

    def __init__(self):
        """Initialize complexity analyzer."""
        self.weights = {
            'element': 1,
            'connector': 0.5,
            'decision': 3,
            'subprocess': 5,
            'integration': 4,
            'sla_rule': 2,
            'custom_logic': 10
        }

    def analyze(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze workflow complexity.
        
        Args:
            workflow_data: Parsed workflow data
            
        Returns:
            Complexity analysis results
        """
        metrics = self._calculate_metrics(workflow_data)
        complexity_score = self._calculate_complexity_score(metrics)
        effort_estimate = self._estimate_effort(complexity_score)
        
        return {
            'metrics': metrics,
            'complexity_score': complexity_score,
            'complexity_level': self._get_complexity_level(complexity_score),
            'effort_estimate': effort_estimate,
            'recommendations': self._generate_recommendations(metrics, complexity_score)
        }

    def _calculate_metrics(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate various complexity metrics."""
        elements = workflow_data.get('elements', [])
        connectors = workflow_data.get('connectors', [])
        
        metrics = {
            'total_elements': len(elements),
            'total_connectors': len(connectors),
            'decision_count': len([e for e in elements if e.get('type') == 'Decision']),
            'assignment_count': len([e for e in elements if e.get('type') == 'Assignment']),
            'flow_action_count': len([e for e in elements if e.get('type') == 'FlowAction']),
            'connector_count': len([e for e in elements if 'Connector' in e.get('type', '')]),
            'wait_count': len([e for e in elements if e.get('type') == 'Wait']),
            'subprocess_count': len([e for e in elements if 'SubProcess' in e.get('type', '') or 'SubFlow' in e.get('type', '')]),
            'sla_count': len(workflow_data.get('metadata', {}).get('sla_rules', [])),
            'routing_rule_count': len(workflow_data.get('metadata', {}).get('routing_rules', [])),
            'stage_count': len(workflow_data.get('stages', [])),
            'cyclomatic_complexity': self._calculate_cyclomatic_complexity(workflow_data)
        }
        
        return metrics

    def _calculate_cyclomatic_complexity(self, workflow_data: Dict[str, Any]) -> int:
        """
        Calculate cyclomatic complexity (McCabe complexity).
        Formula: M = E - N + 2P
        where E = edges, N = nodes, P = connected components (usually 1)
        """
        elements = workflow_data.get('elements', [])
        connectors = workflow_data.get('connectors', [])
        
        nodes = len(elements) + 2  # +2 for implicit start and end
        edges = len(connectors)
        
        # For simplicity, assume 1 connected component
        complexity = edges - nodes + 2
        
        return max(1, complexity)  # Minimum complexity is 1

    def _calculate_complexity_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall complexity score based on metrics."""
        score = 0.0
        
        # Base score from element count
        score += metrics['total_elements'] * self.weights['element']
        score += metrics['total_connectors'] * self.weights['connector']
        
        # Additional complexity from specific element types
        score += metrics['decision_count'] * self.weights['decision']
        score += metrics['subprocess_count'] * self.weights['subprocess']
        score += metrics['connector_count'] * self.weights['integration']
        score += metrics['sla_count'] * self.weights['sla_rule']
        
        # Cyclomatic complexity contributes to overall score
        score += metrics['cyclomatic_complexity'] * 2
        
        return score

    def _get_complexity_level(self, score: float) -> str:
        """Determine complexity level based on score."""
        if score < 20:
            return 'Low'
        elif score < 50:
            return 'Medium'
        elif score < 100:
            return 'High'
        else:
            return 'Very High'

    def _estimate_effort(self, complexity_score: float) -> Dict[str, Any]:
        """Estimate migration effort based on complexity score."""
        # Estimate in person-hours
        # Base assumption: 1 complexity point = 0.5 hours
        hours = complexity_score * 0.5
        
        # Convert to person-days (8 hours per day)
        days = hours / 8
        
        return {
            'estimated_hours': round(hours, 1),
            'estimated_days': round(days, 1),
            'automation_percentage': self._estimate_automation_percentage(complexity_score),
            'manual_effort_percentage': 100 - self._estimate_automation_percentage(complexity_score)
        }

    def _estimate_automation_percentage(self, complexity_score: float) -> int:
        """Estimate what percentage can be automated."""
        # Higher complexity typically means lower automation percentage
        if complexity_score < 20:
            return 85
        elif complexity_score < 50:
            return 75
        elif complexity_score < 100:
            return 65
        else:
            return 55

    def _generate_recommendations(self, metrics: Dict[str, Any], 
                                 complexity_score: float) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        if metrics['decision_count'] > 5:
            recommendations.append(
                "High number of decision points detected. Consider consolidating "
                "decision logic into DMN tables for better maintainability."
            )
        
        if metrics['subprocess_count'] > 3:
            recommendations.append(
                "Multiple subprocesses detected. Ensure proper subprocess "
                "modeling in Camunda (embedded vs. call activities)."
            )
        
        if metrics['sla_count'] > 0:
            recommendations.append(
                "SLA rules detected. These will be converted to timer boundary events. "
                "Review timeout handling logic after migration."
            )
        
        if metrics['cyclomatic_complexity'] > 10:
            recommendations.append(
                "High cyclomatic complexity detected. Consider simplifying workflow "
                "logic or breaking into smaller processes."
            )
        
        if complexity_score > 100:
            recommendations.append(
                "Very high complexity workflow. Consider phased migration approach, "
                "migrating critical paths first."
            )
        
        if metrics['connector_count'] > 5:
            recommendations.append(
                "Multiple integration points detected. Ensure proper mapping of "
                "Pega connectors to Camunda service tasks or external tasks."
            )
        
        return recommendations

    def compare_workflows(self, workflows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare complexity across multiple workflows.
        
        Args:
            workflows: List of workflow data dictionaries
            
        Returns:
            Comparison analysis
        """
        analyses = []
        for workflow in workflows:
            analysis = self.analyze(workflow)
            analysis['workflow_name'] = workflow.get('name', 'Unknown')
            analyses.append(analysis)
        
        # Sort by complexity score
        analyses.sort(key=lambda x: x['complexity_score'], reverse=True)
        
        return {
            'total_workflows': len(workflows),
            'analyses': analyses,
            'summary': {
                'avg_complexity_score': sum(a['complexity_score'] for a in analyses) / len(analyses) if analyses else 0,
                'total_estimated_hours': sum(a['effort_estimate']['estimated_hours'] for a in analyses),
                'total_estimated_days': sum(a['effort_estimate']['estimated_days'] for a in analyses),
                'most_complex': analyses[0]['workflow_name'] if analyses else None,
                'least_complex': analyses[-1]['workflow_name'] if analyses else None
            }
        }
