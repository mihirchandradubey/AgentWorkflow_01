"""Mapping engine for Pega to Camunda element conversion."""

from typing import Dict, Any, Optional
import logging

from ..utils.config_loader import ConfigLoader

logger = logging.getLogger(__name__)


class MappingEngine:
    """Engine for mapping Pega elements to Camunda equivalents."""

    def __init__(self, config_loader: Optional[ConfigLoader] = None):
        """Initialize mapping engine with config loader."""
        self.config_loader = config_loader or ConfigLoader()
        self.mapping_rules = self.config_loader.mapping_rules

    def map_element(self, pega_element: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map a Pega element to its Camunda equivalent.
        
        Args:
            pega_element: Pega element data
            
        Returns:
            Camunda element configuration
        """
        pega_type = pega_element.get('type', '')
        
        # Get mapping configuration
        mapping = self._get_mapping_for_type(pega_type)
        
        if not mapping:
            logger.warning(f"No mapping found for Pega type: {pega_type}")
            return self._create_default_mapping(pega_element)

        # Create Camunda element based on mapping
        camunda_element = {
            'id': self._generate_id(pega_element),
            'name': pega_element.get('name', ''),
            'type': mapping.get('camunda_type', 'task'),
            'properties': {}
        }

        # Apply property mappings
        property_mappings = mapping.get('property_mappings', {})
        for pega_prop, camunda_prop in property_mappings.items():
            if pega_prop in pega_element.get('properties', {}):
                camunda_element['properties'][camunda_prop] = \
                    pega_element['properties'][pega_prop]

        # Apply custom transformations
        if 'transform' in mapping:
            camunda_element = self._apply_transform(
                camunda_element, pega_element, mapping['transform']
            )

        return camunda_element

    def _get_mapping_for_type(self, pega_type: str) -> Optional[Dict[str, Any]]:
        """Get mapping configuration for a Pega type."""
        element_mappings = self.mapping_rules.get('element_mappings', {})
        return element_mappings.get(pega_type)

    def _generate_id(self, pega_element: Dict[str, Any]) -> str:
        """Generate Camunda-compatible ID from Pega element."""
        pega_id = pega_element.get('id', '')
        pega_type = pega_element.get('type', 'element')
        
        # Clean ID to make it BPMN-compatible
        clean_id = pega_id.replace(' ', '_').replace('-', '_')
        if not clean_id:
            clean_id = f"{pega_type}_{id(pega_element)}"
        
        return clean_id

    def _create_default_mapping(self, pega_element: Dict[str, Any]) -> Dict[str, Any]:
        """Create a default mapping for unmapped element types."""
        return {
            'id': self._generate_id(pega_element),
            'name': pega_element.get('name', 'Unmapped Element'),
            'type': 'task',
            'properties': {
                'original_pega_type': pega_element.get('type', 'unknown'),
                'manual_review_required': True
            }
        }

    def _apply_transform(self, camunda_element: Dict[str, Any], 
                        pega_element: Dict[str, Any], 
                        transform_config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply custom transformations to mapped element."""
        # Placeholder for custom transformation logic
        # This can be extended with Jinja2 templates or Python code execution
        
        if transform_config.get('add_candidate_groups'):
            assignee = pega_element.get('assignee', '')
            if assignee:
                camunda_element['properties']['candidateGroups'] = assignee

        if transform_config.get('convert_to_dmn'):
            # Mark that this should generate a DMN table
            camunda_element['properties']['dmn_required'] = True
            camunda_element['properties']['decision_ref'] = \
                f"decision_{camunda_element['id']}"

        return camunda_element

    def map_connector(self, pega_connector: Dict[str, Any]) -> Dict[str, Any]:
        """Map a Pega connector to Camunda sequence flow."""
        return {
            'id': f"flow_{pega_connector.get('id', '')}",
            'sourceRef': pega_connector.get('source', ''),
            'targetRef': pega_connector.get('target', ''),
            'name': pega_connector.get('name', ''),
            'condition': pega_connector.get('condition', '')
        }

    def map_sla_to_timer(self, sla_rule: Dict[str, Any]) -> Dict[str, Any]:
        """Map Pega SLA rule to Camunda timer boundary event."""
        duration = sla_rule.get('duration', '1')
        unit = sla_rule.get('unit', 'hours')
        
        # Convert to ISO 8601 duration format
        iso_duration = self._convert_to_iso_duration(duration, unit)
        
        return {
            'id': f"timer_{sla_rule.get('name', 'sla')}",
            'name': sla_rule.get('name', 'SLA Timer'),
            'type': 'boundaryEvent',
            'timerType': 'timeDuration',
            'timeDuration': iso_duration
        }

    def _convert_to_iso_duration(self, duration: str, unit: str) -> str:
        """Convert duration to ISO 8601 format."""
        unit_map = {
            'seconds': 'S',
            'minutes': 'M',
            'hours': 'H',
            'days': 'D'
        }
        
        iso_unit = unit_map.get(unit.lower(), 'H')
        return f"PT{duration}{iso_unit}"
