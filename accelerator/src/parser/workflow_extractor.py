"""Workflow extractor to extract and organize workflow components."""

from typing import Dict, Any, List, Set
import logging

logger = logging.getLogger(__name__)


class WorkflowExtractor:
    """Extract and organize workflow components from parsed Pega data."""

    def __init__(self, workflow_data: Dict[str, Any]):
        """Initialize with parsed workflow data."""
        self.workflow_data = workflow_data
        self.name = workflow_data.get('name', 'UnnamedWorkflow')
        self.elements = workflow_data.get('elements', [])
        self.connectors = workflow_data.get('connectors', [])

    def get_start_elements(self) -> List[Dict[str, Any]]:
        """Identify start elements (elements with no incoming connectors)."""
        element_ids = {elem['id'] for elem in self.elements}
        target_ids = {conn['target'] for conn in self.connectors if conn.get('target')}
        
        start_ids = element_ids - target_ids
        return [elem for elem in self.elements if elem['id'] in start_ids]

    def get_end_elements(self) -> List[Dict[str, Any]]:
        """Identify end elements (elements with no outgoing connectors)."""
        element_ids = {elem['id'] for elem in self.elements}
        source_ids = {conn['source'] for conn in self.connectors if conn.get('source')}
        
        end_ids = element_ids - source_ids
        return [elem for elem in self.elements if elem['id'] in end_ids]

    def get_element_by_id(self, element_id: str) -> Dict[str, Any]:
        """Get element by ID."""
        for elem in self.elements:
            if elem['id'] == element_id:
                return elem
        return {}

    def get_outgoing_connectors(self, element_id: str) -> List[Dict[str, Any]]:
        """Get outgoing connectors from an element."""
        return [conn for conn in self.connectors if conn.get('source') == element_id]

    def get_incoming_connectors(self, element_id: str) -> List[Dict[str, Any]]:
        """Get incoming connectors to an element."""
        return [conn for conn in self.connectors if conn.get('target') == element_id]

    def get_elements_by_type(self, element_type: str) -> List[Dict[str, Any]]:
        """Get all elements of a specific type."""
        return [elem for elem in self.elements if elem.get('type') == element_type]

    def get_workflow_paths(self) -> List[List[str]]:
        """Extract all possible paths through the workflow."""
        paths = []
        start_elements = self.get_start_elements()

        for start_elem in start_elements:
            self._trace_paths(start_elem['id'], [], paths, set())

        return paths

    def _trace_paths(self, current_id: str, current_path: List[str], 
                     all_paths: List[List[str]], visited: Set[str]):
        """Recursively trace paths through workflow."""
        if current_id in visited:
            return  # Avoid cycles

        visited.add(current_id)
        current_path = current_path + [current_id]

        outgoing = self.get_outgoing_connectors(current_id)
        
        if not outgoing:
            # End of path
            all_paths.append(current_path)
        else:
            for conn in outgoing:
                target_id = conn.get('target')
                if target_id:
                    self._trace_paths(target_id, current_path, all_paths, visited.copy())

    def get_sla_rules(self) -> List[Dict[str, Any]]:
        """Get all SLA rules."""
        return self.workflow_data.get('metadata', {}).get('sla_rules', [])

    def get_routing_rules(self) -> List[Dict[str, Any]]:
        """Get all routing rules."""
        return self.workflow_data.get('metadata', {}).get('routing_rules', [])

    def get_decision_elements(self) -> List[Dict[str, Any]]:
        """Get all decision elements."""
        return self.get_elements_by_type('Decision')

    def get_subprocess_elements(self) -> List[Dict[str, Any]]:
        """Get all subprocess elements."""
        subprocess_types = ['SubProcess', 'SubFlow']
        elements = []
        for elem_type in subprocess_types:
            elements.extend(self.get_elements_by_type(elem_type))
        return elements

    def get_complexity_metrics(self) -> Dict[str, Any]:
        """Calculate basic complexity metrics."""
        return {
            'total_elements': len(self.elements),
            'total_connectors': len(self.connectors),
            'decision_points': len(self.get_decision_elements()),
            'start_elements': len(self.get_start_elements()),
            'end_elements': len(self.get_end_elements()),
            'subprocess_count': len(self.get_subprocess_elements()),
            'sla_rules_count': len(self.get_sla_rules()),
            'routing_rules_count': len(self.get_routing_rules())
        }
