# Customer Onboarding Case Workflow Example

This example demonstrates a multi-stage case workflow migration from Pega to Camunda.

## Workflow Description

- **Type**: Case management workflow
- **Complexity**: Medium
- **Stages**: 3 (Information Gathering, Verification, Account Setup)
- **Decision Points**: 1 (KYC result)
- **External Integrations**: 3 (KYC, Account Creation, Communication)

## Pega Stages

1. **Stage 1 - Information Gathering**
   - Initialize onboarding
   - Verify customer information

2. **Stage 2 - Verification**
   - KYC check (external service)
   - Evaluate KYC results

3. **Stage 3 - Account Setup**
   - Create customer account
   - Send welcome package

## Camunda Conversion

Stages map to embedded subprocesses or call activities:
- Each stage becomes a subprocess
- External integrations become service tasks
- KYC decision converts to DMN table

## Generated Files

Run conversion to generate:
- `pega_case.bpmn` - Main process
- `pega_case_STAGE2_DECISION.dmn` - KYC decision table
- `pega_case_report.txt` - Analysis report
- `pega_case_implementation.md` - Implementation guide

## How to Use

```bash
cd accelerator
python cli.py convert --input examples/case_workflow/pega_case.json --output examples/case_workflow/output/ --format json
```
