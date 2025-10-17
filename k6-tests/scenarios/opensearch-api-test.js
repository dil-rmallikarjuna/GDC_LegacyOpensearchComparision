/**
 * K6 Performance Test for OpenSearch API
 * Tests the /search endpoint with various load patterns
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';
import { getRandomSearchTerm, getTotalSearchTerms } from '../data/search-terms.js';
import { config, API_CONFIG } from '../config/k6-config.js';

// Custom metrics
const errorRate = new Rate('error_rate');
const searchLatency = new Rate('search_latency_ok');

// Test data setup - using search terms from Excel file
let currentTermIndex = 0;

/**
 * Main test function - executed by each VU
 */
export default function() {
    // Get next search term from Excel file (round-robin)
    const searchTerm = getRandomSearchTerm();
    currentTermIndex++;
    
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
    const startTime = Date.now();
    const response = http.post(url, JSON.stringify(payload), { headers });
    const endTime = Date.now();
    const responseTime = endTime - startTime;
    
    // Performance checks
    const checksResult = check(response, {
        'status is 200': (r) => r.status === 200,
        'response time < 2s': (r) => r.timings.duration < 2000,
        'response time < 5s': (r) => r.timings.duration < 5000,
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
    searchLatency.add(responseTime < 2000);
    
    // Log performance data
    console.log(`Search: "${searchTerm}" | Status: ${response.status} | Time: ${responseTime}ms`);
    
    // Add some realistic think time
    sleep(Math.random() * 2 + 1); // 1-3 seconds
}

/**
 * Setup function - runs once before all VUs
 */
export function setup() {
    console.log('🚀 Starting OpenSearch API Performance Test');
    console.log(`📊 Environment: ${config.baseUrl}`);
    console.log(`👥 VUs: ${__ENV.VUS || 10}`);
    console.log(`⏱️  Duration: ${__ENV.DURATION || '1m'}`);
    console.log(`🔍 Search Terms: ${getTotalSearchTerms()} from Excel file`);
    
    // Test API connectivity
    const healthUrl = `${config.baseUrl}${API_CONFIG.endpoints.health}`;
    const healthResponse = http.get(healthUrl, {
        headers: { 'x-api-key': config.apiKey }
    });
    
    if (healthResponse.status !== 200) {
        console.warn('⚠️  Health check failed, but continuing with test');
    } else {
        console.log('✅ API health check passed');
    }
    
    return { searchTerms: getTotalSearchTerms() };
}

/**
 * Teardown function - runs once after all VUs
 */
export function teardown(data) {
    console.log('🏁 OpenSearch API Performance Test Completed');
    console.log(`📈 Total search terms used: ${data.searchTerms}`);
}
