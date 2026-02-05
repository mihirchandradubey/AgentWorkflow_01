# Quick Start Demonstration

This demo shows the complete workflow of using the Pega to Camunda Migration Accelerator.

## Setup

```bash
cd accelerator
pip install -r requirements.txt
```

## Example 1: Simple Approval Workflow

### Step 1: Analyze the Workflow

```bash
python cli.py analyze --input examples/approval_workflow/pega_approval.xml
```

**Output:**
- Complexity Level: Low
- Complexity Score: 16.0
- Estimated Effort: 1.0 days (8.0 hours)
- Automation Rate: 85%
- Patterns: Sequential, Conditional, Approval, Escalation

### Step 2: Convert to Camunda

```bash
python cli.py convert \
  --input examples/approval_workflow/pega_approval.xml \
  --output examples/approval_workflow/output/
```

**Generated Files:**
- `pega_approval.bpmn` - Camunda BPMN 2.0 XML (ready to deploy)
- `pega_approval_DEC001.dmn` - DMN decision table for amount check
- `pega_approval_report.txt` - Detailed migration report
- `pega_approval_implementation.md` - Step-by-step implementation guide

### Step 3: Validate the BPMN

```bash
python cli.py validate --input examples/approval_workflow/output/pega_approval.bpmn
```

**Validation checks:**
- XML well-formedness ✓
- BPMN structure validity
- Element connectivity
- Best practice compliance

### Step 4: Review Implementation Guide

The generated `pega_approval_implementation.md` contains:
- Workflow structure overview
- Service task implementation templates (Java code)
- User task configuration (candidate groups, forms)
- DMN decision table details
- Testing strategy
- Deployment instructions

## Example 2: Multi-Stage Case Workflow

### Convert the JSON workflow

```bash
python cli.py convert \
  --input examples/case_workflow/pega_case.json \
  --output examples/case_workflow/output/ \
  --format json
```

This workflow includes:
- 3 stages (Information Gathering, Verification, Account Setup)
- External KYC integration
- Decision table for KYC results
- Multiple service tasks

## Batch Processing

Convert multiple workflows at once:

```bash
python cli.py convert \
  --input examples/ \
  --output batch_output/ \
  --batch
```

## Initialize Camunda Project

Create a ready-to-use Camunda Spring Boot project structure:

```bash
python cli.py init
```

This creates:
```
src/
├── main/
│   ├── java/com/example/
│   │   ├── delegates/      # Place your service task implementations here
│   │   └── listeners/      # Place your task listeners here
│   └── resources/
│       ├── processes/       # Copy your .bpmn files here
│       └── dmn/            # Copy your .dmn files here
└── test/
    └── java/com/example/   # Write your tests here
```

## What Gets Automated

### ✅ Fully Automated (70%)
- BPMN structure generation
- Element type mapping (FlowAction → UserTask, etc.)
- Sequence flow connections
- DMN table creation for decisions
- Basic property mapping
- Timer event conversion from SLA rules
- Visual diagram layout

### 🔧 Semi-Automated (20%)
- Service task delegate signatures (code templates provided)
- User task form references (placeholders generated)
- Candidate group mappings (suggestions provided)
- Complex decision logic (DMN structure provided)
- Integration endpoint configuration (documented in guide)

### ✋ Manual Work Required (10%)
- Service task implementation logic
- Custom form creation
- User/role mapping to your environment
- External service authentication
- Business rule fine-tuning
- Performance optimization

## Key Features in Action

### 1. Intelligent Mapping

The tool automatically maps Pega elements to Camunda:

| From (Pega) | To (Camunda) |
|-------------|--------------|
| FlowAction | userTask with formKey |
| Assignment | userTask with candidateGroups |
| Decision | businessRuleTask + DMN |
| Connector | serviceTask with delegate |
| Wait | intermediateCatchEvent (timer) |
| SLA Rule | boundaryEvent (timer) |

### 2. Pattern Detection

Automatically identifies workflow patterns:
- Sequential flow
- Parallel execution
- Conditional branching
- Approval chains
- Escalation paths
- Loop patterns

### 3. Complexity Analysis

Provides detailed metrics:
- Total elements and connectors
- Cyclomatic complexity
- Decision point count
- Integration points
- Effort estimation
- Automation percentage

### 4. Quality Validation

Checks generated BPMN for:
- Valid XML structure
- BPMN 2.0 compliance
- Element connectivity
- Naming conventions
- Best practices

### 5. Comprehensive Documentation

Auto-generates:
- Migration analysis reports
- Implementation guides with code templates
- User task configuration instructions
- Service task implementation examples
- Testing strategies
- Deployment procedures

## Tips for Success

1. **Start with simple workflows** - Get familiar with the tool
2. **Review the generated BPMN** - Open in Camunda Modeler for visual inspection
3. **Follow the implementation guide** - It contains all the manual steps needed
4. **Test incrementally** - Deploy and test each workflow individually
5. **Customize mappings** - Adjust `config/mapping_rules.yaml` for your needs

## Next Steps

After conversion:

1. **Import into Camunda Modeler**
   - Visually verify the process
   - Adjust layout if needed
   - Add documentation annotations

2. **Implement Service Tasks**
   ```java
   @Component("myServiceTask")
   public class MyServiceDelegate implements JavaDelegate {
       @Override
       public void execute(DelegateExecution execution) {
           // Your logic here
       }
   }
   ```

3. **Configure User Tasks**
   - Map candidate groups to your organization
   - Create Camunda forms or external forms
   - Set up task routing rules

4. **Test the Process**
   - Unit test with Camunda test framework
   - Integration test with real services
   - User acceptance testing

5. **Deploy to Camunda**
   - Deploy via Camunda Modeler
   - Or use REST API
   - Or Spring Boot auto-deployment

## Support

For questions or issues:
- Review the comprehensive [README](README.md)
- Check the [Migration Playbook](MIGRATION_PLAYBOOK.md)
- Examine the example workflows in `examples/`
- Review the configuration files in `config/`

---

**Happy Migrating! 🚀**
