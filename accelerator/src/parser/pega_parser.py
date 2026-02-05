"""Pega workflow parser for XML/JSON exports."""

import json
from typing import Dict, Any, Optional, List
from lxml import etree
import logging

from ..utils.xml_utils import XMLUtils

logger = logging.getLogger(__name__)


class PegaParser:
    """Parse Pega workflow exports (XML/JSON)."""

    def __init__(self):
        """Initialize Pega parser."""
        self.xml_utils = XMLUtils()

    def parse(self, content: str, format_type: str = 'xml') -> Optional[Dict[str, Any]]:
        """
        Parse Pega workflow content.
        
        Args:
            content: Pega workflow content (XML or JSON string)
            format_type: Format type ('xml' or 'json')
            
        Returns:
            Parsed workflow data as dictionary
        """
        if format_type == 'xml':
            return self._parse_xml(content)
        elif format_type == 'json':
            return self._parse_json(content)
        else:
            logger.error(f"Unsupported format type: {format_type}")
            return None

    def parse_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Parse Pega workflow from file.
        
        Args:
            file_path: Path to Pega workflow file
            
        Returns:
            Parsed workflow data as dictionary
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Detect format based on file extension or content
            if file_path.endswith('.json'):
                return self._parse_json(content)
            else:
                return self._parse_xml(content)
        except IOError as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None

    def _parse_xml(self, xml_content: str) -> Optional[Dict[str, Any]]:
        """Parse Pega XML format."""
        root = self.xml_utils.parse_xml(xml_content)
        if root is None:
            return None

        workflow_data = {
            'name': root.get('name', 'UnnamedWorkflow'),
            'type': 'pega_workflow',
            'metadata': {},
            'elements': [],
            'connectors': [],
            'case_types': [],
            'stages': []
        }

        # Extract metadata
        workflow_data['metadata'] = self._extract_metadata(root)

        # Extract workflow elements (flow actions, assignments, etc.)
        workflow_data['elements'] = self._extract_elements(root)

        # Extract connectors
        workflow_data['connectors'] = self._extract_connectors(root)

        # Extract case types and stages
        workflow_data['case_types'] = self._extract_case_types(root)
        workflow_data['stages'] = self._extract_stages(root)

        return workflow_data

    def _parse_json(self, json_content: str) -> Optional[Dict[str, Any]]:
        """Parse Pega JSON format."""
        try:
            data = json.loads(json_content)
            
            workflow_data = {
                'name': data.get('name', 'UnnamedWorkflow'),
                'type': 'pega_workflow',
                'metadata': data.get('metadata', {}),
                'elements': data.get('elements', []),
                'connectors': data.get('connectors', []),
                'case_types': data.get('caseTypes', []),
                'stages': data.get('stages', [])
            }
            
            return workflow_data
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return None

    def _extract_metadata(self, root: etree._Element) -> Dict[str, Any]:
        """Extract workflow metadata."""
        metadata = {
            'description': root.get('description', ''),
            'version': root.get('version', '1.0'),
            'sla_rules': [],
            'routing_rules': [],
            'data_transforms': []
        }

        # Extract SLA rules
        sla_elements = root.findall('.//SLA') or []
        for sla in sla_elements:
            metadata['sla_rules'].append({
                'name': sla.get('name', ''),
                'duration': sla.get('duration', ''),
                'unit': sla.get('unit', 'hours')
            })

        # Extract routing rules
        routing_elements = root.findall('.//RoutingRule') or []
        for rule in routing_elements:
            metadata['routing_rules'].append({
                'name': rule.get('name', ''),
                'condition': rule.get('condition', ''),
                'target': rule.get('target', '')
            })

        return metadata

    def _extract_elements(self, root: etree._Element) -> List[Dict[str, Any]]:
        """Extract workflow elements."""
        elements = []

        # Extract flow actions
        flow_actions = root.findall('.//FlowAction') or []
        for action in flow_actions:
            elements.append({
                'id': action.get('id', ''),
                'name': action.get('name', ''),
                'type': 'FlowAction',
                'properties': self._extract_properties(action)
            })

        # Extract assignments
        assignments = root.findall('.//Assignment') or []
        for assignment in assignments:
            elements.append({
                'id': assignment.get('id', ''),
                'name': assignment.get('name', ''),
                'type': 'Assignment',
                'assignee': assignment.get('assignee', ''),
                'properties': self._extract_properties(assignment)
            })

        # Extract decision rules
        decisions = root.findall('.//Decision') or []
        for decision in decisions:
            elements.append({
                'id': decision.get('id', ''),
                'name': decision.get('name', ''),
                'type': 'Decision',
                'rule': decision.get('rule', ''),
                'properties': self._extract_properties(decision)
            })

        # Extract wait shapes
        wait_shapes = root.findall('.//Wait') or []
        for wait in wait_shapes:
            elements.append({
                'id': wait.get('id', ''),
                'name': wait.get('name', ''),
                'type': 'Wait',
                'duration': wait.get('duration', ''),
                'properties': self._extract_properties(wait)
            })

        return elements

    def _extract_connectors(self, root: etree._Element) -> List[Dict[str, Any]]:
        """Extract connectors between elements."""
        connectors = []
        
        connector_elements = root.findall('.//Connector') or []
        for connector in connector_elements:
            connectors.append({
                'id': connector.get('id', ''),
                'source': connector.get('source', ''),
                'target': connector.get('target', ''),
                'type': connector.get('type', 'sequence'),
                'condition': connector.get('condition', '')
            })

        return connectors

    def _extract_case_types(self, root: etree._Element) -> List[Dict[str, Any]]:
        """Extract case types."""
        case_types = []
        
        case_type_elements = root.findall('.//CaseType') or []
        for case_type in case_type_elements:
            case_types.append({
                'id': case_type.get('id', ''),
                'name': case_type.get('name', ''),
                'description': case_type.get('description', '')
            })

        return case_types

    def _extract_stages(self, root: etree._Element) -> List[Dict[str, Any]]:
        """Extract workflow stages."""
        stages = []
        
        stage_elements = root.findall('.//Stage') or []
        for stage in stage_elements:
            stages.append({
                'id': stage.get('id', ''),
                'name': stage.get('name', ''),
                'order': int(stage.get('order', '0')),
                'steps': self._extract_stage_steps(stage)
            })

        return stages

    def _extract_stage_steps(self, stage: etree._Element) -> List[Dict[str, Any]]:
        """Extract steps within a stage."""
        steps = []
        
        step_elements = stage.findall('.//Step') or []
        for step in step_elements:
            steps.append({
                'id': step.get('id', ''),
                'name': step.get('name', ''),
                'type': step.get('type', '')
            })

        return steps

    def _extract_properties(self, element: etree._Element) -> Dict[str, Any]:
        """Extract properties from an element."""
        properties = {}
        
        for child in element:
            if child.tag == 'Property':
                name = child.get('name', '')
                value = child.get('value', child.text or '')
                properties[name] = value

        return properties
