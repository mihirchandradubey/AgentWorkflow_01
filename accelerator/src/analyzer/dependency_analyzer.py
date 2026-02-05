"""Dependency analyzer for workflow dependencies."""

from typing import Dict, Any, List, Set
import logging

logger = logging.getLogger(__name__)


class DependencyAnalyzer:
    """Analyze dependencies between workflow elements and external systems."""

    def __init__(self):
        """Initialize dependency analyzer."""
        pass

    def analyze(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze workflow dependencies.
        
        Args:
            workflow_data: Parsed workflow data
            
        Returns:
            Dependency analysis results
        """
        elements = workflow_data.get('elements', [])
        
        return {
            'internal_dependencies': self._analyze_internal_dependencies(workflow_data),
            'external_dependencies': self._analyze_external_dependencies(elements),
            'data_dependencies': self._analyze_data_dependencies(workflow_data),
            'subprocess_dependencies': self._analyze_subprocess_dependencies(elements),
            'dependency_graph': self._build_dependency_graph(workflow_data)
        }

    def _analyze_internal_dependencies(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze dependencies between workflow elements."""
        connectors = workflow_data.get('connectors', [])
        elements = workflow_data.get('elements', [])
        
        # Build adjacency list
        dependencies = {}
        element_ids = {elem['id'] for elem in elements}
        
        for conn in connectors:
            source = conn.get('source', '')
            target = conn.get('target', '')
            
            if source in element_ids and target in element_ids:
                if source not in dependencies:
                    dependencies[source] = []
                dependencies[source].append(target)
        
        return {
            'element_dependencies': dependencies,
            'dependency_count': len(connectors),
            'elements_with_dependencies': len(dependencies)
        }

    def _analyze_external_dependencies(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze external system dependencies."""
        external_deps = []
        
        for elem in elements:
            elem_type = elem.get('type', '')
            properties = elem.get('properties', {})
            
            # Check for connector elements (external integrations)
            if 'Connector' in elem_type or elem_type == 'Integration':
                external_deps.append({
                    'element_id': elem.get('id', ''),
                    'element_name': elem.get('name', ''),
                    'type': elem_type,
                    'endpoint': properties.get('endpoint', 'Unknown'),
                    'method': properties.get('method', 'Unknown')
                })
        
        return {
            'external_systems': external_deps,
            'count': len(external_deps),
            'unique_endpoints': len(set(dep['endpoint'] for dep in external_deps))
        }

    def _analyze_data_dependencies(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data dependencies and data transforms."""
        metadata = workflow_data.get('metadata', {})
        data_transforms = metadata.get('data_transforms', [])
        
        return {
            'data_transforms': data_transforms,
            'transform_count': len(data_transforms)
        }

    def _analyze_subprocess_dependencies(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze subprocess dependencies."""
        subprocess_deps = []
        
        for elem in elements:
            elem_type = elem.get('type', '')
            
            if 'SubProcess' in elem_type or 'SubFlow' in elem_type:
                subprocess_deps.append({
                    'element_id': elem.get('id', ''),
                    'element_name': elem.get('name', ''),
                    'subprocess_ref': elem.get('properties', {}).get('subprocess_ref', 'Unknown')
                })
        
        return {
            'subprocesses': subprocess_deps,
            'count': len(subprocess_deps)
        }

    def _build_dependency_graph(self, workflow_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Build a complete dependency graph."""
        elements = workflow_data.get('elements', [])
        connectors = workflow_data.get('connectors', [])
        
        graph = {}
        
        # Initialize all elements in graph
        for elem in elements:
            graph[elem['id']] = []
        
        # Add connections
        for conn in connectors:
            source = conn.get('source', '')
            target = conn.get('target', '')
            
            if source in graph:
                graph[source].append(target)
        
        return graph

    def find_circular_dependencies(self, workflow_data: Dict[str, Any]) -> List[List[str]]:
        """Find circular dependencies (cycles) in workflow."""
        graph = self._build_dependency_graph(workflow_data)
        cycles = []
        
        def dfs(node: str, path: List[str], visited: Set[str]):
            if node in path:
                # Found a cycle
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            
            if node in visited:
                return
            
            visited.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                dfs(neighbor, path.copy(), visited)
        
        for node in graph:
            dfs(node, [], set())
        
        return cycles

    def get_critical_path(self, workflow_data: Dict[str, Any]) -> List[str]:
        """Identify the critical path through the workflow."""
        # Simple implementation: longest path from start to end
        graph = self._build_dependency_graph(workflow_data)
        elements = workflow_data.get('elements', [])
        
        # Find start nodes (no incoming edges)
        all_targets = set()
        for targets in graph.values():
            all_targets.update(targets)
        
        start_nodes = [node for node in graph.keys() if node not in all_targets]
        
        # Find longest path using DFS
        longest_path = []
        
        def dfs_longest(node: str, path: List[str]):
            nonlocal longest_path
            
            path = path + [node]
            
            if not graph.get(node):
                # Leaf node
                if len(path) > len(longest_path):
                    longest_path = path
                return
            
            for neighbor in graph.get(node, []):
                dfs_longest(neighbor, path)
        
        for start in start_nodes:
            dfs_longest(start, [])
        
        return longest_path

    def generate_dependency_report(self, workflow_data: Dict[str, Any]) -> str:
        """Generate a text report of dependencies."""
        analysis = self.analyze(workflow_data)
        
        report = []
        report.append("=" * 60)
        report.append("DEPENDENCY ANALYSIS REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Internal dependencies
        internal = analysis['internal_dependencies']
        report.append(f"Internal Dependencies: {internal['dependency_count']}")
        report.append(f"Elements with dependencies: {internal['elements_with_dependencies']}")
        report.append("")
        
        # External dependencies
        external = analysis['external_dependencies']
        report.append(f"External System Dependencies: {external['count']}")
        report.append(f"Unique endpoints: {external['unique_endpoints']}")
        if external['external_systems']:
            report.append("\nExternal Systems:")
            for dep in external['external_systems']:
                report.append(f"  - {dep['element_name']} → {dep['endpoint']}")
        report.append("")
        
        # Subprocess dependencies
        subprocess = analysis['subprocess_dependencies']
        report.append(f"Subprocess Dependencies: {subprocess['count']}")
        if subprocess['subprocesses']:
            report.append("Subprocesses:")
            for sp in subprocess['subprocesses']:
                report.append(f"  - {sp['element_name']} → {sp['subprocess_ref']}")
        report.append("")
        
        # Critical path
        critical_path = self.get_critical_path(workflow_data)
        report.append(f"Critical Path Length: {len(critical_path)} elements")
        report.append("")
        
        # Circular dependencies
        cycles = self.find_circular_dependencies(workflow_data)
        if cycles:
            report.append(f"⚠️  WARNING: {len(cycles)} circular dependencies detected!")
            for idx, cycle in enumerate(cycles, 1):
                report.append(f"  Cycle {idx}: {' → '.join(cycle)}")
        else:
            report.append("✓ No circular dependencies detected")
        
        report.append("=" * 60)
        
        return "\n".join(report)
