"""XML utilities for parsing and generating XML content."""

from lxml import etree
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class XMLUtils:
    """Utility class for XML operations."""

    BPMN_NS = "http://www.omg.org/spec/BPMN/20100524/MODEL"
    BPMN_DI_NS = "http://www.omg.org/spec/BPMN/20100524/DI"
    DC_NS = "http://www.omg.org/spec/DD/20100524/DC"
    DI_NS = "http://www.omg.org/spec/DD/20100524/DI"
    CAMUNDA_NS = "http://camunda.org/schema/1.0/bpmn"
    
    NSMAP = {
        'bpmn': BPMN_NS,
        'bpmndi': BPMN_DI_NS,
        'dc': DC_NS,
        'di': DI_NS,
        'camunda': CAMUNDA_NS
    }

    @staticmethod
    def parse_xml(xml_content: str) -> Optional[etree._Element]:
        """Parse XML content and return the root element."""
        try:
            parser = etree.XMLParser(remove_blank_text=True)
            root = etree.fromstring(xml_content.encode('utf-8'), parser)
            return root
        except etree.XMLSyntaxError as e:
            logger.error(f"XML parsing error: {e}")
            return None

    @staticmethod
    def parse_xml_file(file_path: str) -> Optional[etree._Element]:
        """Parse XML file and return the root element."""
        try:
            parser = etree.XMLParser(remove_blank_text=True)
            tree = etree.parse(file_path, parser)
            return tree.getroot()
        except (etree.XMLSyntaxError, IOError) as e:
            logger.error(f"Error parsing XML file {file_path}: {e}")
            return None

    @staticmethod
    def create_element(tag: str, nsmap: Optional[Dict[str, str]] = None, 
                      attrib: Optional[Dict[str, str]] = None) -> etree._Element:
        """Create an XML element with optional namespace and attributes."""
        if nsmap is None:
            nsmap = XMLUtils.NSMAP
        
        element = etree.Element(tag, nsmap=nsmap)
        if attrib:
            for key, value in attrib.items():
                element.set(key, value)
        return element

    @staticmethod
    def to_string(element: etree._Element, pretty_print: bool = True) -> str:
        """Convert XML element to string."""
        return etree.tostring(
            element, 
            pretty_print=pretty_print, 
            xml_declaration=True, 
            encoding='UTF-8'
        ).decode('utf-8')

    @staticmethod
    def validate_xml(xml_content: str, schema_path: Optional[str] = None) -> bool:
        """Validate XML against a schema."""
        try:
            root = XMLUtils.parse_xml(xml_content)
            if root is None:
                return False
            
            if schema_path:
                with open(schema_path, 'r') as f:
                    schema_root = etree.XML(f.read().encode('utf-8'))
                schema = etree.XMLSchema(schema_root)
                return schema.validate(root)
            
            return True
        except Exception as e:
            logger.error(f"XML validation error: {e}")
            return False

    @staticmethod
    def get_namespace(element: etree._Element) -> str:
        """Extract namespace from an element."""
        return element.nsmap.get(None, '')

    @staticmethod
    def find_elements(root: etree._Element, xpath: str, 
                      namespaces: Optional[Dict[str, str]] = None) -> list:
        """Find elements using XPath."""
        if namespaces is None:
            namespaces = XMLUtils.NSMAP
        return root.xpath(xpath, namespaces=namespaces)
