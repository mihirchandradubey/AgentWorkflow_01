"""Schema validator for XML schema validation."""

from typing import Optional
from lxml import etree
import logging
import os

from ..utils.xml_utils import XMLUtils

logger = logging.getLogger(__name__)


class SchemaValidator:
    """Validate XML against XSD schemas."""

    def __init__(self, schema_dir: Optional[str] = None):
        """Initialize schema validator."""
        self.xml_utils = XMLUtils()
        self.schema_dir = schema_dir
        self.bpmn_schema = None
        self.dmn_schema = None

    def validate_bpmn(self, bpmn_xml: str) -> tuple[bool, Optional[str]]:
        """
        Validate BPMN XML against BPMN 2.0 schema.
        
        Args:
            bpmn_xml: BPMN XML string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            root = self.xml_utils.parse_xml(bpmn_xml)
            if root is None:
                return False, "Invalid XML format"
            
            # Note: Full schema validation requires BPMN 2.0 XSD files
            # For now, we do basic XML well-formedness check
            # In production, load and validate against official BPMN 2.0 schema
            
            return True, None
            
        except Exception as e:
            logger.error(f"BPMN validation error: {e}")
            return False, str(e)

    def validate_dmn(self, dmn_xml: str) -> tuple[bool, Optional[str]]:
        """
        Validate DMN XML against DMN 1.3 schema.
        
        Args:
            dmn_xml: DMN XML string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            root = self.xml_utils.parse_xml(dmn_xml)
            if root is None:
                return False, "Invalid XML format"
            
            # Note: Full schema validation requires DMN 1.3 XSD files
            # For now, we do basic XML well-formedness check
            
            return True, None
            
        except Exception as e:
            logger.error(f"DMN validation error: {e}")
            return False, str(e)

    def validate_against_schema(self, xml_content: str, 
                               schema_path: str) -> tuple[bool, Optional[str]]:
        """
        Validate XML against a specific schema file.
        
        Args:
            xml_content: XML string to validate
            schema_path: Path to XSD schema file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not os.path.exists(schema_path):
                return False, f"Schema file not found: {schema_path}"
            
            # Parse XML
            root = self.xml_utils.parse_xml(xml_content)
            if root is None:
                return False, "Invalid XML format"
            
            # Load schema
            with open(schema_path, 'rb') as f:
                schema_root = etree.XML(f.read())
            schema = etree.XMLSchema(schema_root)
            
            # Validate
            if schema.validate(root):
                return True, None
            else:
                error_log = schema.error_log
                errors = [str(error) for error in error_log]
                return False, "; ".join(errors)
                
        except Exception as e:
            logger.error(f"Schema validation error: {e}")
            return False, str(e)
