# Sample Excel Template: Loan Loss Provision Calculator

This document describes the structure of the sample Excel workbook used in the POC.

## Workbook Structure

### Sheet 1: Instructions
- **Purpose**: User guide and documentation
- **Content**:
  - Overview of the calculator
  - Data input instructions
  - Calculation methodology
  - Output interpretation
  - Change history
  - Contact information

### Sheet 2: Portfolio Data
- **Purpose**: Input loan portfolio data

**Columns**:
| Column | Field Name | Data Type | Required | Validation |
|--------|-----------|-----------|----------|------------|
| A | Account ID | Text | Yes | Unique identifier |
| B | Borrower Name | Text | Yes | Non-empty |
| C | Loan Balance | Number | Yes | >= 0 |
| D | Risk Rating | Enum | Yes | {AAA, AA, A, BBB, BB, B, CCC, Default} |
| E | Industry | Text | Yes | Pre-defined list |
| F | Origination Date | Date | Yes | Valid date |
| G | Maturity Date | Date | Yes | >= Origination Date |
| H | Interest Rate | Percentage | Yes | 0-30% |
| I | Collateral Value | Number | No | >= 0 |
| J | Current Status | Enum | Yes | {Current, 30DPD, 60DPD, 90DPD, NPL} |

**Named Range**: `PortfolioData` (A2:J10001, up to 10,000 loans)

**Sample Data** (First 3 rows):
```
Account ID | Borrower Name    | Loan Balance | Risk Rating | Industry      | Orig Date  | Maturity   | Rate  | Collateral | Status
L001234   | ABC Corporation  | 5,000,000    | A           | Manufacturing | 2022-01-15 | 2027-01-15 | 5.25% | 6,000,000  | Current
L001235   | XYZ Inc         | 2,500,000    | BBB         | Retail        | 2021-06-30 | 2026-06-30 | 6.50% | 2,000,000  | Current
L001236   | Tech Startup    | 750,000      | BB          | Technology    | 2023-03-20 | 2028-03-20 | 8.75% | 500,000    | 30DPD
```

### Sheet 3: Risk Parameters
- **Purpose**: Define risk-based provisioning rates

**Section 1: Historical Loss Rates by Risk Rating**
| Risk Rating | 1-Year Default Rate | 3-Year Default Rate | 5-Year Default Rate | Loss Given Default |
|-------------|-------------------|-------------------|-------------------|-------------------|
| AAA | 0.01% | 0.05% | 0.10% | 10% |
| AA | 0.05% | 0.15% | 0.30% | 15% |
| A | 0.10% | 0.30% | 0.60% | 20% |
| BBB | 0.25% | 0.75% | 1.50% | 25% |
| BB | 0.75% | 2.25% | 4.50% | 35% |
| B | 2.00% | 6.00% | 12.00% | 50% |
| CCC | 5.00% | 15.00% | 30.00% | 70% |
| Default | 100.00% | 100.00% | 100.00% | 100% |

**Named Ranges**:
- `RiskRatings` (Risk Rating column)
- `DefaultRates_1Y` (1-Year column)
- `DefaultRates_3Y` (3-Year column)
- `LossGivenDefault` (LGD column)

**Section 2: Economic Adjustment Factors**
| Economic Indicator | Current Value | Forecast (1Y) | Impact Factor |
|-------------------|--------------|--------------|---------------|
| GDP Growth Rate | 2.5% | 1.8% | 0.15 |
| Unemployment Rate | 4.2% | 5.1% | 0.20 |
| Corporate Default Index | 1.2% | 1.8% | 0.30 |

**Named Range**: `EconomicFactors`

### Sheet 4: Calculation
- **Purpose**: Perform provision calculations

**Section 1: Portfolio Summary**
```
Total Portfolio Value: =SUM(PortfolioData[Loan Balance])
Number of Loans: =COUNTA(PortfolioData[Account ID])
Weighted Average Risk Rating: =SUMPRODUCT(...) [Custom formula]
```

**Section 2: Provision by Risk Rating**

| Risk Rating | Total Exposure | Provision Rate | Expected Loss | Management Overlay | Total Provision |
|-------------|---------------|----------------|---------------|-------------------|-----------------|
| AAA | =SUMIF(...) | =VLOOKUP(...) | =B*C | =E*$EconFactor | =D+E |
| AA | =SUMIF(...) | =VLOOKUP(...) | =B*C | =E*$EconFactor | =D+E |
| ... | ... | ... | ... | ... | ... |

**Key Formulas**:

1. **Total Exposure by Risk Rating**:
   ```excel
   =SUMIF(PortfolioData[Risk Rating], A2, PortfolioData[Loan Balance])
   ```

2. **Provision Rate** (Expected Loss Rate):
   ```excel
   =VLOOKUP(A2, RiskParameters, MATCH("1-Year Default Rate", Headers, 0), FALSE) * 
    VLOOKUP(A2, RiskParameters, MATCH("Loss Given Default", Headers, 0), FALSE)
   ```

3. **Expected Loss**:
   ```excel
   =B2 * C2
   ```

4. **Management Overlay** (Economic Adjustment):
   ```excel
   =D2 * EconomicAdjustmentFactor
   ```
   Where `EconomicAdjustmentFactor` is calculated based on economic indicators.

5. **Total Provision**:
   ```excel
   =D2 + E2
   ```

**Section 3: Total Provision Summary**
```
Total Expected Loss: =SUM(ExpectedLoss)
Total Management Overlay: =SUM(ManagementOverlay)
Total Provision Required: =SUM(TotalProvision)
Coverage Ratio: =TotalProvision / TotalPortfolio
```

### Sheet 5: Validation
- **Purpose**: Data quality and consistency checks

**Checks Performed**:

| Check # | Description | Formula | Status |
|---------|-------------|---------|--------|
| 1 | No missing Account IDs | =COUNTA(PortfolioData[Account ID])=ROWS(PortfolioData) | =IF(B2=TRUE,"PASS","FAIL") |
| 2 | All balances >= 0 | =COUNTIF(PortfolioData[Loan Balance],"<0")=0 | =IF(B3=TRUE,"PASS","FAIL") |
| 3 | Valid risk ratings | =SUMPRODUCT(COUNTIF(ValidRatings,PortfolioData[Risk Rating]))=ROWS(PortfolioData) | =IF(B4=TRUE,"PASS","FAIL") |
| 4 | Maturity > Origination | =COUNTIF(PortfolioData[Maturity Date],"<"&PortfolioData[Origination Date])=0 | =IF(B5=TRUE,"PASS","FAIL") |
| 5 | Portfolio total matches | =ABS(TotalFromCalc-TotalFromPortfolio)<100 | =IF(B6=TRUE,"PASS","FAIL") |

**Overall Validation Status**:
```
=IF(COUNTIF(ValidationStatus,"FAIL")=0, "ALL CHECKS PASSED", 
    COUNTIF(ValidationStatus,"FAIL")&" CHECKS FAILED")
```

**Named Range**: `ValidationResults`

### Sheet 6: Output Report
- **Purpose**: Final formatted report for regulatory filing

**Content**:
- Report header (Bank name, period, date)
- Executive summary
- Provision by risk rating (table)
- Provision by industry (table)
- Economic assumptions
- Methodology summary
- Certification section

**Approval Section**:
```
Prepared By: ____________  Date: ______  Signature: ____________
Reviewed By: ____________  Date: ______  Signature: ____________
Approved By: ____________  Date: ______  Signature: ____________
```

### Sheet 7: Audit Trail
- **Purpose**: Track changes and access (populated by agents)

**Columns**:
| Column | Field | Description |
|--------|-------|-------------|
| A | Timestamp | Date/time of action |
| B | User ID | Who performed action |
| C | Action Type | OPEN, EDIT, CALCULATE, APPROVE, etc. |
| D | Sheet | Which sheet was affected |
| E | Cell/Range | Specific location |
| F | Before Value | Value before change |
| G | After Value | Value after change |
| H | Status | SUCCESS, FAILED, BLOCKED |
| I | Notes | Additional details |

**Named Range**: `AuditLog`

**Note**: This sheet is append-only and protected. Only the Audit Trail Agent can write to it.

### Sheet 8: Change History
- **Purpose**: Document all approved changes

**Columns**:
| Column | Field | Description |
|--------|-------|-------------|
| A | Version | Version number (e.g., 2.1.3) |
| B | Date | Date of change |
| C | Changed By | Person who made change |
| D | Approved By | Person who approved |
| E | Change Type | FORMULA, DATA, STRUCTURE, COSMETIC |
| F | Description | What was changed |
| G | Justification | Why it was changed |
| H | Test Results | Summary of testing |
| I | Rollback Available | YES/NO |

**Named Range**: `ChangeHistory`

### Sheet 9: Configuration
- **Purpose**: Store configuration for agentic workflow

**Settings**:
```
Setting                    | Value
----------------------------|------------------
Workbook Version           | 2.1.0
Risk Classification        | High
Business Owner             | John Smith
Technical Owner            | Jane Doe
Last Certification Date    | 2024-12-31
Next Certification Date    | 2025-03-31
Review Frequency           | Quarterly
Backup Frequency           | Daily
Compliance Status          | COMPLIANT
Agent Mode                 | ENABLED
Auto-Validation            | ON
Real-time Monitoring       | ON
```

## Named Ranges Summary

The workbook uses Excel's Named Ranges extensively for:
1. Easier formula readability
2. Dynamic range management
3. API integration with agents

**All Named Ranges**:
- `PortfolioData` - Loan portfolio table
- `RiskRatings` - Valid risk rating list
- `DefaultRates_1Y` - 1-year default rates
- `DefaultRates_3Y` - 3-year default rates
- `LossGivenDefault` - Loss given default percentages
- `EconomicFactors` - Economic indicators table
- `ProvisionByRating` - Calculation results by rating
- `ValidationResults` - Data validation status
- `AuditLog` - Audit trail entries
- `ChangeHistory` - Change management log
- `Configuration` - Workbook settings

## Workbook Protection

### Sheet Protection
- **Locked Cells**: Formula cells, calculation results
- **Unlocked Cells**: Input data cells (Portfolio Data, Risk Parameters)
- **Password Protected**: Change History, Audit Trail, Configuration
- **Allow**: Filtering, sorting of data tables

### Workbook Protection
- **Structure**: Locked (cannot add/delete sheets without password)
- **Windows**: Unlocked (users can resize/move windows)
- **Password**: Managed by Admin role

## VBA Macros (Optional)

If using VBA, include macros for:

1. **RefreshData()**: Import data from source systems
2. **CalculateProvision()**: Trigger calculation with validation
3. **GenerateReport()**: Create output report
4. **ExportAuditLog()**: Export audit trail to CSV
5. **VersionCheck()**: Check for newer versions

**Note**: All VBA code must be digitally signed and reviewed during change approval process.

## Integration with Agentic Workflow

### Data Exchange Format

The Excel workbook communicates with agents via:

1. **JSON API**: Excel Add-in calls REST API
2. **Named Ranges**: Agents read/write using named ranges
3. **Custom XML Parts**: Store metadata and agent state
4. **Table Objects**: Use Excel Tables for structured data

### Example API Call (from Excel Add-in):

```javascript
// When user opens workbook
async function onWorkbookOpen() {
    const response = await fetch('/api/agents/access-control', {
        method: 'POST',
        body: JSON.stringify({
            action: 'OPEN',
            user: Office.context.mailbox.userProfile.emailAddress,
            workbook: 'LoanLossProvision_v2.1.0.xlsx'
        })
    });
    
    const result = await response.json();
    if (!result.allowed) {
        alert('Access denied: ' + result.reason);
        Office.context.document.close();
    }
}

// When user edits a cell
async function onCellChange(cell, oldValue, newValue) {
    const response = await fetch('/api/agents/validate-change', {
        method: 'POST',
        body: JSON.stringify({
            action: 'EDIT',
            cell: cell.address,
            oldValue: oldValue,
            newValue: newValue,
            user: getCurrentUser()
        })
    });
    
    const result = await response.json();
    if (!result.valid) {
        cell.value = oldValue;  // Revert
        alert('Change blocked: ' + result.reason);
    }
}
```

## File Naming Convention

```
<ApplicationName>_v<MajorVersion>.<MinorVersion>.<PatchVersion>_<Date>.xlsx

Examples:
LoanLossProvision_v2.1.0_20240115.xlsx
LoanLossProvision_v2.1.1_20240220.xlsx
```

## Metadata

The workbook should include standard Excel metadata:

- **Title**: Loan Loss Provision Calculator
- **Subject**: Risk Management - Credit Risk
- **Category**: End User Computing - High Risk
- **Keywords**: Provision, Credit Risk, Regulatory, Basel III, IFRS 9
- **Comments**: See Change History sheet for version details
- **Author**: Risk Management Department
- **Company**: [Bank Name]

## File Location

Recommended storage hierarchy:

```
SharePoint or OneDrive:
  /RiskManagement
    /EUC
      /LoanLossProvision
        /Production
          LoanLossProvision_v2.1.0.xlsx  (current)
        /Archive
          /2024
            LoanLossProvision_v2.0.5_20240101.xlsx
            LoanLossProvision_v2.0.6_20240115.xlsx
        /Development
          LoanLossProvision_v2.2.0_DRAFT.xlsx
        /Documentation
          User_Guide.pdf
          Methodology.pdf
          Compliance_Evidence.pdf
        /TestData
          Sample_Portfolio.xlsx
          Test_Cases.xlsx
```

## Next Steps

1. **Create the Excel Template**: Build the workbook following this specification
2. **Populate Sample Data**: Add realistic test data
3. **Test Formulas**: Validate all calculations
4. **Configure Named Ranges**: Set up all named ranges
5. **Document Formulas**: Add comments explaining complex formulas
6. **Review with Stakeholders**: Get business owner approval
7. **Integrate with Agents**: Connect Excel Add-in to agent APIs
8. **Perform UAT**: User acceptance testing with real users
9. **Deploy to Production**: With full audit trail and approval
