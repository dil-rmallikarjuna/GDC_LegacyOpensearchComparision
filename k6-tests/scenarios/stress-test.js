/**
 * K6 Stress Test for OpenSearch API
 * Gradually increases load to find breaking point
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import { getRandomSearchTerm } from '../data/search-terms.js';
import { config, API_CONFIG } from '../config/k6-config.js';

// Custom metrics for stress testing
const errorRate = new Rate('error_rate');
const responseTime = new Trend('response_time');
const throughput = new Rate('throughput');

/**
 * Stress test function with gradual load increase
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
    
    // Stress test specific checks
    const checksResult = check(response, {
        'status is 200': (r) => r.status === 200,
        'response time < 10s': (r) => r.timings.duration < 10000,
        'response time < 30s': (r) => r.timings.duration < 30000,
        'no server errors': (r) => r.status < 500,
        'response has content': (r) => r.body && r.body.length > 0,
        'valid JSON response': (r) => {
            try {
                const data = JSON.parse(r.body);
                return data !== null;
            } catch (e) {
                return false;
            }
        }
    });
    
    // Update metrics
    errorRate.add(!checksResult);
    responseTime.add(duration);
    throughput.add(checksResult);
    
    // Log stress test data
    if (response.status !== 200) {
        console.log(`❌ Error: ${response.status} | Query: "${searchTerm}" | Time: ${duration}ms`);
    } else {
        console.log(`✅ Success: ${response.status} | Query: "${searchTerm}" | Time: ${duration}ms`);
    }
    
    // Shorter sleep for stress testing
    sleep(Math.random() * 0.5 + 0.1); // 0.1-0.6 seconds
}

/**
 * Setup for stress test
 */
export function setup() {
    console.log('🔥 Starting OpenSearch API Stress Test');
    console.log(`📊 Target: ${config.baseUrl}`);
    console.log('⚠️  This test will gradually increase load to find breaking point');
    
    return {};
}

/**
 * Teardown for stress test
 */
export function teardown(data) {
    console.log('🏁 Stress Test Completed');
    console.log('📊 Check results for performance degradation patterns');
}
