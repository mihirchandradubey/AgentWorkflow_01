# Purchase Approval Workflow Example

This example demonstrates a simple purchase approval workflow migration from Pega to Camunda.

## Workflow Description

- **Type**: Approval workflow
- **Complexity**: Low
- **Decision Points**: 1 (amount-based routing)
- **User Tasks**: 2 (Team Lead, Manager)
- **Service Tasks**: 1 (Notification)

## Pega Elements

1. **Flow Action**: Submit Purchase Request
2. **Decision**: Check Purchase Amount
3. **Assignments**: Team Lead or Manager based on amount
4. **Connector**: Notification service

## Camunda Conversion

The workflow converts to:
- Start Event
- User Task: Submit Purchase Request
- Exclusive Gateway: Amount Decision
- User Tasks: Team Lead or Manager Approval
- Service Task: Send Notification
- End Event

## Generated Files

- `pega_approval.xml` - Original Pega workflow
- `pega_approval.bpmn` - Generated Camunda BPMN (after conversion)
- `pega_approval_report.txt` - Analysis report (after conversion)
- `pega_approval_implementation.md` - Implementation guide (after conversion)

## How to Use

```bash
cd accelerator
python cli.py convert --input examples/approval_workflow/pega_approval.xml --output examples/approval_workflow/output/
```
