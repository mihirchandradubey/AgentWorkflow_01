# Example Implementations

This directory contains reference implementations of the agentic workflow components described in the main documentation.

## Directory Structure

```
examples/
├── agents/                          # Agent implementations
│   ├── audit-trail-agent.js        # Audit Trail Agent (complete)
│   └── data-validation-agent.js    # Data Validation Agent (complete)
│
├── config/                          # Configuration files
│   └── workflow-config.yaml        # Workflow orchestration config
│
├── tests/                           # Test suites
│   └── data-validation-agent.test.js
│
├── package.json                     # Node.js dependencies
└── README.md                        # This file
```

## Available Examples

### 1. Audit Trail Agent (`agents/audit-trail-agent.js`)

**Status**: ✅ Complete implementation

**Features**:
- Comprehensive event logging
- Cryptographic hash chain for tamper-proof logs
- Log integrity verification
- Suspicious activity detection
- Audit report generation
- Export to JSON/CSV

**Usage**:
```javascript
const AuditTrailAgent = require('./agents/audit-trail-agent');

// Initialize with storage backend
const agent = new AuditTrailAgent(storage);

// Log an event
await agent.logEvent({
    user: { id: 'user123', name: 'John Doe' },
    action: 'FORMULA_CHANGE',
    resource: 'Sheet1!A1',
    beforeValue: '=SUM(B1:B10)',
    afterValue: '=SUM(B1:B20)',
    ipAddress: '192.168.1.100'
});

// Verify log integrity
const verification = await agent.verifyLogIntegrity();
console.log(verification.valid); // true/false

// Get audit logs
const logs = await agent.getLogs({
    userId: 'user123',
    startDate: '2024-01-01',
    endDate: '2024-12-31'
});

// Generate report
const report = await agent.generateReport({
    startDate: '2024-01-01',
    endDate: '2024-12-31'
});
```

### 2. Data Validation Agent (`agents/data-validation-agent.js`)

**Status**: ✅ Complete implementation

**Features**:
- Completeness validation (Rule 4.1)
- Data type validation (Rule 4.2)
- Range validation (Rule 4.3)
- Consistency checks (Rule 4.4)
- Business rule validation
- Quality score calculation
- Detailed issue reporting

**Usage**:
```javascript
const DataValidationAgent = require('./agents/data-validation-agent');

// Initialize
const agent = new DataValidationAgent();

// Validate dataset
const result = await agent.validate(portfolioData, {
    expectedTotal: 100000000
});

console.log(result.status);        // PASS/FAIL
console.log(result.qualityScore);  // 0-100
console.log(result.issues);        // Array of issues

// Validate single record
const recordResult = await agent.validateRecord(loan);
```

### 3. Workflow Configuration (`config/workflow-config.yaml`)

**Status**: ✅ Complete configuration

**Features**:
- 6 workflow definitions (WORKBOOK_OPEN, FORMULA_CHANGE, etc.)
- Agent execution order
- Timeout and retry policies
- Notification rules
- Scheduled tasks
- Global and agent-specific configuration

**Workflows**:
- `WORKBOOK_OPEN`: Access control → Audit → Quick validation
- `FORMULA_CHANGE`: Full validation with approval workflow
- `DATA_CHANGE`: Data validation and logging
- `CALCULATION`: Comprehensive validation before/after
- `APPROVAL`: Segregation of duties check
- `SCHEDULED_REVIEW`: Daily compliance monitoring

## Running the Examples

### Prerequisites

```bash
# Install Node.js 18+
node --version  # Should be >= 18.0.0

# Install dependencies
cd examples
npm install
```

### Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage
```

### Testing Individual Agents

```javascript
// Create a test file: test-agent.js
const DataValidationAgent = require('./agents/data-validation-agent');

async function testValidation() {
    const agent = new DataValidationAgent();
    
    const testData = [
        {
            account_id: 'L001',
            balance: 1000000,
            risk_rating: 'A',
            maturity_date: '2027-01-15'
        }
    ];
    
    const result = await agent.validate(testData);
    console.log('Validation Result:', result);
}

testValidation();
```

```bash
# Run the test
node test-agent.js
```

## Next Steps

### To Complete the POC

The following components need to be implemented to have a fully functional system:

1. **Remaining Agents**:
   - ✅ Audit Trail Agent (done)
   - ✅ Data Validation Agent (done)
   - ⬜ Access Control Agent
   - ⬜ Formula Verification Agent
   - ⬜ Compliance Checker Agent
   - ⬜ Change Management Agent
   - ⬜ Testing & Validation Agent

2. **Orchestration Engine**:
   - ⬜ Event routing
   - ⬜ Agent coordination
   - ⬜ Error handling
   - ⬜ State management

3. **API Server**:
   - ⬜ REST API endpoints
   - ⬜ Authentication/authorization
   - ⬜ Request validation
   - ⬜ Response formatting

4. **Storage Layer**:
   - ⬜ Database schemas
   - ⬜ Storage adapters
   - ⬜ Migration scripts
   - ⬜ Backup procedures

5. **Excel Integration**:
   - ⬜ Office.js Add-in
   - ⬜ Event handlers
   - ⬜ UI components
   - ⬜ Real-time communication

6. **Deployment**:
   - ⬜ Docker configuration
   - ⬜ Kubernetes manifests
   - ⬜ CI/CD pipeline
   - ⬜ Monitoring setup

### Implementation Order

We recommend implementing in this order:

**Phase 1** (Weeks 1-2):
1. Implement remaining agents (following the pattern in existing examples)
2. Create storage adapters (PostgreSQL for metadata, file system for logs)
3. Build orchestration engine

**Phase 2** (Weeks 3-4):
4. Create REST API server
5. Implement authentication/authorization
6. Add comprehensive tests

**Phase 3** (Weeks 5-6):
7. Develop Excel Add-in
8. Integrate all components
9. Perform integration testing

**Phase 4** (Weeks 7-8):
10. Deploy to test environment
11. User acceptance testing
12. Performance optimization

## Example: Building Access Control Agent

Following the pattern from the existing agents, here's how to implement the Access Control Agent:

```javascript
// agents/access-control-agent.js
class AccessControlAgent {
    constructor(auditAgent, config = {}) {
        this.auditAgent = auditAgent;
        this.rolePermissions = config.rolePermissions || {
            'Viewer': ['READ'],
            'Editor': ['READ', 'EDIT_DATA'],
            'Approver': ['READ', 'APPROVE', 'CERTIFY'],
            'Admin': ['READ', 'EDIT_DATA', 'EDIT_FORMULA', 'MANAGE_ACCESS']
        };
    }
    
    async checkAccess(user, action, resource) {
        // 1. Authenticate
        if (!user.isAuthenticated) {
            await this.auditAgent.logEvent({
                user, action: 'ACCESS_DENIED',
                resource, reason: 'Not authenticated'
            });
            return { allowed: false, reason: 'Authentication required' };
        }
        
        // 2. Check permissions
        const requiredPermission = this.getRequiredPermission(action);
        const userPermissions = this.getUserPermissions(user);
        
        if (!userPermissions.includes(requiredPermission)) {
            await this.auditAgent.logEvent({
                user, action: 'ACCESS_DENIED',
                resource, reason: 'Insufficient permissions'
            });
            return { allowed: false, reason: `Requires ${requiredPermission}` };
        }
        
        // 3. Check segregation of duties
        if (action === 'APPROVE') {
            const preparedBy = await this.getPreparedBy(resource);
            if (preparedBy === user.id) {
                await this.auditAgent.logEvent({
                    user, action: 'ACCESS_DENIED',
                    resource, reason: 'SoD violation'
                });
                return { allowed: false, reason: 'Cannot approve own work' };
            }
        }
        
        // 4. Log and allow
        await this.auditAgent.logEvent({
            user, action, resource, status: 'ALLOWED'
        });
        
        return { allowed: true };
    }
    
    // ... rest of implementation
}
```

## Testing Strategy

Each agent should have comprehensive tests covering:

1. **Happy Path**: Normal, expected operation
2. **Validation**: Input validation and error handling
3. **Edge Cases**: Boundary conditions, empty data, etc.
4. **Integration**: Agent interactions
5. **Performance**: Response time under load

See `tests/data-validation-agent.test.js` for a complete example.

## Configuration

All configuration is centralized in `config/workflow-config.yaml`:

- Workflow definitions
- Agent settings
- Timeouts and retries
- Notification rules
- Schedules

Environment-specific values use environment variables:
```yaml
connection_string: "${DATABASE_URL}"
smtp_host: "${SMTP_HOST}"
```

Set these in a `.env` file:
```
DATABASE_URL=postgresql://localhost:5432/euc_compliance
SMTP_HOST=smtp.gmail.com
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx
```

## Documentation

Each agent should include:

1. **JSDoc comments**: For all public methods
2. **README**: Usage examples and configuration
3. **Tests**: Demonstrating expected behavior
4. **Integration guide**: How it fits with other agents

## Support

For questions or issues with the examples:

1. Review the main documentation:
   - [AGENT_ARCHITECTURE.md](../AGENT_ARCHITECTURE.md)
   - [IMPLEMENTATION_GUIDE.md](../IMPLEMENTATION_GUIDE.md)
   - [COMPLIANCE_RULES.md](../COMPLIANCE_RULES.md)

2. Check test files for usage examples

3. Refer to inline code comments

## Contributing

To add new examples:

1. Follow the established code structure
2. Include comprehensive JSDoc comments
3. Add unit tests
4. Update this README
5. Ensure code passes linting

## License

MIT - See LICENSE file for details
