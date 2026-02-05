"""DMN (Decision Model and Notation) generator for decision logic."""

from typing import Dict, Any, List, Optional
from lxml import etree
import logging

from ..utils.xml_utils import XMLUtils

logger = logging.getLogger(__name__)


class DMNGenerator:
    """Generate DMN 1.3 XML for Camunda decision tables."""

    DMN_NS = "https://www.omg.org/spec/DMN/20191111/MODEL/"
    DMNDI_NS = "https://www.omg.org/spec/DMN/20191111/DMNDI/"
    DC_NS = "http://www.omg.org/spec/DD/20100524/DC"
    
    NSMAP = {
        'dmn': DMN_NS,
        'dmndi': DMNDI_NS,
        'dc': DC_NS,
        'camunda': XMLUtils.CAMUNDA_NS
    }

    def __init__(self):
        """Initialize DMN generator."""
        self.xml_utils = XMLUtils()

    def generate(self, decision_data: Dict[str, Any]) -> str:
        """
        Generate DMN 1.3 XML from decision data.
        
        Args:
            decision_data: Decision logic data from Pega
            
        Returns:
            DMN 1.3 XML string
        """
        # Create root definitions element
        definitions = self._create_definitions(decision_data)
        
        # Create decision element
        decision = self._create_decision(decision_data, definitions)
        
        # Create decision table
        self._create_decision_table(decision_data, decision)
        
        return self.xml_utils.to_string(definitions)

    def _create_definitions(self, decision_data: Dict[str, Any]) -> etree._Element:
        """Create DMN definitions root element."""
        definitions = etree.Element(
            f"{{{self.DMN_NS}}}definitions",
            nsmap=self.NSMAP,
            attrib={
                'id': 'definitions',
                'namespace': 'http://camunda.org/schema/1.0/dmn',
                'name': decision_data.get('name', 'Decision'),
                'exporter': 'Pega-to-Camunda Migration Accelerator',
                'exporterVersion': '1.0'
            }
        )
        return definitions

    def _create_decision(self, decision_data: Dict[str, Any], 
                        definitions: etree._Element) -> etree._Element:
        """Create DMN decision element."""
        decision_id = decision_data.get('id', 'decision_1')
        
        decision = etree.SubElement(
            definitions,
            f"{{{self.DMN_NS}}}decision",
            attrib={
                'id': decision_id,
                'name': decision_data.get('name', 'Decision')
            }
        )
        
        return decision

    def _create_decision_table(self, decision_data: Dict[str, Any], 
                              decision: etree._Element):
        """Create decision table within decision element."""
        table = etree.SubElement(
            decision,
            f"{{{self.DMN_NS}}}decisionTable",
            attrib={
                'id': f"decisionTable_{decision.get('id')}",
                'hitPolicy': decision_data.get('hitPolicy', 'FIRST')
            }
        )
        
        # Add inputs
        inputs = decision_data.get('inputs', [])
        for inp in inputs:
            self._add_input(table, inp)
        
        # Add outputs
        outputs = decision_data.get('outputs', [])
        for out in outputs:
            self._add_output(table, out)
        
        # Add rules
        rules = decision_data.get('rules', [])
        for idx, rule in enumerate(rules, 1):
            self._add_rule(table, rule, idx)

    def _add_input(self, table: etree._Element, input_data: Dict[str, Any]):
        """Add input clause to decision table."""
        input_elem = etree.SubElement(
            table,
            f"{{{self.DMN_NS}}}input",
            attrib={
                'id': input_data.get('id', f"input_{id(input_data)}"),
                'label': input_data.get('label', 'Input')
            }
        )
        
        input_expr = etree.SubElement(
            input_elem,
            f"{{{self.DMN_NS}}}inputExpression",
            attrib={
                'id': f"inputExpression_{id(input_data)}",
                'typeRef': input_data.get('type', 'string')
            }
        )
        
        text = etree.SubElement(
            input_expr,
            f"{{{self.DMN_NS}}}text"
        )
        text.text = input_data.get('expression', '')

    def _add_output(self, table: etree._Element, output_data: Dict[str, Any]):
        """Add output clause to decision table."""
        output_elem = etree.SubElement(
            table,
            f"{{{self.DMN_NS}}}output",
            attrib={
                'id': output_data.get('id', f"output_{id(output_data)}"),
                'label': output_data.get('label', 'Output'),
                'name': output_data.get('name', 'result'),
                'typeRef': output_data.get('type', 'string')
            }
        )

    def _add_rule(self, table: etree._Element, rule_data: Dict[str, Any], rule_num: int):
        """Add rule to decision table."""
        rule = etree.SubElement(
            table,
            f"{{{self.DMN_NS}}}rule",
            attrib={
                'id': f"rule_{rule_num}"
            }
        )
        
        # Add input entries
        for input_entry in rule_data.get('inputEntries', []):
            entry = etree.SubElement(
                rule,
                f"{{{self.DMN_NS}}}inputEntry",
                attrib={'id': f"inputEntry_{rule_num}_{id(input_entry)}"}
            )
            text = etree.SubElement(entry, f"{{{self.DMN_NS}}}text")
            text.text = input_entry.get('expression', '')
        
        # Add output entries
        for output_entry in rule_data.get('outputEntries', []):
            entry = etree.SubElement(
                rule,
                f"{{{self.DMN_NS}}}outputEntry",
                attrib={'id': f"outputEntry_{rule_num}_{id(output_entry)}"}
            )
            text = etree.SubElement(entry, f"{{{self.DMN_NS}}}text")
            text.text = output_entry.get('expression', '')

    def generate_from_pega_decision(self, pega_decision: Dict[str, Any]) -> str:
        """
        Generate DMN from Pega decision element.
        
        Args:
            pega_decision: Pega decision element data
            
        Returns:
            DMN XML string
        """
        # Convert Pega decision format to DMN format
        decision_data = {
            'id': pega_decision.get('id', 'decision_1'),
            'name': pega_decision.get('name', 'Decision'),
            'hitPolicy': 'FIRST',
            'inputs': self._extract_inputs_from_pega(pega_decision),
            'outputs': self._extract_outputs_from_pega(pega_decision),
            'rules': self._extract_rules_from_pega(pega_decision)
        }
        
        return self.generate(decision_data)

    def _extract_inputs_from_pega(self, pega_decision: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract input clauses from Pega decision."""
        inputs = []
        
        # Extract from decision properties or rule conditions
        rule = pega_decision.get('rule', '')
        properties = pega_decision.get('properties', {})
        
        # Simple extraction - can be enhanced based on actual Pega format
        if 'conditions' in properties:
            for idx, condition in enumerate(properties['conditions']):
                inputs.append({
                    'id': f"input_{idx + 1}",
                    'label': condition.get('name', f'Input {idx + 1}'),
                    'expression': condition.get('field', ''),
                    'type': condition.get('type', 'string')
                })
        
        return inputs

    def _extract_outputs_from_pega(self, pega_decision: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract output clauses from Pega decision."""
        return [{
            'id': 'output_1',
            'label': 'Result',
            'name': 'result',
            'type': 'string'
        }]

    def _extract_rules_from_pega(self, pega_decision: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract decision rules from Pega decision."""
        rules = []
        
        properties = pega_decision.get('properties', {})
        pega_rules = properties.get('rules', [])
        
        for rule in pega_rules:
            rules.append({
                'inputEntries': [
                    {'expression': cond.get('expression', '')} 
                    for cond in rule.get('conditions', [])
                ],
                'outputEntries': [
                    {'expression': rule.get('result', '')}
                ]
            })
        
        return rules
