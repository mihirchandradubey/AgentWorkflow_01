# EUC Audit Compliance Rules

This document defines the audit compliance rules that the agentic workflow must enforce for the Loan Loss Provision Calculator EUC application.

## 1. Inventory & Risk Assessment Rules

### Rule 1.1: EUC Registration
**Requirement**: All critical EUC applications must be registered in the central inventory.

**Implementation**:
- **Operator**: MUST EXIST
- **Check**: Verify application exists in EUC_INVENTORY with status="Active"
- **Frequency**: On initial deployment
- **Evidence**: Inventory record with metadata

**Attributes Required**:
- Application Name
- Business Owner
- Technical Owner
- Risk Rating (Low/Medium/High)
- Criticality Level
- Last Review Date
- Next Review Date

### Rule 1.2: Risk Classification
**Requirement**: EUC must have documented risk assessment.

**Implementation**:
- **Operator**: CLASSIFY BY
- **Criteria**: 
  - Financial Impact > $1M → High Risk
  - Regulatory Reporting = Yes → High Risk
  - Users > 10 → Medium Risk
  - Complexity Score > 7 → High Risk
- **Check**: Risk rating matches criteria
- **Frequency**: Annual or on significant change

## 2. Access Control Rules

### Rule 2.1: Role-Based Access
**Requirement**: Users must have appropriate roles assigned.

**Implementation**:
- **Operator**: ROLE IN {Viewer, Editor, Approver, Admin}
- **Check**: User role matches job function
- **Enforcement**: DENY if role not assigned

**Role Definitions**:
- **Viewer**: Read-only access to final reports
- **Editor**: Can modify inputs and formulas (with approval)
- **Approver**: Can approve changes and certify outputs
- **Admin**: Can modify access controls and configurations

### Rule 2.2: Segregation of Duties
**Requirement**: No single user can prepare and approve.

**Implementation**:
- **Operator**: EXCLUDE IF (PreparedBy = ApprovedBy)
- **Check**: Editor cannot also be Approver for same transaction
- **Enforcement**: BLOCK approval if same user

### Rule 2.3: Access Logging
**Requirement**: All access must be logged.

**Implementation**:
- **Operator**: LOG EVERY ACCESS
- **Data Captured**: User ID, Timestamp, Action, IP Address, Workbook Version
- **Retention**: 7 years
- **Storage**: Append-only audit log

## 3. Change Management Rules

### Rule 3.1: Formula Change Approval
**Requirement**: Formula changes require approval.

**Implementation**:
- **Operator**: IF FORMULA_CHANGED THEN REQUIRE_APPROVAL
- **Detection**: Cell formula hash comparison
- **Workflow**: Change Request → Manager Review → Testing → Approval → Deployment
- **Exception**: None (all formula changes must be approved)

### Rule 3.2: Version Control
**Requirement**: Maintain version history with ability to rollback.

**Implementation**:
- **Operator**: VERSION ON SAVE
- **Versioning**: Semantic versioning (Major.Minor.Patch)
  - Major: Formula/logic changes
  - Minor: Input data structure changes
  - Patch: Cosmetic/formatting changes
- **Storage**: All versions retained for 7 years
- **Rollback**: Any version can be restored by Admin

### Rule 3.3: Change Documentation
**Requirement**: All changes must be documented.

**Implementation**:
- **Operator**: DOCUMENT REQUIRED
- **Required Fields**:
  - Change Description
  - Business Justification
  - Changed By / Approved By
  - Test Results
  - Rollback Plan
  - Impact Assessment
- **Check**: Cannot complete change without documentation

## 4. Data Validation Rules

### Rule 4.1: Input Data Completeness
**Requirement**: All required data fields must be populated.

**Implementation**:
- **Operator**: NOT NULL WHERE Required=True
- **Check**: Required cells are not empty
- **Action**: FLAG and prevent calculation if missing

**Required Fields**:
- Loan Portfolio data (Account ID, Balance, Risk Rating, Maturity Date)
- Historical Loss Rates by Risk Rating
- Economic Indicators (GDP Growth, Unemployment Rate)
- Reporting Period

### Rule 4.2: Data Type Validation
**Requirement**: Data must match expected types and formats.

**Implementation**:
- **Operator**: TYPE MATCH
- **Checks**:
  - Loan Balance: NUMBER, >= 0
  - Risk Rating: ENUM {AAA, AA, A, BBB, BB, B, CCC, Default}
  - Date fields: DATE, ISO 8601 format
  - Rates: PERCENTAGE, 0-100%
- **Action**: REJECT invalid data with error message

### Rule 4.3: Range Validation
**Requirement**: Data must be within reasonable bounds.

**Implementation**:
- **Operator**: BETWEEN min AND max
- **Limits**:
  - Loss Rate: 0% to 100%
  - Loan Balance: $0 to $100M (per loan)
  - Economic Growth: -20% to +20%
- **Action**: WARNING if outside normal range, ERROR if outside max range

### Rule 4.4: Consistency Checks
**Requirement**: Related data must be consistent.

**Implementation**:
- **Operator**: VALIDATE_RELATIONSHIP
- **Checks**:
  - Total Portfolio = SUM(Individual Loans) ± 0.01%
  - Provision <= Portfolio Balance
  - Weighted Average Rate matches portfolio composition
- **Action**: BLOCK calculation if inconsistent

## 5. Formula Verification Rules

### Rule 5.1: Formula Integrity
**Requirement**: Formulas must be error-free.

**Implementation**:
- **Operator**: NO FORMULA ERRORS
- **Check**: Detect #REF!, #DIV/0!, #VALUE!, #N/A, #NAME?, #NULL!, #NUM!
- **Action**: BLOCK calculation and ALERT user

### Rule 5.2: Circular Reference Detection
**Requirement**: No circular references allowed.

**Implementation**:
- **Operator**: DETECT CIRCULAR
- **Check**: Dependency graph analysis
- **Action**: BLOCK and require fix

### Rule 5.3: Formula Consistency
**Requirement**: Similar calculations should use same formula.

**Implementation**:
- **Operator**: PATTERN MATCH
- **Check**: Provision formula consistent across risk categories
- **Action**: WARNING if formulas differ unexpectedly

## 6. Testing & Validation Rules

### Rule 6.1: Pre-Change Testing
**Requirement**: Changes must be tested before deployment.

**Implementation**:
- **Operator**: TEST REQUIRED
- **Test Cases**:
  - Unit tests for each formula
  - Integration test with sample data
  - Regression test comparing to previous version
  - Edge case testing (zero values, max values)
- **Pass Criteria**: All tests pass with <0.01% variance

### Rule 6.2: Peer Review
**Requirement**: Critical changes require peer review.

**Implementation**:
- **Operator**: REVIEW BY SECOND_PERSON
- **Scope**: All High-risk changes (formula, logic)
- **Reviewer**: Must be qualified (same or higher role)
- **Documentation**: Review comments and sign-off

## 7. Audit Trail Rules

### Rule 7.1: Comprehensive Logging
**Requirement**: Log all material activities.

**Implementation**:
- **Operator**: LOG EVENT
- **Events Logged**:
  - File open/close
  - Cell edits (before/after values)
  - Formula changes
  - Data imports
  - Calculation runs
  - Approvals/certifications
  - Report generation
- **Format**: JSON with timestamp, user, action, details

### Rule 7.2: Log Integrity
**Requirement**: Logs must be tamper-proof.

**Implementation**:
- **Operator**: CRYPTOGRAPHIC HASH
- **Method**: SHA-256 hash chain
- **Storage**: Append-only, write-once storage
- **Verification**: Hash verification on audit review

### Rule 7.3: Log Retention
**Requirement**: Logs retained per regulatory requirements.

**Implementation**:
- **Operator**: RETAIN FOR duration
- **Duration**: 7 years (SOX requirement)
- **Backup**: Daily backups with offsite storage
- **Archive**: Move to cold storage after 2 years

## 8. Documentation Rules

### Rule 8.1: Current Documentation
**Requirement**: Documentation must be current.

**Implementation**:
- **Operator**: LAST_UPDATED <= 30 days
- **Check**: Documentation timestamp vs. last material change
- **Action**: ALERT if documentation stale

**Required Documentation**:
- Business Purpose
- Calculation Methodology
- Data Sources
- Formula Explanations
- Assumptions
- Known Limitations
- User Guide
- Change History

### Rule 8.2: Assumption Documentation
**Requirement**: All assumptions must be documented.

**Implementation**:
- **Operator**: DOCUMENT ASSUMPTION
- **Trigger**: Manual override or management adjustment
- **Required**: Assumption description, justification, approver

## 9. Backup & Recovery Rules

### Rule 9.1: Regular Backups
**Requirement**: Daily automated backups.

**Implementation**:
- **Operator**: BACKUP DAILY
- **Schedule**: Daily at 2 AM
- **Retention**: 30 daily, 12 monthly, 7 yearly
- **Verification**: Monthly restore test

### Rule 9.2: Disaster Recovery
**Requirement**: Ability to recover within RTO.

**Implementation**:
- **Operator**: RECOVER WITHIN RTO
- **RTO**: 4 hours (business hours)
- **RPO**: 24 hours (last backup)
- **Test**: Quarterly DR drill

## 10. Periodic Review Rules

### Rule 10.1: Quarterly Certification
**Requirement**: Business owner certifies quarterly.

**Implementation**:
- **Operator**: CERTIFY EVERY QUARTER
- **Certification**:
  - Confirms accuracy of output
  - Validates assumptions remain appropriate
  - Reviews access list
  - Confirms no unauthorized changes
- **Evidence**: Signed certification form

### Rule 10.2: Annual Audit
**Requirement**: Annual independent audit.

**Implementation**:
- **Operator**: AUDIT ANNUALLY
- **Scope**: Full audit of controls, formulas, documentation
- **Auditor**: Internal Audit or External Auditor
- **Deliverable**: Audit report with findings and remediation plan

## Compliance Operators Summary

The following operators are used throughout the rules:

- **MUST EXIST**: Mandatory presence check
- **CLASSIFY BY**: Risk/categorization logic
- **ROLE IN**: Role-based access control
- **EXCLUDE IF**: Exclusion/blocking condition
- **LOG EVERY**: Comprehensive logging
- **VERSION ON**: Version control trigger
- **NOT NULL**: Completeness validation
- **TYPE MATCH**: Data type validation
- **BETWEEN**: Range validation
- **VALIDATE_RELATIONSHIP**: Consistency check
- **NO FORMULA ERRORS**: Error detection
- **DETECT CIRCULAR**: Circular reference check
- **PATTERN MATCH**: Consistency pattern
- **TEST REQUIRED**: Mandatory testing
- **REVIEW BY**: Peer review requirement
- **CRYPTOGRAPHIC HASH**: Integrity protection
- **RETAIN FOR**: Retention policy
- **LAST_UPDATED**: Recency check
- **BACKUP DAILY**: Backup frequency
- **RECOVER WITHIN**: Recovery time objective
- **CERTIFY EVERY**: Periodic certification
- **AUDIT ANNUALLY**: Annual audit requirement

## Implementation Priority

### Phase 1 - Critical Controls (Immediate)
- Access Control (Rules 2.1-2.3)
- Formula Verification (Rules 5.1-5.2)
- Audit Trail (Rules 7.1-7.2)
- Data Validation (Rules 4.1-4.2)

### Phase 2 - Enhanced Controls (Month 1-2)
- Change Management (Rules 3.1-3.3)
- Testing & Validation (Rules 6.1-6.2)
- Documentation (Rules 8.1-8.2)

### Phase 3 - Operational Controls (Month 3-4)
- Backup & Recovery (Rules 9.1-9.2)
- Periodic Review (Rules 10.1-10.2)
- Inventory Management (Rules 1.1-1.2)
- Advanced Validation (Rules 4.3-4.4, 5.3)
