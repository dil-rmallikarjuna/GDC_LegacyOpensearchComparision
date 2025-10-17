/**
 * K6 Example Test for OpenSearch API
 * Simple example demonstrating the framework usage
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import { getRandomSearchTerm } from '../data/search-terms.js';
import { config, API_CONFIG } from '../config/k6-config.js';

// Custom metrics
const errorRate = new Rate('error_rate');
const searchLatency = new Trend('search_latency');

/**
 * Main test function - executed by each VU
 */
export default function() {
    // Get a search term from Excel file
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
        limit: API_CONFIG.defaultLimit,
        search_types: API_CONFIG.searchTypes
    };
    
    // Make API request
    const response = http.post(url, JSON.stringify(payload), { headers });
    
    // Performance checks
    const checksResult = check(response, {
        'status is 200': (r) => r.status === 200,
        'response time < 5s': (r) => r.timings.duration < 5000,
        'response has body': (r) => r.body && r.body.length > 0,
        'response is JSON': (r) => {
            try {
                JSON.parse(r.body);
                return true;
            } catch (e) {
                return false;
            }
        }
    });
    
    // Update custom metrics
    errorRate.add(response.status !== 200);
    searchLatency.add(response.timings.duration);
    
    // Log the request
    console.log(`Search: "${searchTerm}" | Status: ${response.status} | Time: ${response.timings.duration}ms`);
    
    // Think time between requests
    sleep(1);
}

/**
 * Setup function - runs once before all VUs
 */
export function setup() {
    console.log('🚀 Starting Example OpenSearch API Test');
    console.log(`📊 Environment: ${config.baseUrl}`);
    console.log(`👥 VUs: ${__ENV.VUS || 5}`);
    console.log(`⏱️  Duration: ${__ENV.DURATION || '1m'}`);
    
    return { startTime: Date.now() };
}

/**
 * Teardown function - runs once after all VUs
 */
export function teardown(data) {
    const duration = (Date.now() - data.startTime) / 1000;
    console.log('🏁 Example Test Completed');
    console.log(`⏱️  Total Duration: ${duration.toFixed(2)}s`);
}
