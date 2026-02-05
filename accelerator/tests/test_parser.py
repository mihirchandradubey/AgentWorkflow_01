"""Tests for Pega parser module."""

import pytest
from src.parser.pega_parser import PegaParser


class TestPegaParser:
    
    def setup_method(self):
        self.parser = PegaParser()
    
    def test_parse_xml_simple(self):
        """Test parsing simple XML workflow."""
        xml_content = '''<?xml version="1.0"?>
        <Workflow name="TestWorkflow" version="1.0">
            <Elements>
                <FlowAction id="FA1" name="Test Action"/>
            </Elements>
        </Workflow>'''
        
        result = self.parser.parse(xml_content, 'xml')
        
        assert result is not None
        assert result['name'] == 'TestWorkflow'
        assert result['type'] == 'pega_workflow'
        assert len(result['elements']) == 1
    
    def test_parse_json_simple(self):
        """Test parsing simple JSON workflow."""
        json_content = '''{
            "name": "TestWorkflow",
            "elements": [
                {"id": "E1", "name": "Test Element", "type": "FlowAction"}
            ],
            "connectors": []
        }'''
        
        result = self.parser.parse(json_content, 'json')
        
        assert result is not None
        assert result['name'] == 'TestWorkflow'
        assert len(result['elements']) == 1
    
    def test_parse_invalid_xml(self):
        """Test parsing invalid XML returns None."""
        invalid_xml = '<Invalid XML Content'
        
        result = self.parser.parse(invalid_xml, 'xml')
        
        assert result is None
