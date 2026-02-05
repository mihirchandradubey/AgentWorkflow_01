"""BPMN 2.0 XML generator for Camunda."""

from typing import Dict, Any, List, Optional
from lxml import etree
import logging

from ..utils.xml_utils import XMLUtils
from .mapping_engine import MappingEngine

logger = logging.getLogger(__name__)


class BPMNGenerator:
    """Generate BPMN 2.0 XML for Camunda from mapped workflow data."""

    def __init__(self, mapping_engine: Optional[MappingEngine] = None):
        """Initialize BPMN generator."""
        self.xml_utils = XMLUtils()
        self.mapping_engine = mapping_engine or MappingEngine()
        self.element_counter = 0

    def generate(self, workflow_data: Dict[str, Any]) -> str:
        """
        Generate BPMN 2.0 XML from workflow data.
        
        Args:
            workflow_data: Parsed Pega workflow data
            
        Returns:
            BPMN 2.0 XML string
        """
        # Create root definitions element
        definitions = self._create_definitions(workflow_data)
        
        # Create process element
        process = self._create_process(workflow_data, definitions)
        
        # Add start event
        self._add_start_event(process)
        
        # Add workflow elements
        self._add_workflow_elements(workflow_data, process)
        
        # Add sequence flows
        self._add_sequence_flows(workflow_data, process)
        
        # Add end event
        self._add_end_event(process)
        
        # Add BPMN diagram information (optional but recommended)
        self._add_bpmn_diagram(definitions, process)
        
        return self.xml_utils.to_string(definitions)

    def _create_definitions(self, workflow_data: Dict[str, Any]) -> etree._Element:
        """Create BPMN definitions root element."""
        definitions = etree.Element(
            f"{{{self.xml_utils.BPMN_NS}}}definitions",
            nsmap=self.xml_utils.NSMAP,
            attrib={
                'id': 'definitions',
                'targetNamespace': 'http://bpmn.io/schema/bpmn',
                'exporter': 'Pega-to-Camunda Migration Accelerator',
                'exporterVersion': '1.0'
            }
        )
        return definitions

    def _create_process(self, workflow_data: Dict[str, Any], 
                       definitions: etree._Element) -> etree._Element:
        """Create BPMN process element."""
        process_id = self._sanitize_id(workflow_data.get('name', 'Process'))
        
        process = etree.SubElement(
            definitions,
            f"{{{self.xml_utils.BPMN_NS}}}process",
            attrib={
                'id': process_id,
                'name': workflow_data.get('name', 'Migrated Process'),
                'isExecutable': 'true'
            }
        )
        return process

    def _add_start_event(self, process: etree._Element) -> etree._Element:
        """Add start event to process."""
        start_event = etree.SubElement(
            process,
            f"{{{self.xml_utils.BPMN_NS}}}startEvent",
            attrib={
                'id': 'StartEvent_1',
                'name': 'Start'
            }
        )
        return start_event

    def _add_end_event(self, process: etree._Element) -> etree._Element:
        """Add end event to process."""
        end_event = etree.SubElement(
            process,
            f"{{{self.xml_utils.BPMN_NS}}}endEvent",
            attrib={
                'id': 'EndEvent_1',
                'name': 'End'
            }
        )
        return end_event

    def _add_workflow_elements(self, workflow_data: Dict[str, Any], 
                               process: etree._Element):
        """Add workflow elements (tasks, gateways, etc.) to process."""
        elements = workflow_data.get('elements', [])
        
        for pega_element in elements:
            camunda_element = self.mapping_engine.map_element(pega_element)
            self._add_element_to_process(camunda_element, process)

    def _add_element_to_process(self, camunda_element: Dict[str, Any], 
                                process: etree._Element):
        """Add a mapped Camunda element to the process."""
        element_type = camunda_element.get('type', 'task')
        element_id = self._sanitize_id(camunda_element.get('id', ''))
        element_name = camunda_element.get('name', '')
        
        # Map element type to BPMN element
        if element_type == 'userTask':
            self._add_user_task(process, element_id, element_name, camunda_element)
        elif element_type == 'serviceTask':
            self._add_service_task(process, element_id, element_name, camunda_element)
        elif element_type == 'businessRuleTask':
            self._add_business_rule_task(process, element_id, element_name, camunda_element)
        elif element_type == 'exclusiveGateway':
            self._add_exclusive_gateway(process, element_id, element_name)
        elif element_type == 'parallelGateway':
            self._add_parallel_gateway(process, element_id, element_name)
        elif element_type == 'intermediateCatchEvent':
            self._add_timer_event(process, element_id, element_name, camunda_element)
        else:
            # Default to generic task
            self._add_task(process, element_id, element_name)

    def _add_user_task(self, process: etree._Element, task_id: str, 
                      name: str, element_data: Dict[str, Any]):
        """Add user task to process."""
        task = etree.SubElement(
            process,
            f"{{{self.xml_utils.BPMN_NS}}}userTask",
            attrib={
                'id': task_id,
                'name': name
            }
        )
        
        # Add candidate groups if specified
        properties = element_data.get('properties', {})
        if 'candidateGroups' in properties:
            task.set(f"{{{self.xml_utils.CAMUNDA_NS}}}candidateGroups", 
                    properties['candidateGroups'])

    def _add_service_task(self, process: etree._Element, task_id: str, 
                         name: str, element_data: Dict[str, Any]):
        """Add service task to process."""
        task = etree.SubElement(
            process,
            f"{{{self.xml_utils.BPMN_NS}}}serviceTask",
            attrib={
                'id': task_id,
                'name': name
            }
        )
        
        properties = element_data.get('properties', {})
        if 'implementation' in properties:
            task.set(f"{{{self.xml_utils.CAMUNDA_NS}}}implementation", 
                    properties['implementation'])

    def _add_business_rule_task(self, process: etree._Element, task_id: str, 
                               name: str, element_data: Dict[str, Any]):
        """Add business rule task to process."""
        task = etree.SubElement(
            process,
            f"{{{self.xml_utils.BPMN_NS}}}businessRuleTask",
            attrib={
                'id': task_id,
                'name': name
            }
        )
        
        properties = element_data.get('properties', {})
        if 'decision_ref' in properties:
            task.set(f"{{{self.xml_utils.CAMUNDA_NS}}}decisionRef", 
                    properties['decision_ref'])

    def _add_exclusive_gateway(self, process: etree._Element, 
                              gateway_id: str, name: str):
        """Add exclusive gateway to process."""
        etree.SubElement(
            process,
            f"{{{self.xml_utils.BPMN_NS}}}exclusiveGateway",
            attrib={
                'id': gateway_id,
                'name': name
            }
        )

    def _add_parallel_gateway(self, process: etree._Element, 
                             gateway_id: str, name: str):
        """Add parallel gateway to process."""
        etree.SubElement(
            process,
            f"{{{self.xml_utils.BPMN_NS}}}parallelGateway",
            attrib={
                'id': gateway_id,
                'name': name
            }
        )

    def _add_timer_event(self, process: etree._Element, event_id: str, 
                        name: str, element_data: Dict[str, Any]):
        """Add intermediate timer event to process."""
        event = etree.SubElement(
            process,
            f"{{{self.xml_utils.BPMN_NS}}}intermediateCatchEvent",
            attrib={
                'id': event_id,
                'name': name
            }
        )
        
        timer_def = etree.SubElement(
            event,
            f"{{{self.xml_utils.BPMN_NS}}}timerEventDefinition"
        )
        
        properties = element_data.get('properties', {})
        if 'timeDuration' in properties:
            time_duration = etree.SubElement(
                timer_def,
                f"{{{self.xml_utils.BPMN_NS}}}timeDuration"
            )
            time_duration.text = properties['timeDuration']

    def _add_task(self, process: etree._Element, task_id: str, name: str):
        """Add generic task to process."""
        etree.SubElement(
            process,
            f"{{{self.xml_utils.BPMN_NS}}}task",
            attrib={
                'id': task_id,
                'name': name
            }
        )

    def _add_sequence_flows(self, workflow_data: Dict[str, Any], 
                           process: etree._Element):
        """Add sequence flows to process."""
        connectors = workflow_data.get('connectors', [])
        
        for connector in connectors:
            flow = self.mapping_engine.map_connector(connector)
            self._add_sequence_flow(process, flow)

    def _add_sequence_flow(self, process: etree._Element, flow_data: Dict[str, Any]):
        """Add a single sequence flow to process."""
        flow_id = self._sanitize_id(flow_data.get('id', f'Flow_{self.element_counter}'))
        self.element_counter += 1
        
        attrib = {
            'id': flow_id,
            'sourceRef': self._sanitize_id(flow_data.get('sourceRef', '')),
            'targetRef': self._sanitize_id(flow_data.get('targetRef', ''))
        }
        
        if flow_data.get('name'):
            attrib['name'] = flow_data['name']
        
        sequence_flow = etree.SubElement(
            process,
            f"{{{self.xml_utils.BPMN_NS}}}sequenceFlow",
            attrib=attrib
        )
        
        # Add condition expression if present
        if flow_data.get('condition'):
            # Create condition expression with proper namespace
            xsi_ns = "http://www.w3.org/2001/XMLSchema-instance"
            attrib = {
                f'{{{xsi_ns}}}type': 'tFormalExpression'
            }
            condition = etree.SubElement(
                sequence_flow,
                f"{{{self.xml_utils.BPMN_NS}}}conditionExpression",
                attrib=attrib,
                nsmap={'xsi': xsi_ns}
            )
            condition.text = flow_data['condition']

    def _add_bpmn_diagram(self, definitions: etree._Element, 
                         process: etree._Element):
        """Add BPMN diagram information for visual layout."""
        diagram = etree.SubElement(
            definitions,
            f"{{{self.xml_utils.BPMN_DI_NS}}}BPMNDiagram",
            attrib={'id': 'BPMNDiagram_1'}
        )
        
        plane = etree.SubElement(
            diagram,
            f"{{{self.xml_utils.BPMN_DI_NS}}}BPMNPlane",
            attrib={
                'id': 'BPMNPlane_1',
                'bpmnElement': process.get('id', '')
            }
        )
        
        # Simple layout - elements in a vertical line
        x, y = 100, 100
        spacing = 150
        
        for element in process:
            if element.tag.endswith(('startEvent', 'endEvent', 'task', 
                                    'userTask', 'serviceTask', 'businessRuleTask',
                                    'exclusiveGateway', 'parallelGateway')):
                self._add_shape(plane, element.get('id'), x, y)
                y += spacing

    def _add_shape(self, plane: etree._Element, element_id: str, x: int, y: int):
        """Add shape element to diagram plane."""
        shape = etree.SubElement(
            plane,
            f"{{{self.xml_utils.BPMN_DI_NS}}}BPMNShape",
            attrib={
                'id': f"{element_id}_di",
                'bpmnElement': element_id
            }
        )
        
        bounds = etree.SubElement(
            shape,
            f"{{{self.xml_utils.DC_NS}}}Bounds",
            attrib={
                'x': str(x),
                'y': str(y),
                'width': '100',
                'height': '80'
            }
        )

    def _sanitize_id(self, id_str: str) -> str:
        """Sanitize ID to be BPMN-compliant."""
        # Replace invalid characters
        sanitized = id_str.replace(' ', '_').replace('-', '_').replace('.', '_')
        # Ensure it starts with a letter
        if sanitized and not sanitized[0].isalpha():
            sanitized = 'id_' + sanitized
        return sanitized if sanitized else f'element_{self.element_counter}'
