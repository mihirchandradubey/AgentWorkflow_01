"""Tests for BPMN generator module."""

import pytest
from src.converter.bpmn_generator import BPMNGenerator
from src.utils.xml_utils import XMLUtils


class TestBPMNGenerator:
    
    def setup_method(self):
        self.generator = BPMNGenerator()
        self.xml_utils = XMLUtils()
    
    def test_generate_simple_workflow(self):
        """Test generating simple BPMN workflow."""
        workflow_data = {
            'name': 'SimpleWorkflow',
            'elements': [
                {'id': 'task1', 'name': 'Task 1', 'type': 'FlowAction'}
            ],
            'connectors': []
        }
        
        bpmn_xml = self.generator.generate(workflow_data)
        
        assert bpmn_xml is not None
        assert 'bpmn:definitions' in bpmn_xml
        assert 'bpmn:process' in bpmn_xml
        assert 'SimpleWorkflow' in bpmn_xml
    
    def test_generate_includes_start_end_events(self):
        """Test that generated BPMN includes start and end events."""
        workflow_data = {
            'name': 'TestWorkflow',
            'elements': [],
            'connectors': []
        }
        
        bpmn_xml = self.generator.generate(workflow_data)
        
        assert 'startEvent' in bpmn_xml
        assert 'endEvent' in bpmn_xml
    
    def test_sanitize_id(self):
        """Test ID sanitization."""
        test_id = "test-id.with.special chars"
        sanitized = self.generator._sanitize_id(test_id)
        
        assert ' ' not in sanitized
        assert '-' not in sanitized
        assert '.' not in sanitized
