"""Tests for complexity analyzer module."""

import pytest
from src.analyzer.complexity_analyzer import ComplexityAnalyzer


class TestComplexityAnalyzer:
    
    def setup_method(self):
        self.analyzer = ComplexityAnalyzer()
    
    def test_analyze_simple_workflow(self):
        """Test analyzing simple workflow."""
        workflow_data = {
            'name': 'SimpleWorkflow',
            'elements': [
                {'id': 'e1', 'type': 'FlowAction'},
                {'id': 'e2', 'type': 'Assignment'}
            ],
            'connectors': [
                {'id': 'c1', 'source': 'e1', 'target': 'e2'}
            ],
            'metadata': {'sla_rules': [], 'routing_rules': []},
            'stages': []
        }
        
        result = self.analyzer.analyze(workflow_data)
        
        assert 'complexity_score' in result
        assert 'complexity_level' in result
        assert 'effort_estimate' in result
        assert result['complexity_level'] == 'Low'
    
    def test_analyze_complex_workflow(self):
        """Test analyzing complex workflow."""
        # Create workflow with many elements
        elements = [{'id': f'e{i}', 'type': 'Decision'} for i in range(20)]
        connectors = [{'id': f'c{i}', 'source': f'e{i}', 'target': f'e{i+1}'} 
                     for i in range(19)]
        
        workflow_data = {
            'name': 'ComplexWorkflow',
            'elements': elements,
            'connectors': connectors,
            'metadata': {'sla_rules': [{'name': 'SLA1'}], 'routing_rules': []},
            'stages': []
        }
        
        result = self.analyzer.analyze(workflow_data)
        
        assert result['complexity_score'] > 20
        assert result['complexity_level'] in ['Medium', 'High', 'Very High']
    
    def test_effort_estimation(self):
        """Test effort estimation calculation."""
        workflow_data = {
            'elements': [{'id': 'e1', 'type': 'FlowAction'}],
            'connectors': [],
            'metadata': {'sla_rules': [], 'routing_rules': []},
            'stages': []
        }
        
        result = self.analyzer.analyze(workflow_data)
        effort = result['effort_estimate']
        
        assert 'estimated_hours' in effort
        assert 'estimated_days' in effort
        assert 'automation_percentage' in effort
        assert effort['estimated_hours'] > 0
