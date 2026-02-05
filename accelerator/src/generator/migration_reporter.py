"""Migration reporting with customizable output formats."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json

class MigrationReporter:
    """Creates detailed migration reports with multiple output formats."""

    def __init__(self, workflow_name: str = "Unnamed"):
        self.workflow_name = workflow_name
        self.report_sections = []
        self.timestamp = datetime.now()

    def build_comprehensive_report(self, 
                                   source_data: Dict[str, Any],
                                   analysis_output: Dict[str, Any],
                                   validation_output: Dict[str, Any]) -> str:
        """Constructs a full migration report from all data sources."""
        
        sections = []
        
        # Header
        sections.append(self._build_header())
        
        # Executive summary
        sections.append(self._build_executive_summary(source_data, analysis_output))
        
        # Technical metrics
        sections.append(self._build_technical_metrics(source_data))
        
        # Analysis insights
        sections.append(self._build_analysis_insights(analysis_output))
        
        # Quality assessment
        sections.append(self._build_quality_assessment(validation_output))
        
        # Action items
        sections.append(self._build_action_items(analysis_output, validation_output))
        
        # Footer
        sections.append(self._build_footer())
        
        return "\n\n".join(sections)

    def _build_header(self) -> str:
        """Creates report header with metadata."""
        header_lines = [
            "╔" + "═" * 78 + "╗",
            "║" + " MIGRATION ANALYSIS REPORT".center(78) + "║",
            "║" + f" Workflow: {self.workflow_name}".ljust(78) + "║",
            "║" + f" Generated: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}".ljust(78) + "║",
            "╚" + "═" * 78 + "╝"
        ]
        return "\n".join(header_lines)

    def _build_executive_summary(self, source_data: Dict[str, Any], 
                                 analysis_output: Dict[str, Any]) -> str:
        """Creates executive summary section."""
        lines = [
            "┌─ EXECUTIVE SUMMARY " + "─" * 58 + "┐",
            ""
        ]
        
        total_items = len(source_data.get('elements', []))
        complexity_info = analysis_output.get('complexity', {})
        effort_data = complexity_info.get('effort_estimate', {})
        
        lines.append(f"  Workflow Components: {total_items}")
        lines.append(f"  Migration Complexity: {complexity_info.get('complexity_level', 'Unknown')}")
        lines.append(f"  Estimated Effort: {effort_data.get('estimated_days', 0):.1f} person-days")
        lines.append(f"  Automation Rate: {effort_data.get('automation_percentage', 0)}%")
        
        lines.append("")
        lines.append("└" + "─" * 78 + "┘")
        
        return "\n".join(lines)

    def _build_technical_metrics(self, source_data: Dict[str, Any]) -> str:
        """Creates technical metrics section."""
        lines = [
            "┌─ TECHNICAL METRICS " + "─" * 59 + "┐",
            ""
        ]
        
        items = source_data.get('elements', [])
        connections = source_data.get('connectors', [])
        
        # Count by type
        type_counts = {}
        for item in items:
            item_type = item.get('type', 'Unknown')
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
        
        lines.append(f"  Total Elements: {len(items)}")
        lines.append(f"  Total Connections: {len(connections)}")
        lines.append("")
        lines.append("  Element Distribution:")
        
        for elem_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(items) * 100) if items else 0
            lines.append(f"    • {elem_type}: {count} ({percentage:.1f}%)")
        
        lines.append("")
        lines.append("└" + "─" * 78 + "┘")
        
        return "\n".join(lines)

    def _build_analysis_insights(self, analysis_output: Dict[str, Any]) -> str:
        """Creates analysis insights section."""
        lines = [
            "┌─ ANALYSIS INSIGHTS " + "─" * 59 + "┐",
            ""
        ]
        
        # Patterns
        pattern_info = analysis_output.get('patterns', {})
        found_patterns = pattern_info.get('patterns', {})
        found_antipatterns = pattern_info.get('anti_patterns', {})
        
        if found_patterns:
            lines.append("  Identified Patterns:")
            for pattern_name, pattern_details in found_patterns.items():
                confidence = pattern_details.get('confidence', 'unknown')
                lines.append(f"    ✓ {pattern_name.title()} (confidence: {confidence})")
        
        if found_antipatterns:
            lines.append("")
            lines.append("  Identified Issues:")
            for antipattern_name, antipattern_details in found_antipatterns.items():
                severity = antipattern_details.get('severity', 'unknown')
                lines.append(f"    ⚠ {antipattern_name.title()} (severity: {severity})")
        
        # Dependencies
        dep_info = analysis_output.get('dependencies', {})
        external_deps = dep_info.get('external_dependencies', {})
        
        if external_deps.get('count', 0) > 0:
            lines.append("")
            lines.append(f"  External Dependencies: {external_deps['count']}")
        
        lines.append("")
        lines.append("└" + "─" * 78 + "┘")
        
        return "\n".join(lines)

    def _build_quality_assessment(self, validation_output: Dict[str, Any]) -> str:
        """Creates quality assessment section."""
        lines = [
            "┌─ QUALITY ASSESSMENT " + "─" * 58 + "┐",
            ""
        ]
        
        is_valid = validation_output.get('valid', False)
        status_icon = "✓" if is_valid else "✗"
        
        lines.append(f"  BPMN Validity: {status_icon} {'PASSED' if is_valid else 'FAILED'}")
        
        errors = validation_output.get('errors', [])
        warnings = validation_output.get('warnings', [])
        
        if errors:
            lines.append(f"  Errors: {len(errors)}")
            for idx, error in enumerate(errors[:5], 1):
                lines.append(f"    {idx}. {error}")
            if len(errors) > 5:
                lines.append(f"    ... plus {len(errors) - 5} more")
        
        if warnings:
            lines.append(f"  Warnings: {len(warnings)}")
            for idx, warning in enumerate(warnings[:3], 1):
                lines.append(f"    {idx}. {warning}")
            if len(warnings) > 3:
                lines.append(f"    ... plus {len(warnings) - 3} more")
        
        lines.append("")
        lines.append("└" + "─" * 78 + "┘")
        
        return "\n".join(lines)

    def _build_action_items(self, analysis_output: Dict[str, Any],
                           validation_output: Dict[str, Any]) -> str:
        """Creates action items section."""
        lines = [
            "┌─ REQUIRED ACTIONS " + "─" * 61 + "┐",
            ""
        ]
        
        action_number = 1
        
        # From validation
        if validation_output.get('errors'):
            lines.append(f"  {action_number}. Fix BPMN validation errors")
            action_number += 1
        
        # From analysis
        complexity_info = analysis_output.get('complexity', {})
        recommendations = complexity_info.get('recommendations', [])
        
        for rec in recommendations[:5]:
            lines.append(f"  {action_number}. {rec}")
            action_number += 1
        
        # Standard actions
        lines.append(f"  {action_number}. Review and test in Camunda Modeler")
        action_number += 1
        lines.append(f"  {action_number}. Implement service task delegates")
        action_number += 1
        lines.append(f"  {action_number}. Configure user task assignments")
        
        lines.append("")
        lines.append("└" + "─" * 78 + "┘")
        
        return "\n".join(lines)

    def _build_footer(self) -> str:
        """Creates report footer."""
        footer_lines = [
            "╔" + "═" * 78 + "╗",
            "║" + " END OF REPORT".center(78) + "║",
            "╚" + "═" * 78 + "╝"
        ]
        return "\n".join(footer_lines)

    def export_json_format(self, data: Dict[str, Any], output_path: str):
        """Exports report data in JSON format."""
        report_data = {
            'workflow_name': self.workflow_name,
            'timestamp': self.timestamp.isoformat(),
            'data': data
        }
        
        with open(output_path, 'w') as file:
            json.dump(report_data, file, indent=2)
