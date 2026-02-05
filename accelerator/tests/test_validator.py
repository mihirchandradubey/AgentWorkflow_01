"""Tests for BPMN validator module."""

import pytest
from src.validator.bpmn_validator import BPMNValidator


class TestBPMNValidator:
    
    def setup_method(self):
        self.validator = BPMNValidator()
    
    def test_validate_valid_bpmn(self):
        """Test validating valid BPMN."""
        bpmn_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL">
            <bpmn:process id="Process_1" isExecutable="true">
                <bpmn:startEvent id="StartEvent_1"/>
                <bpmn:endEvent id="EndEvent_1"/>
            </bpmn:process>
        </bpmn:definitions>'''
        
        result = self.validator.validate(bpmn_xml)
        
        assert result is not None
        assert 'valid' in result
        assert 'errors' in result
        assert 'warnings' in result
    
    def test_validate_invalid_xml(self):
        """Test validating invalid XML."""
        invalid_xml = '<Invalid XML'
        
        result = self.validator.validate(invalid_xml)
        
        assert result['valid'] is False
        assert len(result['errors']) > 0
