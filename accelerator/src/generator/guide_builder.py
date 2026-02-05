"""Implementation guide builder with markdown output."""

from typing import Dict, Any, List
from datetime import datetime

class GuideBuilder:
    """Builds implementation guides and documentation."""

    def __init__(self):
        self.sections = []

    def create_implementation_manual(self, 
                                    workflow_info: Dict[str, Any],
                                    bpmn_output: str) -> str:
        """Creates a comprehensive implementation manual."""
        
        manual_parts = []
        
        # Title and intro
        manual_parts.append(self._create_title_section(workflow_info))
        
        # Quick reference
        manual_parts.append(self._create_quick_reference(workflow_info))
        
        # Setup instructions
        manual_parts.append(self._create_setup_section())
        
        # Implementation details
        manual_parts.append(self._create_implementation_details(workflow_info))
        
        # Service integration
        manual_parts.append(self._create_service_integration_section(workflow_info))
        
        # Task configuration
        manual_parts.append(self._create_task_configuration_section(workflow_info))
        
        # Testing strategy
        manual_parts.append(self._create_testing_section())
        
        # Deployment guide
        manual_parts.append(self._create_deployment_section())
        
        return "\n\n".join(manual_parts)

    def _create_title_section(self, workflow_info: Dict[str, Any]) -> str:
        """Creates title and introduction."""
        workflow_name = workflow_info.get('name', 'Workflow')
        
        lines = [
            f"# Implementation Manual: {workflow_name}",
            "",
            f"**Date**: {datetime.now().strftime('%B %d, %Y')}",
            "",
            "## Introduction",
            "",
            f"This manual provides complete instructions for implementing the migrated ",
            f"**{workflow_name}** process in Camunda BPM Platform.",
            "",
            "---"
        ]
        
        return "\n".join(lines)

    def _create_quick_reference(self, workflow_info: Dict[str, Any]) -> str:
        """Creates quick reference section."""
        items = workflow_info.get('elements', [])
        
        lines = [
            "## Quick Reference",
            "",
            "| Metric | Value |",
            "|--------|-------|"
        ]
        
        lines.append(f"| Total Components | {len(items)} |")
        
        # Count types
        type_map = {}
        for item in items:
            item_type = item.get('type', 'Unknown')
            type_map[item_type] = type_map.get(item_type, 0) + 1
        
        for item_type, count in type_map.items():
            lines.append(f"| {item_type} | {count} |")
        
        lines.append("")
        lines.append("---")
        
        return "\n".join(lines)

    def _create_setup_section(self) -> str:
        """Creates setup section."""
        lines = [
            "## Environment Setup",
            "",
            "### Required Software",
            "",
            "- Camunda Platform 7.18+ or Camunda Platform 8",
            "- Camunda Modeler (latest version)",
            "- JDK 11 or later",
            "- Build tool: Maven 3.6+ or Gradle 7+",
            "",
            "### Project Structure",
            "",
            "```",
            "camunda-project/",
            "├── src/",
            "│   ├── main/",
            "│   │   ├── java/",
            "│   │   │   └── com/example/",
            "│   │   │       ├── delegates/",
            "│   │   │       └── listeners/",
            "│   │   └── resources/",
            "│   │       ├── processes/",
            "│   │       └── dmn/",
            "│   └── test/",
            "└── pom.xml",
            "```",
            "",
            "---"
        ]
        
        return "\n".join(lines)

    def _create_implementation_details(self, workflow_info: Dict[str, Any]) -> str:
        """Creates implementation details section."""
        lines = [
            "## Implementation Steps",
            "",
            "### Phase 1: Import and Review",
            "",
            "1. Open Camunda Modeler application",
            "2. Select **File → Open** and load the generated BPMN file",
            "3. Visually inspect the process diagram",
            "4. Verify all elements are correctly positioned",
            "",
            "### Phase 2: Variable Configuration",
            "",
            "Configure process variables in the properties panel:",
            "",
            "```java",
            "// Core process variables",
            "Map<String, Object> variables = new HashMap<>();",
            "variables.put(\"processId\", UUID.randomUUID().toString());",
            "variables.put(\"status\", \"INITIATED\");",
            "variables.put(\"initiator\", \"system\");",
            "```",
            "",
            "### Phase 3: Element Configuration",
            "",
            "Configure each process element according to requirements.",
            "See detailed sections below for specific element types.",
            "",
            "---"
        ]
        
        return "\n".join(lines)

    def _create_service_integration_section(self, workflow_info: Dict[str, Any]) -> str:
        """Creates service integration section."""
        items = workflow_info.get('elements', [])
        service_items = [i for i in items if i.get('type') in ['Connector', 'Integration']]
        
        lines = [
            "## Service Integration",
            ""
        ]
        
        if service_items:
            lines.append(f"This workflow requires {len(service_items)} service integration(s):")
            lines.append("")
            
            for idx, item in enumerate(service_items, 1):
                item_name = item.get('name', f'Service{idx}')
                item_id = item.get('id', '')
                
                lines.append(f"### Integration {idx}: {item_name}")
                lines.append("")
                lines.append(f"**Original ID**: `{item_id}`")
                lines.append("")
                lines.append("**Java Delegate Implementation**:")
                lines.append("")
                lines.append("```java")
                
                class_name = item_name.replace(' ', '') + "Handler"
                lines.append(f"@Component(\"{item_id}\")")
                lines.append(f"public class {class_name} implements JavaDelegate {{")
                lines.append("")
                lines.append("    @Autowired")
                lines.append("    private RestTemplate restTemplate;")
                lines.append("")
                lines.append("    @Override")
                lines.append("    public void execute(DelegateExecution exec) throws Exception {{")
                lines.append(f"        // TODO: Implement {item_name} logic")
                lines.append("        String processId = (String) exec.getVariable(\"processId\");")
                lines.append("        ")
                lines.append("        // Call external service")
                lines.append("        // ResponseEntity<String> response = restTemplate.getForEntity(...);")
                lines.append("        ")
                lines.append("        // Store result")
                lines.append("        // exec.setVariable(\"result\", response.getBody());")
                lines.append("    }")
                lines.append("}")
                lines.append("```")
                lines.append("")
        else:
            lines.append("No external service integrations detected.")
            lines.append("")
        
        lines.append("---")
        
        return "\n".join(lines)

    def _create_task_configuration_section(self, workflow_info: Dict[str, Any]) -> str:
        """Creates task configuration section."""
        items = workflow_info.get('elements', [])
        user_items = [i for i in items if i.get('type') in ['Assignment', 'FlowAction']]
        
        lines = [
            "## User Task Configuration",
            ""
        ]
        
        if user_items:
            lines.append("### Task Assignments")
            lines.append("")
            lines.append("| Task Name | Assignee/Group | Configuration |")
            lines.append("|-----------|----------------|---------------|")
            
            for item in user_items:
                task_name = item.get('name', 'Task')
                assignee = item.get('assignee', 'unassigned')
                lines.append(f"| {task_name} | {assignee} | Candidate Groups |")
            
            lines.append("")
            lines.append("### Form Configuration")
            lines.append("")
            lines.append("Create forms using Camunda Forms or embedded forms:")
            lines.append("")
            lines.append("```xml")
            lines.append('<userTask id="userTask1" name="Review Request"')
            lines.append('    camunda:formKey="embedded:app:forms/review-form.html"')
            lines.append('    camunda:candidateGroups="reviewers">')
            lines.append("</userTask>")
            lines.append("```")
            lines.append("")
        else:
            lines.append("No user tasks detected in this workflow.")
            lines.append("")
        
        lines.append("---")
        
        return "\n".join(lines)

    def _create_testing_section(self) -> str:
        """Creates testing section."""
        lines = [
            "## Testing Strategy",
            "",
            "### Unit Testing",
            "",
            "Test individual process components:",
            "",
            "```java",
            "@ExtendWith(MockitoExtension.class)",
            "class ProcessUnitTest {",
            "",
            "    @Mock",
            "    private RuntimeService runtimeService;",
            "",
            "    @Test",
            "    void testProcessStart() {",
            "        Map<String, Object> vars = new HashMap<>();",
            "        vars.put(\"testVar\", \"testValue\");",
            "        ",
            "        ProcessInstance instance = runtimeService",
            "            .startProcessInstanceByKey(\"processKey\", vars);",
            "        ",
            "        assertNotNull(instance);",
            "    }",
            "}",
            "```",
            "",
            "### Integration Testing",
            "",
            "1. Deploy process to test environment",
            "2. Execute complete workflow scenarios",
            "3. Validate all paths and outcomes",
            "4. Test error handling and boundaries",
            "",
            "### Performance Testing",
            "",
            "- Load test with expected volume",
            "- Monitor database performance",
            "- Check memory usage patterns",
            "",
            "---"
        ]
        
        return "\n".join(lines)

    def _create_deployment_section(self) -> str:
        """Creates deployment section."""
        lines = [
            "## Deployment",
            "",
            "### Method 1: Modeler Deployment",
            "",
            "1. Configure deployment endpoint in Modeler",
            "2. Click **Deploy** button",
            "3. Select target environment",
            "4. Confirm deployment",
            "",
            "### Method 2: REST API Deployment",
            "",
            "```bash",
            "curl -X POST \\",
            "  'http://camunda-server:8080/engine-rest/deployment/create' \\",
            "  -H 'Content-Type: multipart/form-data' \\",
            "  -F 'deployment-name=MyProcess' \\",
            "  -F 'deploy-changed-only=true' \\",
            "  -F 'deployment-source=migration' \\",
            "  -F 'data=@process.bpmn'",
            "```",
            "",
            "### Method 3: Spring Boot Auto-Deployment",
            "",
            "Place BPMN files in:",
            "```",
            "src/main/resources/processes/",
            "```",
            "",
            "They will auto-deploy on application startup.",
            "",
            "---",
            "",
            "## Support and Troubleshooting",
            "",
            "For issues or questions:",
            "- Review Camunda documentation",
            "- Check process instance history",
            "- Enable debug logging",
            "- Contact support team"
        ]
        
        return "\n".join(lines)

    def create_quickstart_guide(self) -> str:
        """Creates a quick start guide."""
        lines = [
            "# Quick Start: Pega to Camunda Migration Accelerator",
            "",
            "## Installation",
            "",
            "```bash",
            "# Navigate to accelerator directory",
            "cd accelerator",
            "",
            "# Install required packages",
            "pip install -r requirements.txt",
            "```",
            "",
            "## Basic Usage",
            "",
            "### Convert Single Workflow",
            "",
            "```bash",
            "python cli.py convert \\",
            "  --input pega_workflow.xml \\",
            "  --output ./output/",
            "```",
            "",
            "### Batch Conversion",
            "",
            "```bash",
            "python cli.py convert \\",
            "  --input ./workflows/ \\",
            "  --output ./output/ \\",
            "  --batch",
            "```",
            "",
            "### Analyze Complexity",
            "",
            "```bash",
            "python cli.py analyze --input pega_workflow.xml",
            "```",
            "",
            "## Output Files",
            "",
            "- `*.bpmn` - Camunda BPMN files",
            "- `*.dmn` - DMN decision tables",
            "- `*_analysis.txt` - Analysis report",
            "- `*_implementation.md` - Implementation guide",
            "",
            "## Next Steps",
            "",
            "1. Import BPMN into Camunda Modeler",
            "2. Review implementation guide",
            "3. Configure service tasks",
            "4. Test workflow",
            "5. Deploy to Camunda"
        ]
        
        return "\n".join(lines)
