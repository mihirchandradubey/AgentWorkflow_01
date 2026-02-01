/**
 * Test suite for Data Validation Agent
 */

const DataValidationAgent = require('../agents/data-validation-agent');

describe('DataValidationAgent', () => {
    let agent;

    beforeEach(() => {
        agent = new DataValidationAgent();
    });

    describe('Completeness Validation (Rule 4.1)', () => {
        test('should pass when all required fields are present', async () => {
            const data = [
                {
                    account_id: 'L001',
                    balance: 1000000,
                    risk_rating: 'A',
                    maturity_date: '2027-01-15'
                },
                {
                    account_id: 'L002',
                    balance: 500000,
                    risk_rating: 'BBB',
                    maturity_date: '2026-06-30'
                }
            ];

            const result = await agent.validate(data);

            expect(result.status).toBe('PASS');
            expect(result.issues).toHaveLength(0);
        });

        test('should detect missing required fields', async () => {
            const data = [
                {
                    account_id: 'L001',
                    balance: null, // Missing required field
                    risk_rating: 'A',
                    maturity_date: '2027-01-15'
                },
                {
                    account_id: null, // Missing required field
                    balance: 500000,
                    risk_rating: 'BBB',
                    maturity_date: '2026-06-30'
                }
            ];

            const result = await agent.validate(data);

            expect(result.status).toBe('FAIL');
            expect(result.issues.length).toBeGreaterThan(0);
            expect(result.issues[0].rule).toBe('Rule 4.1');
            expect(result.issues[0].severity).toBe('ERROR');
        });
    });

    describe('Data Type Validation (Rule 4.2)', () => {
        test('should detect invalid data types', async () => {
            const data = [
                {
                    account_id: 'L001',
                    balance: 'invalid', // Should be number
                    risk_rating: 'A',
                    maturity_date: '2027-01-15'
                }
            ];

            const result = await agent.validate(data);

            expect(result.status).toBe('FAIL');
            const typeIssues = result.issues.filter(i => i.rule === 'Rule 4.2');
            expect(typeIssues.length).toBeGreaterThan(0);
            expect(typeIssues[0].expected).toBe('number');
        });

        test('should validate enum values', async () => {
            const data = [
                {
                    account_id: 'L001',
                    balance: 1000000,
                    risk_rating: 'INVALID_RATING', // Invalid enum
                    maturity_date: '2027-01-15'
                }
            ];

            const result = await agent.validate(data);

            expect(result.status).toBe('FAIL');
            const enumIssues = result.issues.filter(
                i => i.rule === 'Rule 4.2' && i.field === 'risk_rating'
            );
            expect(enumIssues.length).toBeGreaterThan(0);
        });

        test('should validate date formats', async () => {
            const data = [
                {
                    account_id: 'L001',
                    balance: 1000000,
                    risk_rating: 'A',
                    maturity_date: 'invalid-date'
                }
            ];

            const result = await agent.validate(data);

            expect(result.status).toBe('FAIL');
            const dateIssues = result.issues.filter(
                i => i.rule === 'Rule 4.2' && i.field === 'maturity_date'
            );
            expect(dateIssues.length).toBeGreaterThan(0);
        });
    });

    describe('Range Validation (Rule 4.3)', () => {
        test('should detect negative balances', async () => {
            const data = [
                {
                    account_id: 'L001',
                    balance: -1000, // Negative not allowed
                    risk_rating: 'A',
                    maturity_date: '2027-01-15'
                }
            ];

            const result = await agent.validate(data);

            expect(result.status).toBe('FAIL');
            const rangeIssues = result.issues.filter(i => i.rule === 'Rule 4.3');
            expect(rangeIssues.length).toBeGreaterThan(0);
            expect(rangeIssues[0].message).toContain('below minimum');
        });

        test('should warn on values exceeding soft maximum', async () => {
            const data = [
                {
                    account_id: 'L001',
                    balance: 15000000, // Above soft max of 10M
                    risk_rating: 'A',
                    maturity_date: '2027-01-15'
                }
            ];

            const result = await agent.validate(data);

            const warnings = result.issues.filter(i => i.severity === 'WARNING');
            expect(warnings.length).toBeGreaterThan(0);
            expect(warnings[0].message).toContain('typical range');
        });
    });

    describe('Consistency Validation (Rule 4.4)', () => {
        test('should detect portfolio total mismatch', async () => {
            const data = [
                {
                    account_id: 'L001',
                    balance: 1000000,
                    risk_rating: 'A',
                    maturity_date: '2027-01-15'
                }
            ];

            const context = {
                expectedTotal: 1500000 // Mismatch
            };

            const result = await agent.validate(data, context);

            const consistencyIssues = result.issues.filter(i => i.rule === 'Rule 4.4');
            expect(consistencyIssues.length).toBeGreaterThan(0);
        });

        test('should detect maturity before origination', async () => {
            const data = [
                {
                    account_id: 'L001',
                    balance: 1000000,
                    risk_rating: 'A',
                    origination_date: '2027-01-15',
                    maturity_date: '2026-01-15' // Before origination
                }
            ];

            const result = await agent.validate(data);

            const dateIssues = result.issues.filter(
                i => i.rule === 'Rule 4.4' && i.message.includes('Maturity')
            );
            expect(dateIssues.length).toBeGreaterThan(0);
        });
    });

    describe('Quality Score Calculation', () => {
        test('should calculate 100% for perfect data', async () => {
            const data = [
                {
                    account_id: 'L001',
                    balance: 1000000,
                    risk_rating: 'A',
                    maturity_date: '2027-01-15'
                }
            ];

            const result = await agent.validate(data);

            expect(result.qualityScore).toBe(100);
        });

        test('should reduce score based on issue severity', async () => {
            const data = [
                {
                    account_id: 'L001',
                    balance: null, // ERROR
                    risk_rating: 'A',
                    maturity_date: '2027-01-15'
                }
            ];

            const result = await agent.validate(data);

            expect(result.qualityScore).toBeLessThan(100);
        });
    });

    describe('Summary Generation', () => {
        test('should generate summary statistics', async () => {
            const data = [
                {
                    account_id: 'L001',
                    balance: null,
                    risk_rating: 'INVALID',
                    maturity_date: '2027-01-15'
                }
            ];

            const result = await agent.validate(data);

            expect(result.summary).toBeDefined();
            expect(result.summary.totalIssues).toBeGreaterThan(0);
            expect(result.summary.bySeverity).toBeDefined();
            expect(result.summary.byRule).toBeDefined();
        });
    });

    describe('Single Record Validation', () => {
        test('should validate a single record', async () => {
            const record = {
                account_id: 'L001',
                balance: 1000000,
                risk_rating: 'A',
                maturity_date: '2027-01-15'
            };

            const result = await agent.validateRecord(record);

            expect(result.status).toBe('PASS');
            expect(result.totalRecords).toBe(1);
        });
    });

    describe('Business Rules', () => {
        test('should warn on low interest rate for high-risk loan', async () => {
            const data = [
                {
                    account_id: 'L001',
                    balance: 1000000,
                    risk_rating: 'CCC',
                    interest_rate: 0.03, // 3% - too low for CCC
                    maturity_date: '2027-01-15'
                }
            ];

            const result = await agent.validate(data);

            const businessWarnings = result.issues.filter(
                i => i.rule === 'Business Rule' && i.message.includes('interest rate')
            );
            expect(businessWarnings.length).toBeGreaterThan(0);
        });

        test('should warn on NPL with investment grade rating', async () => {
            const data = [
                {
                    account_id: 'L001',
                    balance: 1000000,
                    risk_rating: 'A', // Investment grade
                    status: 'NPL', // Non-performing loan
                    maturity_date: '2027-01-15'
                }
            ];

            const result = await agent.validate(data);

            const businessWarnings = result.issues.filter(
                i => i.rule === 'Business Rule' && i.message.includes('NPL')
            );
            expect(businessWarnings.length).toBeGreaterThan(0);
        });
    });
});
