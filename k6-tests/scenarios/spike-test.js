/**
 * K6 Spike Test for OpenSearch API
 * Tests system behavior under sudden load spikes
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import { getRandomSearchTerm } from '../data/search-terms.js';
import { config, API_CONFIG } from '../config/k6-config.js';

// Custom metrics for spike testing
const errorRate = new Rate('error_rate');
const responseTime = new Trend('response_time');
const requestCount = new Counter('request_count');
const spikeErrors = new Counter('spike_errors');

/**
 * Spike test function
 */
export default function() {
    const searchTerm = getRandomSearchTerm();
    
    const url = `${config.baseUrl}${API_CONFIG.endpoints.search}`;
    const headers = {
        ...API_CONFIG.headers,
        'Authorization': `Bearer ${config.apiKey}`
    };
    
    const payload = {
        query: searchTerm,
        schemas: API_CONFIG.schemas,
        limit: API_CONFIG.defaultLimit,
        search_types: API_CONFIG.searchTypes
    };
    
    const startTime = Date.now();
    const response = http.post(url, JSON.stringify(payload), { headers });
    const endTime = Date.now();
    const duration = endTime - startTime;
    
    // Increment request counter
    requestCount.add(1);
    
    // Spike test specific checks
    const checksResult = check(response, {
        'status is 200': (r) => r.status === 200,
        'response time < 5s': (r) => r.timings.duration < 5000,
        'response time < 10s': (r) => r.timings.duration < 10000,
        'no timeout errors': (r) => r.status !== 408,
        'no server overload': (r) => r.status !== 503,
        'no rate limiting': (r) => r.status !== 429,
        'response is valid': (r) => r.body && r.body.length > 0
    });
    
    // Update metrics
    errorRate.add(!checksResult);
    responseTime.add(duration);
    
    if (!checksResult) {
        spikeErrors.add(1);
    }
    
    // Log spike test data
    const currentTime = new Date().toISOString();
    console.log(`[${currentTime}] Spike Test | Status: ${response.status} | Time: ${duration}ms | Query: "${searchTerm}"`);
    
    // Very short sleep for spike testing
    sleep(Math.random() * 0.2 + 0.05); // 0.05-0.25 seconds
}

/**
 * Setup for spike test
 */
export function setup() {
    console.log('⚡ Starting OpenSearch API Spike Test');
    console.log(`📊 Target: ${config.baseUrl}`);
    console.log('⚠️  This test simulates sudden traffic spikes');
    console.log('📈 Load pattern: Low → High → Low');
    
    return {};
}

/**
 * Teardown for spike test
 */
export function teardown(data) {
    console.log('🏁 Spike Test Completed');
    console.log('📊 Analyze how system recovers from traffic spikes');
}
