/**
 * K6 Test Helper Utilities
 * Common functions for performance testing
 */

import http from 'k6/http';
import { check } from 'k6';

/**
 * Validate API response structure
 */
export function validateApiResponse(response, expectedFields = []) {
    const checks = {
        'status is 200': response.status === 200,
        'has response body': response.body && response.body.length > 0,
        'is valid JSON': (() => {
            try {
                JSON.parse(response.body);
                return true;
            } catch (e) {
                return false;
            }
        })()
    };
    
    // Check for expected fields in response
    if (expectedFields.length > 0) {
        try {
            const data = JSON.parse(response.body);
            expectedFields.forEach(field => {
                checks[`has ${field}`] = data.hasOwnProperty(field);
            });
        } catch (e) {
            checks['valid JSON for field check'] = false;
        }
    }
    
    return check(response, checks);
}

/**
 * Generate realistic search payload
 */
export function generateSearchPayload(query, schemas, limit = 100, searchTypes = ['keyword', 'phonetic', 'similarity']) {
    return {
        query: query,
        schemas: schemas,
        limit: limit,
        search_types: searchTypes
    };
}

/**
 * Make API request with retry logic
 */
export function makeApiRequestWithRetry(url, payload, headers, maxRetries = 3) {
    let lastResponse = null;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        const response = http.post(url, JSON.stringify(payload), { headers });
        
        if (response.status === 200) {
            return response;
        }
        
        lastResponse = response;
        
        if (attempt < maxRetries) {
            console.log(`⚠️  Attempt ${attempt} failed (${response.status}), retrying...`);
            // Exponential backoff
            const delay = Math.pow(2, attempt) * 1000;
            sleep(delay / 1000);
        }
    }
    
    return lastResponse;
}

/**
 * Calculate performance metrics
 */
export function calculateMetrics(responses) {
    const successful = responses.filter(r => r.status === 200);
    const failed = responses.filter(r => r.status !== 200);
    
    const responseTimes = successful.map(r => r.timings.duration);
    const avgResponseTime = responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length;
    const maxResponseTime = Math.max(...responseTimes);
    const minResponseTime = Math.min(...responseTimes);
    
    return {
        totalRequests: responses.length,
        successfulRequests: successful.length,
        failedRequests: failed.length,
        successRate: (successful.length / responses.length) * 100,
        averageResponseTime: avgResponseTime,
        maxResponseTime: maxResponseTime,
        minResponseTime: minResponseTime
    };
}

/**
 * Log performance summary
 */
export function logPerformanceSummary(metrics) {
    console.log('\n📊 Performance Summary:');
    console.log(`Total Requests: ${metrics.totalRequests}`);
    console.log(`Successful: ${metrics.successfulRequests} (${metrics.successRate.toFixed(2)}%)`);
    console.log(`Failed: ${metrics.failedRequests}`);
    console.log(`Avg Response Time: ${metrics.averageResponseTime.toFixed(2)}ms`);
    console.log(`Max Response Time: ${metrics.maxResponseTime}ms`);
    console.log(`Min Response Time: ${metrics.minResponseTime}ms`);
}

/**
 * Check system health
 */
export function checkSystemHealth(baseUrl, apiKey) {
    const healthUrl = `${baseUrl}/health`;
    const headers = { 'x-api-key': apiKey };
    
    try {
        const response = http.get(healthUrl, { headers });
        return {
            isHealthy: response.status === 200,
            status: response.status,
            responseTime: response.timings.duration
        };
    } catch (e) {
        return {
            isHealthy: false,
            status: 'error',
            responseTime: 0,
            error: e.message
        };
    }
}

/**
 * Generate test report data
 */
export function generateTestReport(testName, startTime, endTime, metrics) {
    const duration = (endTime - startTime) / 1000; // seconds
    
    return {
        testName: testName,
        startTime: new Date(startTime).toISOString(),
        endTime: new Date(endTime).toISOString(),
        duration: `${duration.toFixed(2)}s`,
        metrics: metrics,
        summary: {
            throughput: (metrics.totalRequests / duration).toFixed(2),
            errorRate: ((metrics.failedRequests / metrics.totalRequests) * 100).toFixed(2),
            avgLatency: metrics.averageResponseTime.toFixed(2)
        }
    };
}

/**
 * Advanced performance analysis
 */
export function analyzePerformance(responses, thresholds = {}) {
    const defaultThresholds = {
        maxResponseTime: 5000,
        errorRate: 0.1,
        p95ResponseTime: 3000,
        p99ResponseTime: 5000
    };
    
    const finalThresholds = { ...defaultThresholds, ...thresholds };
    
    const successful = responses.filter(r => r.status === 200);
    const failed = responses.filter(r => r.status !== 200);
    
    const responseTimes = successful.map(r => r.timings.duration).sort((a, b) => a - b);
    
    // Calculate percentiles
    const p50 = responseTimes[Math.floor(responseTimes.length * 0.5)];
    const p95 = responseTimes[Math.floor(responseTimes.length * 0.95)];
    const p99 = responseTimes[Math.floor(responseTimes.length * 0.99)];
    
    const errorRate = failed.length / responses.length;
    const maxResponseTime = Math.max(...responseTimes);
    const avgResponseTime = responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length;
    
    // Performance analysis
    const analysis = {
        totalRequests: responses.length,
        successfulRequests: successful.length,
        failedRequests: failed.length,
        errorRate: errorRate,
        averageResponseTime: avgResponseTime,
        maxResponseTime: maxResponseTime,
        p50ResponseTime: p50,
        p95ResponseTime: p95,
        p99ResponseTime: p99,
        thresholds: finalThresholds,
        performance: {
            meetsMaxResponseTime: maxResponseTime <= finalThresholds.maxResponseTime,
            meetsErrorRate: errorRate <= finalThresholds.errorRate,
            meetsP95: p95 <= finalThresholds.p95ResponseTime,
            meetsP99: p99 <= finalThresholds.p99ResponseTime,
            overallPass: maxResponseTime <= finalThresholds.maxResponseTime && 
                        errorRate <= finalThresholds.errorRate &&
                        p95 <= finalThresholds.p95ResponseTime
        }
    };
    
    return analysis;
}

/**
 * Generate detailed performance report
 */
export function generateDetailedReport(testName, startTime, endTime, responses, thresholds = {}) {
    const duration = (endTime - startTime) / 1000;
    const analysis = analyzePerformance(responses, thresholds);
    
    return {
        testInfo: {
            name: testName,
            startTime: new Date(startTime).toISOString(),
            endTime: new Date(endTime).toISOString(),
            duration: `${duration.toFixed(2)}s`,
            vus: __ENV.VUS || 'unknown'
        },
        performance: analysis,
        summary: {
            throughput: (analysis.totalRequests / duration).toFixed(2),
            successRate: ((analysis.successfulRequests / analysis.totalRequests) * 100).toFixed(2),
            errorRate: (analysis.errorRate * 100).toFixed(2),
            avgLatency: analysis.averageResponseTime.toFixed(2),
            maxLatency: analysis.maxResponseTime,
            p95Latency: analysis.p95ResponseTime,
            p99Latency: analysis.p99ResponseTime,
            overallPass: analysis.performance.overallPass
        }
    };
}

/**
 * Simulate realistic user behavior patterns
 */
export function simulateUserBehavior() {
    const patterns = [
        'quick_search',      // Fast searches, short think time
        'thorough_search',   // Slower searches, longer think time
        'exploratory',       // Multiple related searches
        'casual_browsing'    // Random searches with variable timing
    ];
    
    const pattern = patterns[Math.floor(Math.random() * patterns.length)];
    
    switch (pattern) {
        case 'quick_search':
            return {
                thinkTime: Math.random() * 1 + 0.5, // 0.5-1.5 seconds
                searchLimit: Math.floor(Math.random() * 20) + 5, // 5-25
                searchTypes: ['keyword']
            };
        case 'thorough_search':
            return {
                thinkTime: Math.random() * 3 + 2, // 2-5 seconds
                searchLimit: Math.floor(Math.random() * 100) + 50, // 50-150
                searchTypes: ['keyword', 'phonetic', 'similarity']
            };
        case 'exploratory':
            return {
                thinkTime: Math.random() * 2 + 1, // 1-3 seconds
                searchLimit: Math.floor(Math.random() * 50) + 25, // 25-75
                searchTypes: ['keyword', 'similarity']
            };
        case 'casual_browsing':
        default:
            return {
                thinkTime: Math.random() * 4 + 1, // 1-5 seconds
                searchLimit: Math.floor(Math.random() * 30) + 10, // 10-40
                searchTypes: ['keyword']
            };
    }
}

/**
 * Monitor system resources during test
 */
export function monitorSystemResources() {
    // This would typically integrate with system monitoring tools
    // For now, we'll return mock data
    return {
        timestamp: Date.now(),
        cpu: Math.random() * 100,
        memory: Math.random() * 100,
        disk: Math.random() * 100,
        network: Math.random() * 100
    };
}
