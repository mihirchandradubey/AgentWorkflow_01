/**
 * Data Validation Agent
 * 
 * Validates input data quality, completeness, and consistency against
 * business rules defined in COMPLIANCE_RULES.md
 */

class DataValidationAgent {
    constructor(config = {}) {
        this.config = {
            requiredFields: config.requiredFields || [
                'account_id',
                'balance',
                'risk_rating',
                'maturity_date'
            ],
            dataTypes: config.dataTypes || {
                'account_id': 'string',
                'borrower_name': 'string',
                'balance': 'number',
                'risk_rating': 'enum',
                'industry': 'string',
                'origination_date': 'date',
                'maturity_date': 'date',
                'interest_rate': 'number',
                'collateral_value': 'number',
                'status': 'enum'
            },
            enums: config.enums || {
                'risk_rating': ['AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC', 'Default'],
                'status': ['Current', '30DPD', '60DPD', '90DPD', 'NPL']
            },
            ranges: config.ranges || {
                'balance': { min: 0, max: 100000000, softMax: 10000000 },
                'interest_rate': { min: 0, max: 0.30 },
                'collateral_value': { min: 0 }
            },
            tolerances: config.tolerances || {
                'portfolio_total': 0.0001 // 0.01%
            }
        };

        this.validationRules = this.loadValidationRules();
    }

    /**
     * Validate dataset against all rules
     * @param {Array} data - Array of loan records
     * @param {Object} context - Additional context (expected totals, etc.)
     * @returns {Object} Validation results
     */
    async validate(data, context = {}) {
        const issues = [];
        
        // Rule 4.1: Completeness Check
        const completenessIssues = this.checkCompleteness(data);
        issues.push(...completenessIssues);

        // Rule 4.2: Data Type Validation
        const typeIssues = this.checkDataTypes(data);
        issues.push(...typeIssues);

        // Rule 4.3: Range Validation
        const rangeIssues = this.checkRanges(data);
        issues.push(...rangeIssues);

        // Rule 4.4: Consistency Checks
        const consistencyIssues = await this.checkConsistency(data, context);
        issues.push(...consistencyIssues);

        // Additional checks
        const businessIssues = this.checkBusinessRules(data);
        issues.push(...businessIssues);

        // Calculate quality score
        const qualityScore = this.calculateQualityScore(issues, data.length);

        // Determine overall status
        const hasErrors = issues.some(i => i.severity === 'ERROR');
        const status = hasErrors ? 'FAIL' : 'PASS';

        return {
            status,
            qualityScore,
            totalRecords: data.length,
            issueCount: issues.length,
            issues,
            summary: this.generateSummary(issues)
        };
    }

    /**
     * Check data completeness (Rule 4.1)
     */
    checkCompleteness(data) {
        const issues = [];

        data.forEach((record, index) => {
            this.config.requiredFields.forEach(field => {
                if (record[field] === null || record[field] === undefined || record[field] === '') {
                    issues.push({
                        severity: 'ERROR',
                        rule: 'Rule 4.1',
                        ruleDescription: 'Input Data Completeness',
                        rowIndex: index,
                        field: field,
                        message: `Missing required field: ${field}`,
                        value: record[field]
                    });
                }
            });
        });

        return issues;
    }

    /**
     * Check data types (Rule 4.2)
     */
    checkDataTypes(data) {
        const issues = [];

        data.forEach((record, index) => {
            Object.entries(this.config.dataTypes).forEach(([field, expectedType]) => {
                const value = record[field];

                // Skip if null/undefined (caught by completeness check)
                if (value === null || value === undefined) {
                    return;
                }

                let isValid = true;
                let actualType = typeof value;

                switch (expectedType) {
                    case 'number':
                        isValid = typeof value === 'number' && !isNaN(value);
                        break;

                    case 'string':
                        isValid = typeof value === 'string';
                        break;

                    case 'date':
                        isValid = this.isValidDate(value);
                        actualType = isValid ? 'date' : actualType;
                        break;

                    case 'enum':
                        const validValues = this.config.enums[field];
                        isValid = validValues && validValues.includes(value);
                        actualType = isValid ? 'enum' : `invalid enum value: ${value}`;
                        break;
                }

                if (!isValid) {
                    issues.push({
                        severity: 'ERROR',
                        rule: 'Rule 4.2',
                        ruleDescription: 'Data Type Validation',
                        rowIndex: index,
                        field: field,
                        message: `Invalid data type for ${field}`,
                        expected: expectedType,
                        actual: actualType,
                        value: value
                    });
                }
            });
        });

        return issues;
    }

    /**
     * Check value ranges (Rule 4.3)
     */
    checkRanges(data) {
        const issues = [];

        data.forEach((record, index) => {
            Object.entries(this.config.ranges).forEach(([field, range]) => {
                const value = record[field];

                // Skip if not a number
                if (typeof value !== 'number') {
                    return;
                }

                // Check minimum
                if (range.min !== undefined && value < range.min) {
                    issues.push({
                        severity: 'ERROR',
                        rule: 'Rule 4.3',
                        ruleDescription: 'Range Validation',
                        rowIndex: index,
                        field: field,
                        message: `${field} below minimum`,
                        value: value,
                        min: range.min
                    });
                }

                // Check maximum
                if (range.max !== undefined && value > range.max) {
                    issues.push({
                        severity: 'ERROR',
                        rule: 'Rule 4.3',
                        ruleDescription: 'Range Validation',
                        rowIndex: index,
                        field: field,
                        message: `${field} exceeds maximum`,
                        value: value,
                        max: range.max
                    });
                }

                // Check soft maximum (warning only)
                if (range.softMax !== undefined && value > range.softMax) {
                    issues.push({
                        severity: 'WARNING',
                        rule: 'Rule 4.3',
                        ruleDescription: 'Range Validation',
                        rowIndex: index,
                        field: field,
                        message: `${field} exceeds typical range`,
                        value: value,
                        softMax: range.softMax
                    });
                }
            });
        });

        return issues;
    }

    /**
     * Check data consistency (Rule 4.4)
     */
    async checkConsistency(data, context) {
        const issues = [];

        // Check portfolio total
        const actualTotal = data.reduce((sum, record) => {
            return sum + (record.balance || 0);
        }, 0);

        if (context.expectedTotal) {
            const variance = Math.abs(actualTotal - context.expectedTotal) / context.expectedTotal;
            const tolerance = this.config.tolerances.portfolio_total;

            if (variance > tolerance) {
                issues.push({
                    severity: 'WARNING',
                    rule: 'Rule 4.4',
                    ruleDescription: 'Consistency Checks',
                    message: 'Portfolio total mismatch',
                    expected: context.expectedTotal,
                    actual: actualTotal,
                    variance: variance,
                    tolerance: tolerance
                });
            }
        }

        // Check date consistency (maturity > origination)
        data.forEach((record, index) => {
            if (record.maturity_date && record.origination_date) {
                const maturity = new Date(record.maturity_date);
                const origination = new Date(record.origination_date);

                if (maturity <= origination) {
                    issues.push({
                        severity: 'ERROR',
                        rule: 'Rule 4.4',
                        ruleDescription: 'Consistency Checks',
                        rowIndex: index,
                        message: 'Maturity date must be after origination date',
                        originationDate: record.origination_date,
                        maturityDate: record.maturity_date
                    });
                }
            }
        });

        // Check collateral vs balance
        data.forEach((record, index) => {
            if (record.collateral_value && record.balance) {
                // Warning if under-collateralized
                if (record.collateral_value < record.balance * 0.5) {
                    issues.push({
                        severity: 'WARNING',
                        rule: 'Rule 4.4',
                        ruleDescription: 'Consistency Checks',
                        rowIndex: index,
                        message: 'Low collateral coverage',
                        balance: record.balance,
                        collateral: record.collateral_value,
                        coverage: (record.collateral_value / record.balance * 100).toFixed(2) + '%'
                    });
                }
            }
        });

        return issues;
    }

    /**
     * Check business rules
     */
    checkBusinessRules(data) {
        const issues = [];

        data.forEach((record, index) => {
            // High-risk rating with low interest rate
            if (['BB', 'B', 'CCC', 'Default'].includes(record.risk_rating)) {
                if (record.interest_rate < 0.05) { // 5%
                    issues.push({
                        severity: 'WARNING',
                        rule: 'Business Rule',
                        rowIndex: index,
                        message: 'Low interest rate for high-risk loan',
                        riskRating: record.risk_rating,
                        interestRate: (record.interest_rate * 100).toFixed(2) + '%'
                    });
                }
            }

            // NPL status should have high risk rating
            if (record.status === 'NPL' && !['CCC', 'Default'].includes(record.risk_rating)) {
                issues.push({
                    severity: 'WARNING',
                    rule: 'Business Rule',
                    rowIndex: index,
                    message: 'NPL status inconsistent with risk rating',
                    status: record.status,
                    riskRating: record.risk_rating
                });
            }
        });

        return issues;
    }

    /**
     * Calculate data quality score (0-100)
     */
    calculateQualityScore(issues, totalRecords) {
        if (totalRecords === 0) {
            return 0;
        }

        // Weight by severity
        const weights = {
            'ERROR': 10,
            'WARNING': 3,
            'INFO': 1
        };

        const totalPenalty = issues.reduce((sum, issue) => {
            return sum + (weights[issue.severity] || 0);
        }, 0);

        // Maximum possible penalty (if every record has an error)
        const maxPenalty = totalRecords * weights.ERROR;

        // Score = 100 - (penalty / max_penalty * 100)
        const score = Math.max(0, 100 - (totalPenalty / maxPenalty * 100));

        return Math.round(score * 100) / 100; // Round to 2 decimals
    }

    /**
     * Generate summary statistics
     */
    generateSummary(issues) {
        const summary = {
            totalIssues: issues.length,
            byRule: {},
            bySeverity: {
                ERROR: 0,
                WARNING: 0,
                INFO: 0
            },
            byField: {}
        };

        issues.forEach(issue => {
            // Count by rule
            summary.byRule[issue.rule] = (summary.byRule[issue.rule] || 0) + 1;

            // Count by severity
            summary.bySeverity[issue.severity]++;

            // Count by field
            if (issue.field) {
                summary.byField[issue.field] = (summary.byField[issue.field] || 0) + 1;
            }
        });

        return summary;
    }

    /**
     * Validate a single record
     */
    validateRecord(record) {
        return this.validate([record]);
    }

    /**
     * Check if a value is a valid date
     */
    isValidDate(value) {
        if (value instanceof Date) {
            return !isNaN(value.getTime());
        }

        if (typeof value === 'string') {
            const date = new Date(value);
            return !isNaN(date.getTime());
        }

        return false;
    }

    /**
     * Load validation rules from configuration
     */
    loadValidationRules() {
        // In production, load from COMPLIANCE_RULES.md or database
        return {
            'Rule 4.1': {
                name: 'Input Data Completeness',
                description: 'All required data fields must be populated'
            },
            'Rule 4.2': {
                name: 'Data Type Validation',
                description: 'Data must match expected types and formats'
            },
            'Rule 4.3': {
                name: 'Range Validation',
                description: 'Data must be within reasonable bounds'
            },
            'Rule 4.4': {
                name: 'Consistency Checks',
                description: 'Related data must be consistent'
            }
        };
    }

    /**
     * Get validation statistics for monitoring
     */
    async getValidationStatistics(timeRange) {
        // This would query historical validation results
        // For now, return placeholder
        return {
            timeRange,
            totalValidations: 0,
            averageQualityScore: 0,
            commonIssues: []
        };
    }
}

module.exports = DataValidationAgent;
