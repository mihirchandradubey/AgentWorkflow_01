"""Configuration loader for mapping rules and templates."""

import yaml
import json
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Load and manage configuration files."""

    def __init__(self, config_dir: Optional[str] = None):
        """Initialize config loader with config directory."""
        if config_dir is None:
            # Default to config directory relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            config_dir = os.path.join(base_dir, 'config')
        
        self.config_dir = config_dir
        self._mapping_rules = None
        self._transformation_templates = None
        self._validation_rules = None

    def load_yaml(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load YAML configuration file."""
        try:
            with open(file_path, 'r') as f:
                return yaml.safe_load(f)
        except (IOError, yaml.YAMLError) as e:
            logger.error(f"Error loading YAML file {file_path}: {e}")
            return None

    def load_json(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load JSON configuration file."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error loading JSON file {file_path}: {e}")
            return None

    @property
    def mapping_rules(self) -> Dict[str, Any]:
        """Get mapping rules configuration."""
        if self._mapping_rules is None:
            path = os.path.join(self.config_dir, 'mapping_rules.yaml')
            self._mapping_rules = self.load_yaml(path) or {}
        return self._mapping_rules

    @property
    def transformation_templates(self) -> Dict[str, Any]:
        """Get transformation templates configuration."""
        if self._transformation_templates is None:
            path = os.path.join(self.config_dir, 'transformation_templates.yaml')
            self._transformation_templates = self.load_yaml(path) or {}
        return self._transformation_templates

    @property
    def validation_rules(self) -> Dict[str, Any]:
        """Get validation rules configuration."""
        if self._validation_rules is None:
            path = os.path.join(self.config_dir, 'validation_rules.yaml')
            self._validation_rules = self.load_yaml(path) or {}
        return self._validation_rules

    def get_pega_to_camunda_mapping(self, pega_type: str) -> Optional[Dict[str, Any]]:
        """Get Camunda mapping for a Pega element type."""
        mappings = self.mapping_rules.get('element_mappings', {})
        return mappings.get(pega_type)

    def reload(self):
        """Reload all configuration files."""
        self._mapping_rules = None
        self._transformation_templates = None
        self._validation_rules = None
