/**
 * Audit Trail Agent
 * 
 * Maintains comprehensive, tamper-proof logs of all activities using
 * cryptographic hash chains to ensure log integrity.
 */

const crypto = require('crypto');
const { EventEmitter } = require('events');

class AuditTrailAgent extends EventEmitter {
    constructor(storage) {
        super();
        this.storage = storage; // Database or file storage
        this.eventTypes = [
            'WORKBOOK_OPEN',
            'WORKBOOK_CLOSE',
            'CELL_EDIT',
            'FORMULA_CHANGE',
            'DATA_IMPORT',
            'CALCULATION',
            'APPROVAL',
            'CERTIFICATION',
            'ACCESS_DENIED',
            'VALIDATION_FAILED'
        ];
    }

    /**
     * Log an event to the audit trail
     * @param {Object} event - Event to log
     * @returns {Object} Created log entry
     */
    async logEvent(event) {
        // Validate event
        this.validateEvent(event);

        // Create log entry
        const logEntry = {
            eventId: this.generateUUID(),
            timestamp: new Date().toISOString(),
            userId: event.user?.id || 'SYSTEM',
            userName: event.user?.name || 'System',
            action: event.action,
            resource: event.resource || null,
            ipAddress: event.ipAddress || null,
            sessionId: event.sessionId || null,
            beforeValue: event.beforeValue || null,
            afterValue: event.afterValue || null,
            status: event.status || 'SUCCESS',
            details: event.details || {},
            metadata: {
                userAgent: event.userAgent,
                location: event.location,
                deviceId: event.deviceId
            }
        };

        // Generate hash chain
        const previousHash = await this.getLastLogHash();
        logEntry.previousHash = previousHash;
        logEntry.hash = this.generateHash(logEntry, previousHash);

        // Store log entry
        await this.storage.append(logEntry);

        // Emit event for monitoring
        this.emit('log_created', logEntry);

        // Check for suspicious activity
        if (this.isSuspicious(event)) {
            this.emit('suspicious_activity', logEntry);
        }

        return logEntry;
    }

    /**
     * Generate cryptographic hash for log entry
     * @param {Object} entry - Log entry
     * @param {string} previousHash - Hash of previous entry
     * @returns {string} SHA-256 hash
     */
    generateHash(entry, previousHash) {
        // Create deterministic string representation
        const entryWithoutHash = { ...entry };
        delete entryWithoutHash.hash;
        delete entryWithoutHash.previousHash;

        // Sort keys for deterministic output
        const sortedData = JSON.stringify(entryWithoutHash, Object.keys(entryWithoutHash).sort());
        
        // Combine with previous hash
        const dataToHash = sortedData + (previousHash || '');

        // Generate SHA-256 hash
        return crypto.createHash('sha256')
            .update(dataToHash)
            .digest('hex');
    }

    /**
     * Get hash of the last log entry
     * @returns {string} Hash of last entry or null
     */
    async getLastLogHash() {
        const lastEntry = await this.storage.getLast();
        return lastEntry ? lastEntry.hash : null;
    }

    /**
     * Verify integrity of the audit log
     * @returns {Object} Verification result
     */
    async verifyLogIntegrity() {
        const logs = await this.storage.getAll();
        
        if (logs.length === 0) {
            return { valid: true, message: 'No logs to verify' };
        }

        // Verify first entry
        const firstEntry = logs[0];
        const expectedFirstHash = this.generateHash(firstEntry, null);
        if (expectedFirstHash !== firstEntry.hash) {
            return {
                valid: false,
                message: 'First entry hash mismatch',
                tamperedIndex: 0
            };
        }

        // Verify hash chain
        for (let i = 1; i < logs.length; i++) {
            const currentEntry = logs[i];
            const previousEntry = logs[i - 1];

            // Verify previous hash reference
            if (currentEntry.previousHash !== previousEntry.hash) {
                return {
                    valid: false,
                    message: 'Hash chain broken',
                    tamperedIndex: i,
                    details: {
                        expected: previousEntry.hash,
                        actual: currentEntry.previousHash
                    }
                };
            }

            // Verify current entry hash
            const expectedHash = this.generateHash(currentEntry, previousEntry.hash);
            if (expectedHash !== currentEntry.hash) {
                return {
                    valid: false,
                    message: 'Entry hash mismatch',
                    tamperedIndex: i
                };
            }
        }

        return {
            valid: true,
            message: 'Log integrity verified',
            entriesVerified: logs.length
        };
    }

    /**
     * Get audit logs with filtering
     * @param {Object} filters - Filter criteria
     * @returns {Array} Filtered log entries
     */
    async getLogs(filters = {}) {
        let logs = await this.storage.getAll();

        // Filter by user
        if (filters.userId) {
            logs = logs.filter(log => log.userId === filters.userId);
        }

        // Filter by action
        if (filters.action) {
            logs = logs.filter(log => log.action === filters.action);
        }

        // Filter by date range
        if (filters.startDate) {
            const startDate = new Date(filters.startDate);
            logs = logs.filter(log => new Date(log.timestamp) >= startDate);
        }

        if (filters.endDate) {
            const endDate = new Date(filters.endDate);
            logs = logs.filter(log => new Date(log.timestamp) <= endDate);
        }

        // Filter by resource
        if (filters.resource) {
            logs = logs.filter(log => 
                log.resource && log.resource.includes(filters.resource)
            );
        }

        // Pagination
        const page = filters.page || 1;
        const perPage = filters.perPage || 100;
        const startIndex = (page - 1) * perPage;
        const endIndex = startIndex + perPage;

        return {
            total: logs.length,
            page: page,
            perPage: perPage,
            totalPages: Math.ceil(logs.length / perPage),
            data: logs.slice(startIndex, endIndex)
        };
    }

    /**
     * Generate audit report
     * @param {Object} criteria - Report criteria
     * @returns {Object} Audit report
     */
    async generateReport(criteria) {
        const logs = await this.getLogs(criteria);

        // Aggregate statistics
        const stats = {
            totalEvents: logs.total,
            byAction: {},
            byUser: {},
            byStatus: {},
            timeline: []
        };

        logs.data.forEach(log => {
            // Count by action
            stats.byAction[log.action] = (stats.byAction[log.action] || 0) + 1;

            // Count by user
            stats.byUser[log.userId] = (stats.byUser[log.userId] || 0) + 1;

            // Count by status
            stats.byStatus[log.status] = (stats.byStatus[log.status] || 0) + 1;
        });

        // Generate timeline (daily aggregation)
        const timelineMap = {};
        logs.data.forEach(log => {
            const date = log.timestamp.split('T')[0];
            timelineMap[date] = (timelineMap[date] || 0) + 1;
        });

        stats.timeline = Object.entries(timelineMap).map(([date, count]) => ({
            date,
            count
        }));

        return {
            period: {
                start: criteria.startDate,
                end: criteria.endDate
            },
            statistics: stats,
            logs: logs
        };
    }

    /**
     * Detect suspicious activity patterns
     * @param {Object} event - Event to check
     * @returns {boolean} True if suspicious
     */
    isSuspicious(event) {
        const suspiciousPatterns = [
            // Multiple failed access attempts
            () => this.checkMultipleFailedAccess(event),
            // Off-hours access
            () => this.checkOffHoursAccess(event),
            // Bulk changes
            () => this.checkBulkChanges(event),
            // Unusual user behavior
            () => this.checkUnusualBehavior(event)
        ];

        return suspiciousPatterns.some(check => check());
    }

    /**
     * Check for multiple failed access attempts
     */
    async checkMultipleFailedAccess(event) {
        if (event.status !== 'FAILED' || event.action !== 'ACCESS_DENIED') {
            return false;
        }

        const recentLogs = await this.storage.getRecent(event.userId, 5);
        const failedAttempts = recentLogs.filter(
            log => log.status === 'FAILED' && log.action === 'ACCESS_DENIED'
        );

        return failedAttempts.length >= 3;
    }

    /**
     * Check for off-hours access
     */
    checkOffHoursAccess(event) {
        const hour = new Date(event.timestamp || new Date()).getHours();
        
        // Off-hours: before 6 AM or after 10 PM
        return hour < 6 || hour > 22;
    }

    /**
     * Check for bulk changes
     */
    checkBulkChanges(event) {
        // Flag if changing more than 100 cells at once
        if (event.action === 'CELL_EDIT' && event.details?.cellCount > 100) {
            return true;
        }

        return false;
    }

    /**
     * Check for unusual user behavior
     */
    async checkUnusualBehavior(event) {
        // This is a simplified check
        // In production, use ML-based anomaly detection
        
        const userActivity = await this.storage.getUserActivity(event.userId, 30); // last 30 days
        
        // Check if action is rare for this user
        const actionCount = userActivity.filter(log => log.action === event.action).length;
        const totalCount = userActivity.length;
        
        if (totalCount > 10 && actionCount === 0) {
            return true; // First time doing this action
        }

        return false;
    }

    /**
     * Validate event structure
     */
    validateEvent(event) {
        if (!event.action) {
            throw new Error('Event must have an action');
        }

        if (!this.eventTypes.includes(event.action)) {
            throw new Error(`Invalid event action: ${event.action}`);
        }
    }

    /**
     * Generate UUID
     */
    generateUUID() {
        return crypto.randomUUID();
    }

    /**
     * Export audit logs for compliance
     * @param {Object} criteria - Export criteria
     * @param {string} format - Export format (json, csv)
     * @returns {string} Exported data
     */
    async exportLogs(criteria, format = 'json') {
        const logs = await this.getLogs(criteria);

        if (format === 'csv') {
            return this.logsToCSV(logs.data);
        }

        return JSON.stringify(logs, null, 2);
    }

    /**
     * Convert logs to CSV format
     */
    logsToCSV(logs) {
        if (logs.length === 0) {
            return '';
        }

        // Headers
        const headers = [
            'Timestamp',
            'Event ID',
            'User ID',
            'User Name',
            'Action',
            'Resource',
            'Status',
            'Before Value',
            'After Value',
            'Hash'
        ];

        // Rows
        const rows = logs.map(log => [
            log.timestamp,
            log.eventId,
            log.userId,
            log.userName,
            log.action,
            log.resource || '',
            log.status,
            log.beforeValue || '',
            log.afterValue || '',
            log.hash
        ]);

        // Combine headers and rows
        const csv = [
            headers.join(','),
            ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
        ].join('\n');

        return csv;
    }
}

module.exports = AuditTrailAgent;
