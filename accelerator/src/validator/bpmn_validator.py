"""BPMN validator for checking BPMN quality and common issues."""

from typing import Dict, Any, List
from lxml import etree
import logging

from ..utils.xml_utils import XMLUtils

logger = logging.getLogger(__name__)


class BPMNValidator:
    """Validate BPMN 2.0 XML for common modeling issues."""

    def __init__(self):
        """Initialize BPMN validator."""
        self.xml_utils = XMLUtils()
        self.issues = []
        self.warnings = []

    def validate(self, bpmn_xml: str) -> Dict[str, Any]:
        """
        Validate BPMN XML.
        
        Args:
            bpmn_xml: BPMN 2.0 XML string
            
        Returns:
            Validation results
        """
        self.issues = []
        self.warnings = []
        
        root = self.xml_utils.parse_xml(bpmn_xml)
        if root is None:
            return {
                'valid': False,
                'errors': ['Invalid XML format'],
                'warnings': [],
                'suggestions': []
            }
        
        # Run validation checks
        self._check_process_elements(root)
        self._check_start_events(root)
        self._check_end_events(root)
        self._check_sequence_flows(root)
        self._check_task_names(root)
        self._check_gateway_usage(root)
        
        suggestions = self._generate_suggestions()
        
        return {
            'valid': len(self.issues) == 0,
            'errors': self.issues,
            'warnings': self.warnings,
            'suggestions': suggestions
        }

    def _check_process_elements(self, root: etree._Element):
        """Check that process elements exist and are properly configured."""
        processes = self.xml_utils.find_elements(root, '//bpmn:process')
        
        if not processes:
            self.issues.append("No process element found in BPMN")
        
        for process in processes:
            if not process.get('id'):
                self.issues.append("Process missing 'id' attribute")
            
            if not process.get('isExecutable'):
                self.warnings.append(
                    f"Process '{process.get('id')}' missing 'isExecutable' attribute"
                )

    def _check_start_events(self, root: etree._Element):
        """Check start events."""
        processes = self.xml_utils.find_elements(root, '//bpmn:process')
        
        for process in processes:
            process_id = process.get('id', 'unknown')
            start_events = process.findall(f'{{{self.xml_utils.BPMN_NS}}}startEvent')
            
            if not start_events:
                self.issues.append(f"Process '{process_id}' has no start event")
            elif len(start_events) > 1:
                self.warnings.append(
                    f"Process '{process_id}' has multiple start events ({len(start_events)})"
                )

    def _check_end_events(self, root: etree._Element):
        """Check end events."""
        processes = self.xml_utils.find_elements(root, '//bpmn:process')
        
        for process in processes:
            process_id = process.get('id', 'unknown')
            end_events = process.findall(f'{{{self.xml_utils.BPMN_NS}}}endEvent')
            
            if not end_events:
                self.warnings.append(f"Process '{process_id}' has no end event")

    def _check_sequence_flows(self, root: etree._Element):
        """Check sequence flows for dangling references."""
        processes = self.xml_utils.find_elements(root, '//bpmn:process')
        
        for process in processes:
            # Collect all element IDs
            element_ids = set()
            for elem in process:
                elem_id = elem.get('id')
                if elem_id:
                    element_ids.add(elem_id)
            
            # Check sequence flows
            flows = process.findall(f'{{{self.xml_utils.BPMN_NS}}}sequenceFlow')
            for flow in flows:
                source_ref = flow.get('sourceRef')
                target_ref = flow.get('targetRef')
                
                if source_ref and source_ref not in element_ids:
                    self.issues.append(
                        f"Sequence flow references non-existent source: {source_ref}"
                    )
                
                if target_ref and target_ref not in element_ids:
                    self.issues.append(
                        f"Sequence flow references non-existent target: {target_ref}"
                    )

    def _check_task_names(self, root: etree._Element):
        """Check that tasks have meaningful names."""
        tasks = self.xml_utils.find_elements(
            root, 
            '//bpmn:task | //bpmn:userTask | //bpmn:serviceTask | //bpmn:businessRuleTask'
        )
        
        for task in tasks:
            task_id = task.get('id', 'unknown')
            task_name = task.get('name', '')
            
            if not task_name:
                self.warnings.append(f"Task '{task_id}' has no name attribute")
            elif len(task_name) < 3:
                self.warnings.append(
                    f"Task '{task_id}' has very short name: '{task_name}'"
                )

    def _check_gateway_usage(self, root: etree._Element):
        """Check gateway usage patterns."""
        gateways = self.xml_utils.find_elements(
            root,
            '//bpmn:exclusiveGateway | //bpmn:parallelGateway | //bpmn:inclusiveGateway'
        )
        
        for gateway in gateways:
            gateway_id = gateway.get('id', 'unknown')
            
            # Check for gateway name
            if not gateway.get('name'):
                self.warnings.append(
                    f"Gateway '{gateway_id}' has no name - consider adding descriptive name"
                )

    def _generate_suggestions(self) -> List[str]:
        """Generate optimization suggestions."""
        suggestions = []
        
        if self.warnings:
            suggestions.append(
                "Address warnings to improve BPMN model quality and maintainability"
            )
        
        suggestions.append(
            "Review generated BPMN in Camunda Modeler for visual verification"
        )
        
        suggestions.append(
            "Add documentation elements (text annotations) to explain complex logic"
        )
        
        suggestions.append(
            "Consider adding execution listeners for audit logging"
        )
        
        return suggestions
