"""Shared pytest configuration and fixtures."""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def sample_workflow_data():
    """Fixture providing sample workflow data."""
    return {
        'name': 'SampleWorkflow',
        'type': 'pega_workflow',
        'metadata': {
            'description': 'Sample workflow for testing',
            'version': '1.0',
            'sla_rules': [],
            'routing_rules': []
        },
        'elements': [
            {
                'id': 'FA001',
                'name': 'Submit Request',
                'type': 'FlowAction',
                'properties': {}
            },
            {
                'id': 'ASN001',
                'name': 'Approve Request',
                'type': 'Assignment',
                'assignee': 'approvers',
                'properties': {}
            }
        ],
        'connectors': [
            {
                'id': 'C001',
                'source': 'FA001',
                'target': 'ASN001',
                'type': 'sequence'
            }
        ],
        'case_types': [],
        'stages': []
    }
