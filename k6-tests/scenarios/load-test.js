/**
 * K6 Load Test for OpenSearch API
 * Simulates normal production load with realistic user behavior
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import { getRandomSearchTerm } from '../data/search-terms.js';
import { config, API_CONFIG } from '../config/k6-config.js';

// Custom metrics
const errorRate = new Rate('error_rate');
const searchLatency = new Trend('search_latency');
const responseSize = new Trend('response_size');

/**
 * Main test function - executed by each VU
 */
export default function() {
    // Get search term from Excel file
    const searchTerm = getRandomSearchTerm();
    
    // Prepare API request
    const url = `${config.baseUrl}${API_CONFIG.endpoints.search}`;
    const headers = {
        ...API_CONFIG.headers,
        'Authorization': `Bearer ${config.apiKey}`
    };
    
    const payload = {
        query: searchTerm,
        schemas: API_CONFIG.schemas,
        limit: Math.floor(Math.random() * 50) + 10, // Random limit between 10-60
        search_types: API_CONFIG.searchTypes
    };
    
    // Make API request
    const response = http.post(url, JSON.stringify(payload), { headers });
    
    // Performance checks
    const checksResult = check(response, {
        'status is 200': (r) => r.status === 200,
        'response time < 3s': (r) => r.timings.duration < 3000,
        'response has body': (r) => r.body && r.body.length > 0,
        'response is JSON': (r) => {
            try {
                JSON.parse(r.body);
                return true;
            } catch (e) {
                return false;
            }
        },
        'response has results': (r) => {
            try {
                const data = JSON.parse(r.body);
                return data && (data.results || data.data || data.hits);
            } catch (e) {
                return false;
            }
        }
    });
    
    // Update custom metrics
    errorRate.add(response.status !== 200);
    searchLatency.add(response.timings.duration);
    responseSize.add(response.body.length);
    
    // Log performance data (only for errors or slow requests)
    if (response.status !== 200 || response.timings.duration > 2000) {
        console.log(`⚠️  Slow/Error: "${searchTerm.fullName || searchTerm.name}" | Status: ${response.status} | Time: ${response.timings.duration}ms`);
    }
    
    // Realistic think time (1-5 seconds)
    sleep(Math.random() * 4 + 1);
}

/**
 * Setup function - runs once before all VUs
 */
export function setup() {
    console.log('🚀 Starting OpenSearch API Load Test');
    console.log(`📊 Environment: ${config.baseUrl}`);
    console.log(`👥 VUs: ${__ENV.VUS || 20}`);
    console.log(`⏱️  Duration: ${__ENV.DURATION || '5m'}`);
    
    return { startTime: Date.now() };
}

/**
 * Teardown function - runs once after all VUs
 */
export function teardown(data) {
    const duration = (Date.now() - data.startTime) / 1000;
    console.log('🏁 Load Test Completed');
    console.log(`⏱️  Total Duration: ${duration.toFixed(2)}s`);
}
