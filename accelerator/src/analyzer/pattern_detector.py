"""Pattern detector for identifying common workflow patterns."""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class PatternDetector:
    """Detect common workflow patterns and anti-patterns."""

    def __init__(self):
        """Initialize pattern detector."""
        self.patterns = {
            'sequential': self._detect_sequential,
            'parallel': self._detect_parallel,
            'conditional': self._detect_conditional,
            'loop': self._detect_loop,
            'approval': self._detect_approval,
            'escalation': self._detect_escalation
        }
        
        self.anti_patterns = {
            'spaghetti': self._detect_spaghetti,
            'god_object': self._detect_god_object,
            'dead_end': self._detect_dead_end,
            'redundant_gateway': self._detect_redundant_gateway
        }

    def detect(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect patterns and anti-patterns in workflow.
        
        Args:
            workflow_data: Parsed workflow data
            
        Returns:
            Pattern detection results
        """
        detected_patterns = {}
        detected_anti_patterns = {}
        
        # Detect patterns
        for pattern_name, detector_func in self.patterns.items():
            result = detector_func(workflow_data)
            if result:
                detected_patterns[pattern_name] = result
        
        # Detect anti-patterns
        for anti_pattern_name, detector_func in self.anti_patterns.items():
            result = detector_func(workflow_data)
            if result:
                detected_anti_patterns[anti_pattern_name] = result
        
        return {
            'patterns': detected_patterns,
            'anti_patterns': detected_anti_patterns,
            'recommendations': self._generate_pattern_recommendations(
                detected_patterns, detected_anti_patterns
            )
        }

    def _detect_sequential(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect sequential execution pattern."""
        elements = workflow_data.get('elements', [])
        connectors = workflow_data.get('connectors', [])
        
        # Check if mostly linear flow (few branches)
        branch_points = [e for e in elements if e.get('type') in ['Decision', 'Gateway']]
        
        if len(branch_points) <= 1 and len(elements) > 2:
            return {
                'detected': True,
                'confidence': 'high',
                'description': 'Linear sequential workflow with minimal branching',
                'element_count': len(elements)
            }
        
        return None

    def _detect_parallel(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect parallel execution pattern."""
        elements = workflow_data.get('elements', [])
        
        # Look for parallel gateway patterns
        parallel_gateways = [e for e in elements if 'Parallel' in e.get('type', '')]
        
        if parallel_gateways:
            return {
                'detected': True,
                'confidence': 'high',
                'description': 'Parallel execution pattern detected',
                'gateway_count': len(parallel_gateways)
            }
        
        # Check for multiple outgoing connectors from single element
        connectors = workflow_data.get('connectors', [])
        source_counts = {}
        for conn in connectors:
            source = conn.get('source', '')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        parallel_sources = [s for s, count in source_counts.items() if count > 1]
        
        if len(parallel_sources) >= 2:
            return {
                'detected': True,
                'confidence': 'medium',
                'description': 'Potential parallel execution pattern',
                'parallel_split_count': len(parallel_sources)
            }
        
        return None

    def _detect_conditional(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect conditional branching pattern."""
        elements = workflow_data.get('elements', [])
        
        decision_elements = [e for e in elements if e.get('type') == 'Decision']
        
        if decision_elements:
            return {
                'detected': True,
                'confidence': 'high',
                'description': 'Conditional branching pattern',
                'decision_count': len(decision_elements),
                'decisions': [d.get('name', 'Unnamed') for d in decision_elements]
            }
        
        return None

    def _detect_loop(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect loop/iteration pattern."""
        connectors = workflow_data.get('connectors', [])
        elements = workflow_data.get('elements', [])
        
        # Build graph and check for back edges
        graph = {}
        for elem in elements:
            graph[elem['id']] = []
        
        for conn in connectors:
            source = conn.get('source', '')
            target = conn.get('target', '')
            if source in graph:
                graph[source].append(target)
        
        # Simple cycle detection
        def has_cycle(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        visited = set()
        for node in graph:
            if node not in visited:
                if has_cycle(node, visited, set()):
                    return {
                        'detected': True,
                        'confidence': 'high',
                        'description': 'Loop/iteration pattern detected',
                        'warning': 'Loops need careful review in BPMN migration'
                    }
        
        return None

    def _detect_approval(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect approval workflow pattern."""
        elements = workflow_data.get('elements', [])
        
        # Look for assignment tasks with approval-related names
        approval_keywords = ['approv', 'review', 'sign', 'authorize']
        
        approval_tasks = []
        for elem in elements:
            name = elem.get('name', '').lower()
            elem_type = elem.get('type', '')
            
            if elem_type in ['Assignment', 'FlowAction', 'UserTask']:
                if any(keyword in name for keyword in approval_keywords):
                    approval_tasks.append(elem)
        
        if approval_tasks:
            return {
                'detected': True,
                'confidence': 'medium',
                'description': 'Approval workflow pattern',
                'approval_task_count': len(approval_tasks),
                'tasks': [t.get('name', 'Unnamed') for t in approval_tasks]
            }
        
        return None

    def _detect_escalation(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect escalation pattern (SLA-based)."""
        metadata = workflow_data.get('metadata', {})
        sla_rules = metadata.get('sla_rules', [])
        
        if sla_rules:
            return {
                'detected': True,
                'confidence': 'high',
                'description': 'Escalation pattern with SLA rules',
                'sla_count': len(sla_rules),
                'sla_rules': [s.get('name', 'Unnamed') for s in sla_rules]
            }
        
        return None

    def _detect_spaghetti(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect spaghetti code anti-pattern (overly complex flow)."""
        elements = workflow_data.get('elements', [])
        connectors = workflow_data.get('connectors', [])
        
        # High ratio of connectors to elements suggests spaghetti
        if elements:
            ratio = len(connectors) / len(elements)
            
            if ratio > 1.5 and len(elements) > 10:
                return {
                    'detected': True,
                    'severity': 'medium',
                    'description': 'Overly complex workflow structure',
                    'connector_to_element_ratio': round(ratio, 2),
                    'recommendation': 'Consider breaking into smaller subprocesses'
                }
        
        return None

    def _detect_god_object(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect god object anti-pattern (single element doing too much)."""
        elements = workflow_data.get('elements', [])
        
        for elem in elements:
            properties = elem.get('properties', {})
            
            # Check if element has excessive properties/responsibilities
            if len(properties) > 10:
                return {
                    'detected': True,
                    'severity': 'low',
                    'description': 'Element with too many responsibilities',
                    'element_name': elem.get('name', 'Unnamed'),
                    'property_count': len(properties),
                    'recommendation': 'Consider splitting into multiple tasks'
                }
        
        return None

    def _detect_dead_end(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect dead-end paths (elements with no outgoing flows)."""
        elements = workflow_data.get('elements', [])
        connectors = workflow_data.get('connectors', [])
        
        sources = {conn.get('source') for conn in connectors}
        element_ids = {elem.get('id') for elem in elements}
        
        dead_ends = element_ids - sources
        
        # Exclude legitimate end points
        if len(dead_ends) > 1:  # More than one end point is suspicious
            return {
                'detected': True,
                'severity': 'medium',
                'description': 'Multiple dead-end paths detected',
                'dead_end_count': len(dead_ends),
                'recommendation': 'Review workflow termination points'
            }
        
        return None

    def _detect_redundant_gateway(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect redundant gateways (gateway with single outgoing path)."""
        elements = workflow_data.get('elements', [])
        connectors = workflow_data.get('connectors', [])
        
        gateways = [e for e in elements if 'Gateway' in e.get('type', '') or e.get('type') == 'Decision']
        
        redundant = []
        for gateway in gateways:
            gateway_id = gateway.get('id')
            outgoing = [c for c in connectors if c.get('source') == gateway_id]
            
            if len(outgoing) <= 1:
                redundant.append(gateway)
        
        if redundant:
            return {
                'detected': True,
                'severity': 'low',
                'description': 'Redundant gateways detected',
                'count': len(redundant),
                'recommendation': 'Remove gateways with single outgoing path'
            }
        
        return None

    def _generate_pattern_recommendations(self, patterns: Dict[str, Any], 
                                         anti_patterns: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on detected patterns."""
        recommendations = []
        
        if 'approval' in patterns:
            recommendations.append(
                "Approval pattern detected. Use Camunda user tasks with candidate groups "
                "for proper task assignment."
            )
        
        if 'parallel' in patterns:
            recommendations.append(
                "Parallel pattern detected. Use Camunda parallel gateways to properly "
                "model concurrent execution."
            )
        
        if 'escalation' in patterns:
            recommendations.append(
                "Escalation pattern with SLA rules. Map to Camunda timer boundary events "
                "with escalation handling."
            )
        
        if 'loop' in patterns:
            recommendations.append(
                "Loop pattern detected. Use BPMN loop markers or multi-instance activities "
                "in Camunda. Review carefully for correctness."
            )
        
        if 'spaghetti' in anti_patterns:
            recommendations.append(
                "⚠️  Complex workflow structure detected. Consider refactoring into "
                "smaller, more maintainable subprocesses."
            )
        
        if 'dead_end' in anti_patterns:
            recommendations.append(
                "⚠️  Multiple termination points detected. Ensure all paths properly "
                "end with end events in BPMN."
            )
        
        return recommendations
